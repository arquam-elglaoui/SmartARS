# -*- coding: utf-8 -*-
"""
SmartARS - Robot de Veille Réglementaire
========================================
Analyse les RAA (Recueils des Actes Administratifs) pour trouver 
les autorisations d'équipements d'imagerie médicale.

Usage:
    python main.py                          # Mode interactif
    python main.py novembre 2025            # Toutes régions
    python main.py 11 2025                  # Avec numéro de mois
    python main.py novembre 2025 bretagne   # Région spécifique
"""

import sys
import os
import io
import datetime
import logging
import hashlib
import json
import pandas as pd
import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import KEYWORDS, MOIS_FR
from utils import log, telecharger_page, analyser_pdf_pages, normaliser_mois, MOIS_NOMS
from regions import EXTRACTEURS

# === CONFIGURATION DES DOSSIERS ===
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SmartARS")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CACHE_FILE = os.path.join(BASE_DIR, ".cache.json")
HISTORIQUE_EXCEL = os.path.join(BASE_DIR, "SmartARS_Historique.xlsx")


def setup_logging(log_dir):
    """Configure le logging dans un fichier et la console."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "smartars.log")
    
    logger = logging.getLogger("SmartARS")
    logger.setLevel(logging.INFO)
    
    # Éviter les handlers dupliqués
    if logger.handlers:
        logger.handlers.clear()
    
    # Handler fichier
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)
    
    # Handler console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def get_output_dir(annee, mois_num, region=None):
    """
    Retourne le dossier de sortie.
    Structure: ~/Documents/SmartARS/results/{annee}_{mois}/{region}/
    """
    mois_nom = MOIS_NOMS.get(mois_num, str(mois_num).zfill(2))
    
    if region:
        path = os.path.join(RESULTS_DIR, f"{annee}_{mois_nom}", region)
    else:
        path = os.path.join(RESULTS_DIR, f"{annee}_{mois_nom}")
    
    os.makedirs(path, exist_ok=True)
    return path


# === GESTION DU CACHE (Anti-doublons) ===

def load_cache():
    """Charge le cache des URLs déjà traitées."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"processed_urls": {}}


