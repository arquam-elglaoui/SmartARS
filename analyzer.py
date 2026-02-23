# -*- coding: utf-8 -*-
"""
SmartARS - Analyse des régions
================================
Orchestre l'analyse des RAA pour chaque région :
1. Récupère les liens PDF via l'extracteur de la région
2. Télécharge et analyse chaque PDF
3. Crée les PDFs extraits
4. Sauvegarde les logs détaillés par région
"""

import datetime
import io
import os

from cache import is_already_processed, mark_as_processed, save_cache
from pdf_extractor import creer_pdf_par_raa
from utils import MOIS_NOMS, analyser_pdf_pages, log, telecharger_page

# Abréviations des régions pour les noms de fichiers log
ABREVIATIONS_REGIONS = {
    "auvergne-rhone-alpes": "aura",
    "bourgogne-franche-comte": "bfc",
    "bretagne": "bzh",
    "centre-val-de-loire": "cvl",
    "corse": "cors",
    "grand-est": "gest",
    "guadeloupe": "guad",
    "guyane": "guy",
    "hauts-de-france": "hdf",
    "ile-de-france": "idf",
    "martinique": "mart",
    "normandie": "norm",
    "nouvelle-aquitaine": "naq",
    "occitanie": "occ",
    "pays-de-la-loire": "pdl",
    "paca": "paca",
    "reunion": "reu",
}


def analyser_region(nom_region, extracteur, mois_num, annee, output_dir, logger, cache, skip_cache=False, should_stop=None):
    """
    Analyse une région : scrape les PDFs, cherche les autorisations,
    crée les extraits PDF et les logs.

    Retourne (resultats_excel, nb_pdfs_trouves, nb_pages, nb_pdfs_crees, nb_skipped).
    """
    resultats = []
    nb_pages_total = 0
    pdfs_crees = 0
    nb_skipped = 0
    nb_pdfs_trouves = 0

    log_region = _initialiser_log_region(nom_region, mois_num, annee)

    logger.info(f"Debut analyse: {nom_region}")
    log(f"══ {nom_region.upper().replace('-', ' ')} ══", "REGION")

    try:
        pdf_urls = extracteur(mois_num, annee)
        nb_pdfs_trouves = len(pdf_urls) if pdf_urls else 0

        if not pdf_urls:
            logger.warning(f"{nom_region}: Aucun PDF trouve")
            log(f"  0 PDF trouve — extracteur n'a rien retourne", "WARNING")
            log_region.append("RESULTAT: Aucun PDF trouve (0 URL retournee par l'extracteur)")
            sauvegarder_log_region(output_dir, nom_region, mois_num, annee, log_region)
            return resultats, 0, 0, 0, 0

        logger.info(f"{nom_region}: {nb_pdfs_trouves} PDF trouve(s)")
        log(f"  {nb_pdfs_trouves} PDF trouve(s) sur le site", "SEARCH")

        log_region.append(f"PDFs TROUVES ({nb_pdfs_trouves}):")
        for i, url in enumerate(pdf_urls, 1):
            nom = url.split('/')[-1][:80]
            log_region.append(f"  {i}. {nom}")

        resultats, nb_pages_total, pdfs_crees, nb_skipped = _analyser_pdfs(
            pdf_urls, nom_region, mois_num, annee,
            output_dir, logger, cache, skip_cache, should_stop
        )

        save_cache(cache)
        _log_resume_region(nom_region, nb_pdfs_trouves, nb_pages_total, pdfs_crees, nb_skipped, logger)
        _completer_log_region(log_region, pdf_urls, nb_skipped, nb_pages_total, pdfs_crees, resultats)
        sauvegarder_log_region(output_dir, nom_region, mois_num, annee, log_region)

    except Exception as e:
        logger.error(f"{nom_region}: Erreur - {e}")
        log(f"Erreur {nom_region}: {e}", "ERROR")
        log_region.append(f"ERREUR: {e}")
        sauvegarder_log_region(output_dir, nom_region, mois_num, annee, log_region)

    return resultats, nb_pdfs_trouves, nb_pages_total, pdfs_crees, nb_skipped