def save_cache(cache):
    """Sauvegarde le cache."""
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def get_url_hash(url):
    """Génère un hash unique pour une URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def is_already_processed(cache, url, mois_num, annee):
    """Vérifie si une URL a déjà été traitée pour ce mois/année."""
    key = f"{annee}_{mois_num}"
    url_hash = get_url_hash(url)
    return key in cache.get("processed_urls", {}) and url_hash in cache["processed_urls"].get(key, [])


def mark_as_processed(cache, url, mois_num, annee):
    """Marque une URL comme traitée."""
    key = f"{annee}_{mois_num}"
    url_hash = get_url_hash(url)
    
    if "processed_urls" not in cache:
        cache["processed_urls"] = {}
    if key not in cache["processed_urls"]:
        cache["processed_urls"][key] = []
    
    if url_hash not in cache["processed_urls"][key]:
        cache["processed_urls"][key].append(url_hash)


# === EXCEL HISTORIQUE UNIQUE ===

def maj_historique_excel(resultats, mois_num, annee):
    """
    Met à jour le fichier Excel historique unique.
    - Crée une feuille par mois/année (ex: "2025_novembre")
    - Ajoute les nouveaux résultats sans doublons
    
    Args:
        resultats: Liste des nouvelles autorisations trouvées
        mois_num: Numéro du mois
        annee: Année
    """
    if not resultats:
        return 0
    
    mois_nom = MOIS_NOMS.get(mois_num, str(mois_num).zfill(2))
    sheet_name = f"{annee}_{mois_nom}"
    
    # Créer le dossier si nécessaire
    os.makedirs(BASE_DIR, exist_ok=True)
    
    # Nouveau DataFrame avec les résultats
    df_new = pd.DataFrame(resultats)
    
    # Créer une clé unique pour chaque ligne (éviter doublons)
    df_new["_cle_unique"] = df_new.apply(
        lambda r: f"{r['Region']}|{r['Source']}|{r['Page']}|{r['Equipements']}", 
        axis=1
    )
    
    nb_ajoutes = 0
    
    try:
        if os.path.exists(HISTORIQUE_EXCEL):
            # Fichier existe → charger toutes les feuilles
            with pd.ExcelFile(HISTORIQUE_EXCEL) as xls:
                existing_sheets = xls.sheet_names
            
            if sheet_name in existing_sheets:
                # La feuille existe → charger et fusionner
                df_existing = pd.read_excel(HISTORIQUE_EXCEL, sheet_name=sheet_name)
                
                # Ajouter la clé unique aux données existantes
                if "_cle_unique" not in df_existing.columns:
                    df_existing["_cle_unique"] = df_existing.apply(
                        lambda r: f"{r.get('Region', '')}|{r.get('Source', '')}|{r.get('Page', '')}|{r.get('Equipements', '')}", 
                        axis=1
                    )
                
                # Filtrer les doublons
                cles_existantes = set(df_existing["_cle_unique"].tolist())
                df_nouvelles = df_new[~df_new["_cle_unique"].isin(cles_existantes)]
                
                nb_ajoutes = len(df_nouvelles)
                
                if nb_ajoutes > 0:
                    # Combiner les données
                    df_final = pd.concat([df_existing, df_nouvelles], ignore_index=True)
                else:
                    df_final = df_existing
            else:
                # Nouvelle feuille
                df_final = df_new
                nb_ajoutes = len(df_new)
            
            # Charger toutes les feuilles existantes
            all_sheets = {}
            with pd.ExcelFile(HISTORIQUE_EXCEL) as xls:
                for sheet in xls.sheet_names:
                    if sheet != sheet_name:
                        all_sheets[sheet] = pd.read_excel(xls, sheet_name=sheet)
            
            # Ajouter/Mettre à jour la feuille courante
            all_sheets[sheet_name] = df_final
            
            # Réécrire le fichier avec toutes les feuilles
            with pd.ExcelWriter(HISTORIQUE_EXCEL, engine='openpyxl') as writer:
                for sname, sdf in sorted(all_sheets.items(), reverse=True):
                    # Supprimer la colonne clé unique pour l'export
                    if "_cle_unique" in sdf.columns:
                        sdf = sdf.drop(columns=["_cle_unique"])
                    sdf.to_excel(writer, sheet_name=sname, index=False)
        
        else:
            # Nouveau fichier
            df_final = df_new.drop(columns=["_cle_unique"])
            nb_ajoutes = len(df_final)
            
            with pd.ExcelWriter(HISTORIQUE_EXCEL, engine='openpyxl') as writer:
                df_final.to_excel(writer, sheet_name=sheet_name, index=False)
    
    except Exception as e:
        logging.getLogger("SmartARS").error(f"Erreur maj historique Excel: {e}")
        return 0
    
    return nb_ajoutes


# === CRÉATION DU PDF PAR RAA ===

def detecter_fin_sommaire(pdf_bytes, max_pages=10):
    """
    Essaie de détecter où se termine le sommaire dans un PDF.
    Retourne le numéro de la dernière page du sommaire (0-indexed).
    Par défaut retourne 2 (pages 0, 1, 2 = 3 premières pages).
    """
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num in range(min(max_pages, len(doc))):
                text = doc[page_num].get_text().lower()
                
                # Patterns qui indiquent la FIN du sommaire
                # (début du contenu réel)
                patterns_fin_sommaire = [
                    "vu le code",
                    "le préfet",
                    "le directeur",
                    "arrête",
                    "article 1",
                    "décide",
                ]
                
                for pattern in patterns_fin_sommaire:
                    if pattern in text and page_num > 0:
                        # On retourne la page précédente comme fin du sommaire
                        return max(0, page_num - 1)
            
            # Par défaut: 3 premières pages (indices 0, 1, 2)
            return min(2, len(doc) - 1)
    except:
        return 2


def creer_pdf_par_raa(pdf_bytes, pages_pertinentes, output_dir, nom_fichier_original):
    """
    Crée un PDF extrait d'un RAA avec:
    - Pages 1-3 (ou jusqu'à la fin du sommaire) du RAA original
    - Pages pertinentes contenant les autorisations
    
    Args:
        pdf_bytes: Contenu binaire du PDF source
        pages_pertinentes: Liste des numéros de pages avec autorisations (0-indexed)
        output_dir: Dossier de sortie
        nom_fichier_original: Nom du fichier RAA original
    
    Returns:
        Chemin du fichier créé ou None
    """
    if not pages_pertinentes:
        return None
    
    try:
        # Ouvrir le PDF source
        src = fitz.open(stream=pdf_bytes, filetype="pdf")
        doc = fitz.open()  # Nouveau PDF
        
        # Détecter la fin du sommaire
        fin_sommaire = detecter_fin_sommaire(pdf_bytes)
        
        # 1. Ajouter les pages de garde/sommaire (pages 0 à fin_sommaire)
        pages_header = list(range(0, fin_sommaire + 1))
        
        # 2. Collecter toutes les pages à inclure (sans doublons, triées)
        toutes_pages = set(pages_header)
        for p in pages_pertinentes:
            if p not in toutes_pages:  # Éviter les doublons
                toutes_pages.add(p)
        
        toutes_pages = sorted(toutes_pages)
        
        # 3. Insérer les pages dans le nouveau PDF
        for page_num in toutes_pages:
            if page_num < len(src):
                doc.insert_pdf(src, from_page=page_num, to_page=page_num)
        
        src.close()
        
        # 4. Sauvegarder avec le nom original (nettoyé)
        # Nettoyer le nom de fichier
        nom_clean = nom_fichier_original
        # Retirer l'extension .pdf si présente
        if nom_clean.lower().endswith('.pdf'):
            nom_clean = nom_clean[:-4]
        # Décoder les caractères URL (%20, etc.)
        try:
            from urllib.parse import unquote
            nom_clean = unquote(nom_clean)
        except:
            pass
        # Remplacer les caractères problématiques
        nom_clean = nom_clean.replace('+', '_').replace('%', '_')
        
        filename = f"{nom_clean}_EXTRACT.pdf"
        filepath = os.path.join(output_dir, filename)
        
        doc.save(filepath)
        doc.close()
        
        return filepath
        
    except Exception as e:
        logging.getLogger("SmartARS").error(f"Erreur creation PDF: {e}")
        return None


# === ANALYSE D'UNE RÉGION ===

def analyser_region(nom_region, extracteur, mois_num, annee, output_dir, logger, cache, skip_cache=False):
    """
    Analyse une région et génère les fichiers de sortie.
    
    Crée UN PDF PAR RAA contenant:
    - Pages 1-3 du RAA (page de garde + sommaire original)
    - Pages pertinentes avec les autorisations
    
    Returns:
        Tuple (resultats_excel, nb_pages, nb_pdfs, nb_skipped)
    """
    resultats = []
    nb_pages_total = 0
    pdfs_crees = 0
    nb_skipped = 0
    
    logger.info(f"Debut analyse: {nom_region}")
    log(f"══ {nom_region.upper().replace('-', ' ')} ══", "REGION")
    
    try:
        # 1. Récupérer les liens PDF du mois
        pdf_urls = extracteur(mois_num, annee)
        
        if not pdf_urls:
            logger.warning(f"{nom_region}: Aucun PDF trouve")
            log(f"  Aucun PDF trouve pour ce mois", "WARNING")
            return resultats, 0, 0, 0
        
        logger.info(f"{nom_region}: {len(pdf_urls)} PDF a analyser")
        log(f"  {len(pdf_urls)} PDF trouve(s)", "INFO")
        
        # 2. Analyser chaque PDF
        for pdf_url in pdf_urls:
            # Vérifier le cache (anti-doublons)
            if not skip_cache and is_already_processed(cache, pdf_url, mois_num, annee):
                nb_skipped += 1
                continue
            
            nom_fichier = pdf_url.split('/')[-1]
            log(f"  Analyse: {nom_fichier[:50]}...", "DOWNLOAD")
            
            response = telecharger_page(pdf_url, is_pdf=True)
            if not response:
                logger.error(f"Echec telechargement: {pdf_url}")
                continue
            
            # Marquer comme traité
            mark_as_processed(cache, pdf_url, mois_num, annee)
            
            # 3. Trouver les pages avec autorisations
            pages = analyser_pdf_pages(io.BytesIO(response.content))
            
            # Collecter les pages pertinentes pour CE PDF
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
            
            # 4. Créer un PDF extrait pour CE RAA (si pages pertinentes trouvées)
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
        
        # 5. Sauvegarder le cache
        save_cache(cache)
        
        # Résumé de la région
        if nb_pages_total > 0:
            log(f"  Resume: {nb_pages_total} page(s) dans {pdfs_crees} PDF(s) cree(s)", "SUCCESS")
        
        if nb_skipped > 0:
            log(f"  ({nb_skipped} PDF deja traite(s), ignore(s))", "INFO")
        
        logger.info(f"{nom_region}: {nb_pages_total} page(s) pertinente(s), {pdfs_crees} PDF(s) cree(s)")
        
    except Exception as e:
        logger.error(f"{nom_region}: Erreur - {e}")
        log(f"Erreur {nom_region}: {e}", "ERROR")
    
    return resultats, nb_pages_total, pdfs_crees, nb_skipped


# === MENU INTERACTIF ===

def afficher_menu():
    """Affiche un menu interactif pour faciliter l'utilisation."""
    print()
    print("=" * 60)
    print("   SmartARS - Robot de Veille Reglementaire")
    print("   Autorisations d'Equipements d'Imagerie Medicale")
    print("=" * 60)
    print()
    
    # Mois
    print("Mois disponibles:")
    mois_list = list(MOIS_FR.keys())[:12]  # Uniquement les noms uniques
    for i, m in enumerate(["janvier", "fevrier", "mars", "avril", "mai", "juin", 
                           "juillet", "aout", "septembre", "octobre", "novembre", "decembre"], 1):
        print(f"  {i:2}. {m.capitalize()}")
    print()
    
    mois_input = input("Entrez le mois (nom ou numero): ").strip()
    if not mois_input:
        print("Annule.")
        return None, None, None
    
    # Année
    annee_defaut = datetime.datetime.now().year
    annee_input = input(f"Entrez l'annee [{annee_defaut}]: ").strip()
    if not annee_input:
        annee_input = str(annee_defaut)
    
    # Régions
    print()
    print("Regions disponibles:")
    regions_list = sorted(EXTRACTEURS.keys())
    for i, r in enumerate(regions_list, 1):
        print(f"  {i:2}. {r}")
    print(f"  0. TOUTES les regions")
    print()
    
    regions_input = input("Entrez les numeros des regions (ex: 1,3,5) ou 0 pour toutes: ").strip()
    
    if regions_input == "0" or not regions_input:
        regions = None  # Toutes
    else:
        try:
            indices = [int(x.strip()) - 1 for x in regions_input.split(",")]
            regions = [regions_list[i] for i in indices if 0 <= i < len(regions_list)]
        except:
            regions = None
    
    return mois_input, annee_input, regions


# === FONCTION PRINCIPALE ===

def run_bot(mois, annee, regions=None, skip_cache=False):
    """Lance le robot."""
    
    mois_nom, mois_num = normaliser_mois(mois)
    annee = int(annee)
    
    # Créer les dossiers
    output_base = get_output_dir(annee, mois_num)
    os.makedirs(BASE_DIR, exist_ok=True)
    
    # Setup logging
    logger = setup_logging(output_base)
    
    # Charger le cache
    cache = load_cache()
    
    print()
    log(f"SmartARS - {mois_nom.capitalize()} {annee}", "START")
    log(f"Mots-cles: {len(KEYWORDS)} configures", "INFO")
    log(f"Dossier de sortie: {output_base}", "INFO")
    print("-" * 50)
    
    logger.info(f"=== Demarrage SmartARS - {mois_nom} {annee} ===")
    logger.info(f"Mots-cles: {KEYWORDS}")
    
    # Régions à traiter
    if regions:
        extracteurs = {k: v for k, v in EXTRACTEURS.items() if k in regions}
    else:
        extracteurs = EXTRACTEURS
    
    log(f"{len(extracteurs)} region(s) a analyser", "INFO")
    logger.info(f"Regions: {list(extracteurs.keys())}")
    
    tous_resultats = []
    stats = {"total_pages": 0, "total_pdfs": 0, "par_region": {}, "skipped": 0, "erreurs": []}
    
    for nom, extracteur in extracteurs.items():
        print()
        
        # Créer le dossier de sortie pour cette région
        output_dir = get_output_dir(annee, mois_num, nom)
        
        resultats, nb_pages, nb_pdfs, nb_skipped = analyser_region(
            nom, extracteur, mois_num, annee, output_dir, logger, cache, skip_cache
        )
        
        tous_resultats.extend(resultats)
        stats["total_pages"] += nb_pages
        stats["total_pdfs"] += nb_pdfs
        stats["par_region"][nom] = {"pages": nb_pages, "pdfs": nb_pdfs}
        stats["skipped"] += nb_skipped
    
    # Mettre à jour l'Excel historique unique (UN SEUL fichier pour tout)
    nb_ajoutes = maj_historique_excel(tous_resultats, mois_num, annee)
    if nb_ajoutes > 0:
        logger.info(f"Historique Excel: {nb_ajoutes} nouvelle(s) ligne(s) ajoutee(s)")
        log(f"Historique: {nb_ajoutes} nouvelle(s) page(s) ajoutee(s)", "SUCCESS")
    elif tous_resultats:
        log(f"Historique: toutes les pages etaient deja presentes", "INFO")
    
    # Résumé final
    print()
    print("=" * 60)
    print("   RÉSUMÉ")
    print("=" * 60)
    
    if tous_resultats:
        log(f"TERMINE ! {stats['total_pages']} page(s) pertinente(s) dans {stats['total_pdfs']} PDF(s)", "SUCCESS")
        
        # Résumé par région (seulement celles avec résultats)
        regions_avec_resultats = [(r, d) for r, d in stats["par_region"].items() if d["pages"] > 0]
        if regions_avec_resultats:
            print()
            print("Par region:")
            for region, data in sorted(regions_avec_resultats, key=lambda x: -x[1]["pages"]):
                print(f"   ✓ {region}: {data['pages']} page(s) dans {data['pdfs']} PDF(s)")
        
        # Régions sans résultat
        regions_vides = [r for r, d in stats["par_region"].items() if d["pages"] == 0]
        if regions_vides and len(regions_vides) < len(stats["par_region"]):
            print()
            print(f"Sans resultat: {', '.join(regions_vides)}")
        
        logger.info(f"=== Termine: {stats['total_pages']} pages dans {stats['total_pdfs']} PDFs ===")
        logger.info(f"Detail: {stats['par_region']}")
        
    else:
        log("Aucune autorisation trouvee pour ce mois", "WARNING")
        logger.warning("Aucune autorisation trouvee")
    
    if stats["skipped"] > 0:
        print()
        log(f"{stats['skipped']} PDF(s) ignore(s) (deja traites)", "INFO")
    
    # Fichiers de sortie
    print()
    print("-" * 60)
    print("FICHIERS:")
    print(f"   PDFs extraits: {output_base}")
    print(f"   Excel unique:  {HISTORIQUE_EXCEL}")
    print(f"   Logs:          {os.path.join(output_base, 'smartars.log')}")
    print("-" * 60)
    log("Termine", "END")


def main():
    args = sys.argv[1:]
    
    # Mode interactif si pas d'arguments
    if len(args) == 0:
        mois, annee, regions = afficher_menu()
        if mois and annee:
            run_bot(mois, annee, regions)
        return
    
    # Mode ligne de commande
    if len(args) < 2:
        print("Usage: python main.py <mois> <annee> [regions...]")
        print()
        print("Exemples:")
        print("  python main.py                    # Mode interactif")
        print("  python main.py novembre 2025      # Toutes regions")
        print("  python main.py 11 2025 bretagne   # Region specifique")
        print()
        print("Options:")
        print("  --force    Ignorer le cache et re-analyser tout")
        print()
        print("Regions disponibles:")
        for r in sorted(EXTRACTEURS.keys()):
            print(f"  - {r}")
        print()
        print(f"Sortie: ~/Documents/SmartARS/results/{{annee}}_{{mois}}/{{region}}/")
        return
    
    mois = args[0]
    annee = args[1]
    
    # Options
    skip_cache = "--force" in args
    
    # Régions (exclure les options)
    regions = [a for a in args[2:] if not a.startswith("--")]
    if not regions:
        regions = None
    
    run_bot(mois, annee, regions, skip_cache)


if __name__ == "__main__":
    main()