def _analyser_pdfs(pdf_urls, nom_region, mois_num, annee, output_dir, logger, cache, skip_cache, should_stop):
    """Boucle d'analyse sur chaque PDF d'une région."""
    resultats = []
    nb_pages_total = 0
    pdfs_crees = 0
    nb_skipped = 0
    nb_echecs = 0

    for pdf_url in pdf_urls:
        if should_stop and should_stop():
            logger.info(f"{nom_region}: Analyse arretee par l'utilisateur")
            log(f"  Analyse arretee", "WARNING")
            break

        if not skip_cache and is_already_processed(cache, pdf_url, mois_num, annee):
            nb_skipped += 1
            continue

        nom_fichier = pdf_url.split('/')[-1]
        log(f"  Analyse: {nom_fichier[:50]}...", "DOWNLOAD")

        response = telecharger_page(pdf_url, is_pdf=True)
        if not response:
            nb_echecs += 1
            logger.error(f"Echec telechargement: {pdf_url}")
            log(f"    ECHEC telechargement: {nom_fichier[:50]}", "ERROR")
            continue

        mark_as_processed(cache, pdf_url, mois_num, annee)

        pages = analyser_pdf_pages(io.BytesIO(response.content))

        pages_pertinentes = []
        for page in pages:
            if page["est_autorisation"]:
                log(f"    -> Page {page['page_num']+1}: {', '.join(page['equipements'])}", "FOUND")
                pages_pertinentes.append(page["page_num"])

                resultats.append({
                    "Region": nom_region,
                    "Source": nom_fichier[:60],
                    "Page": page["page_num"] + 1,
                    "Equipements": ", ".join(page["equipements"]),
                    "Etablissement": page.get("etablissement", ""),
                    "Code_Postal": page.get("ville", ""),
                    "URL": pdf_url,
                })

        if pages_pertinentes:
            nb_pages_total += len(pages_pertinentes)
            pdf_path = creer_pdf_par_raa(
                pdf_bytes=response.content,
                pages_pertinentes=pages_pertinentes,
                output_dir=output_dir,
                nom_fichier_original=nom_fichier
            )
            if pdf_path:
                pdfs_crees += 1
                logger.info(f"PDF cree: {os.path.basename(pdf_path)}")
                log(f"    PDF: {os.path.basename(pdf_path)}", "SUCCESS")

    if nb_echecs > 0:
        log(f"  /!\\ {nb_echecs} PDF(s) impossible(s) a telecharger", "WARNING")

    return resultats, nb_pages_total, pdfs_crees, nb_skipped


def _initialiser_log_region(nom_region, mois_num, annee):
    """Prépare les premières lignes du log de région."""
    return [
        f"=== {nom_region.upper()} - {mois_num:02d}/{annee} ===",
        f"Date analyse: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]


def _log_resume_region(nom_region, nb_trouves, nb_pages, nb_pdfs, nb_skipped, logger):
    """Affiche le résumé d'une région dans la console."""
    log(f"  -- {nom_region} : {nb_trouves} PDF trouves, {nb_pages} page(s) pertinente(s), {nb_pdfs} extrait(s) cree(s)", "INFO")
    if nb_skipped > 0:
        log(f"     ({nb_skipped} PDF deja traite(s), ignore(s))", "INFO")
    logger.info(f"{nom_region}: {nb_trouves} trouves, {nb_pages} pertinente(s), {nb_pdfs} extrait(s)")


def _completer_log_region(log_region, pdf_urls, nb_skipped, nb_pages, nb_pdfs, resultats):
    """Ajoute le résumé au log de région."""
    log_region.append("")
    log_region.append(f"PDFs ANALYSES: {len(pdf_urls) - nb_skipped}")
    log_region.append(f"PDFs IGNORES (cache): {nb_skipped}")
    log_region.append(f"PAGES PERTINENTES: {nb_pages}")
    log_region.append(f"PDFs EXTRAITS CREES: {nb_pdfs}")
    log_region.append("")
    if resultats:
        log_region.append("AUTORISATIONS TROUVEES:")
        for r in resultats:
            log_region.append(f"  - Page {r['Page']}: {r['Equipements']} ({r['Source']})")
    else:
        log_region.append("AUTORISATIONS TROUVEES: Aucune")


def sauvegarder_log_region(output_dir, nom_region, mois_num, annee, log_lines):
    """
    Sauvegarde le log détaillé d'une région dans un fichier texte.
    Mode append : chaque exécution ajoute une entrée datée.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        region_abrege = ABREVIATIONS_REGIONS.get(nom_region, nom_region[:4])
        mois_nom = MOIS_NOMS.get(mois_num, str(mois_num))

        log_filename = f"log_{region_abrege}_{mois_nom}_{annee}.txt"
        log_path = os.path.join(output_dir, log_filename)

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write('\n'.join(log_lines))
            f.write("\n")

    except Exception as e:
        print(f"Impossible de sauvegarder le log region: {e}")
