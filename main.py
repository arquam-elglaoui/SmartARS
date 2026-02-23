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

import datetime
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import analyser_region
from cache import load_cache
from config import KEYWORDS
from excel_export import HISTORIQUE_EXCEL, maj_historique_excel
from regions import EXTRACTEURS
from utils import MOIS_NOMS, log, normaliser_mois

BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SmartARS")
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def setup_logging(log_dir):
    """Configure le logging dans un fichier et la console."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "smartars.log")

    logger = logging.getLogger("SmartARS")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        logger.handlers.clear()

    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
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


# === PARSERS D'ENTRÉE ===

def parser_mois_multiples(mois_input):
    """
    Parse une entrée de mois séparés par virgules.
    Ex: "10,11" ou "octobre,novembre"
    """
    mois_list = []
    for m in mois_input.split(","):
        m = m.strip()
        if not m:
            continue
        _, mois_num = normaliser_mois(m)
        if mois_num and mois_num not in mois_list:
            mois_list.append(mois_num)
    return mois_list


def parser_annees_multiples(annee_input):
    """
    Parse une entrée d'années séparées par virgules.
    Ex: "2024,2025"
    """
    annees = []
    for a in annee_input.split(","):
        a = a.strip()
        if a.isdigit():
            annee = int(a)
            if 2000 <= annee <= 2100 and annee not in annees:
                annees.append(annee)
    return annees


# === MENU INTERACTIF ===

def afficher_menu():
    """Affiche un menu interactif pour la sélection mois/année/régions."""
    print()
    print("=" * 60)
    print("   SmartARS - Robot de Veille Reglementaire")
    print("   Autorisations d'Equipements d'Imagerie Medicale")
    print("=" * 60)
    print()

    mois_list = _demander_mois()
    if not mois_list:
        return None, None, None

    annees_list = _demander_annees()
    if not annees_list:
        return None, None, None

    regions = _demander_regions()

    mois_noms = [MOIS_NOMS.get(m, str(m)) for m in mois_list]
    print()
    print("-" * 40)
    print(f"  Mois:    {', '.join(mois_noms)}")
    print(f"  Annees:  {', '.join(map(str, annees_list))}")
    print(f"  Regions: {', '.join(regions) if regions else 'TOUTES'}")
    print("-" * 40)
    print()

    confirm = input("Lancer l'analyse ? (O/n): ").strip().lower()
    if confirm in ['n', 'non', 'no']:
        print("Annule.")
        return None, None, None

    return mois_list, annees_list, regions


def _demander_mois():
    """Sous-menu de sélection des mois."""
    print("Mois disponibles:")
    noms = [
        "janvier", "fevrier", "mars", "avril", "mai", "juin",
        "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
    ]
    for i, m in enumerate(noms, 1):
        print(f"  {i:2}. {m.capitalize()}")
    print()
    print("  Astuce: Plusieurs mois possibles avec virgule (ex: 10,11)")
    print()

    mois_input = input("Entrez le(s) mois (ex: 11 ou 10,11,12): ").strip()
    if not mois_input:
        print("Annule.")
        return None

    mois_list = parser_mois_multiples(mois_input)
    if not mois_list:
        print("Mois invalide.")
        return None
    return mois_list


def _demander_annees():
    """Sous-menu de sélection des années."""
    annee_defaut = datetime.datetime.now().year
    print()
    print(f"  Astuce: Plusieurs annees possibles avec virgule (ex: 2024,2025)")
    print()
    annee_input = input(f"Entrez l'annee(s) [{annee_defaut}]: ").strip()
    if not annee_input:
        annee_input = str(annee_defaut)

    annees_list = parser_annees_multiples(annee_input)
    if not annees_list:
        print("Annee invalide.")
        return None
    return annees_list


def _demander_regions():
    """Sous-menu de sélection des régions."""
    print()
    print("Regions disponibles:")
    regions_list = sorted(EXTRACTEURS.keys())
    for i, r in enumerate(regions_list, 1):
        print(f"  {i:2}. {r}")
    print(f"   0. TOUTES les regions")
    print()

    regions_input = input(
        "Entrez les numeros des regions (ex: 1,3,5) ou 0 pour toutes: "
    ).strip()

    if regions_input == "0" or not regions_input:
        return None

    try:
        indices = [int(x.strip()) - 1 for x in regions_input.split(",")]
        return [regions_list[i] for i in indices if 0 <= i < len(regions_list)]
    except (ValueError, IndexError):
        return None


# === FONCTION PRINCIPALE ===

def run_bot(mois, annee, regions=None, skip_cache=False, should_stop=None):
    """Lance le robot d'analyse pour un mois/année donné."""
    mois_nom, mois_num = normaliser_mois(mois)
    annee = int(annee)

    output_base = get_output_dir(annee, mois_num)
    os.makedirs(BASE_DIR, exist_ok=True)

    logger = setup_logging(output_base)
    cache = load_cache()

    print()
    log(f"SmartARS - {mois_nom.capitalize()} {annee}", "START")
    log(f"Mots-cles: {len(KEYWORDS)} configures", "INFO")
    log(f"Dossier de sortie: {output_base}", "INFO")
    print("-" * 50)

    logger.info(f"=== Demarrage SmartARS - {mois_nom} {annee} ===")
    logger.info(f"Mots-cles: {KEYWORDS}")

    if regions:
        extracteurs = {k: v for k, v in EXTRACTEURS.items() if k in regions}
    else:
        extracteurs = EXTRACTEURS

    log(f"{len(extracteurs)} region(s) a analyser", "INFO")
    logger.info(f"Regions: {list(extracteurs.keys())}")

    tous_resultats = []
    stats = {
        "total_pages": 0,
        "total_pdfs_crees": 0,
        "total_pdfs_trouves": 0,
        "par_region": {},
        "skipped": 0,
    }

    for nom, extracteur in extracteurs.items():
        if should_stop and should_stop():
            logger.info("Analyse arretee par l'utilisateur")
            log("Analyse arretee", "WARNING")
            break

        print()
        output_dir = get_output_dir(annee, mois_num, nom)

        resultats, nb_trouves, nb_pages, nb_pdfs, nb_skipped = analyser_region(
            nom, extracteur, mois_num, annee,
            output_dir, logger, cache, skip_cache, should_stop
        )

        tous_resultats.extend(resultats)
        stats["total_pages"] += nb_pages
        stats["total_pdfs_crees"] += nb_pdfs
        stats["total_pdfs_trouves"] += nb_trouves
        stats["par_region"][nom] = {
            "trouves": nb_trouves,
            "pages": nb_pages,
            "pdfs_crees": nb_pdfs,
        }
        stats["skipped"] += nb_skipped

    nb_ajoutes = maj_historique_excel(tous_resultats, mois_num, annee)
    if nb_ajoutes > 0:
        logger.info(f"Historique Excel: {nb_ajoutes} nouvelle(s) ligne(s) ajoutee(s)")
        log(f"Historique: {nb_ajoutes} nouvelle(s) page(s) ajoutee(s)", "SUCCESS")
    elif tous_resultats:
        log(f"Historique: toutes les pages etaient deja presentes", "INFO")

    _afficher_resume(tous_resultats, stats, output_base, logger, mois_num, annee)


def _afficher_resume(tous_resultats, stats, output_base, logger, mois_num, annee):
    """Affiche le résumé final avec tableau par région et alertes."""
    print()
    print("=" * 60)
    print("   RESUME")
    print("=" * 60)

    # Tableau par région
    print()
    print(f"  {'Region':<30} {'Trouves':>8} {'Pages':>8} {'Extraits':>9}")
    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*9}")

    for region in sorted(stats["par_region"].keys()):
        data = stats["par_region"][region]
        trouves = data["trouves"]
        pages = data["pages"]
        pdfs = data["pdfs_crees"]
        print(f"  {region:<30} {trouves:>8} {pages:>8} {pdfs:>9}")

    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*9}")
    print(
        f"  {'TOTAL':<30} "
        f"{stats['total_pdfs_trouves']:>8} "
        f"{stats['total_pages']:>8} "
        f"{stats['total_pdfs_crees']:>9}"
    )

    # La Réunion publie ses RAA en fin de mois, donc 0 PDF est normal
    # UNIQUEMENT si on cherche le mois en cours (pas encore publié)
    now = datetime.datetime.now()
    isReunionMoisEnCours = (annee == now.year and mois_num == now.month)

    regions_zero_pdf = []
    regions_zero_attendu = []

    for region, data in stats["par_region"].items():
        if data["trouves"] > 0:
            continue
        if region == "reunion" and isReunionMoisEnCours:
            regions_zero_attendu.append(region)
        else:
            regions_zero_pdf.append(region)

    if regions_zero_pdf:
        print()
        print("!" * 60)
        log(
            f"ATTENTION : {len(regions_zero_pdf)} region(s) avec 0 PDF trouve !",
            "WARNING"
        )
        print()
        for region in regions_zero_pdf:
            print(f"   /!\\ {region} : 0 PDF — l'extracteur ne fonctionne peut-etre plus")
        print()
        print("   Cause probable : le site de la prefecture a change de structure.")
        print("   Action : verifier manuellement le site et mettre a jour l'extracteur.")
        print("!" * 60)

        logger.warning(f"Regions avec 0 PDF (extracteur potentiellement casse): {regions_zero_pdf}")

    if regions_zero_attendu:
        print()
        log(
            "reunion : 0 PDF — normal, les RAA du mois en cours ne sont pas encore publies",
            "INFO"
        )

    # Résumé global
    print()
    if tous_resultats:
        log(
            f"TERMINE : {stats['total_pdfs_trouves']} PDF trouves, "
            f"{stats['total_pages']} page(s) pertinente(s), "
            f"{stats['total_pdfs_crees']} extrait(s) cree(s)",
            "SUCCESS"
        )
        logger.info(
            f"=== Termine: {stats['total_pdfs_trouves']} trouves, "
            f"{stats['total_pages']} pages, {stats['total_pdfs_crees']} extraits ==="
        )
    else:
        log("Aucune autorisation trouvee pour ce mois", "WARNING")
        logger.warning("Aucune autorisation trouvee")

    if stats["skipped"] > 0:
        log(f"{stats['skipped']} PDF(s) ignore(s) (deja traites via cache)", "INFO")

    logger.info(f"Detail: {stats['par_region']}")

    print()
    print("-" * 60)
    print("FICHIERS:")
    print(f"   PDFs extraits: {output_base}")
    print(f"   Excel unique:  {HISTORIQUE_EXCEL}")
    print(f"   Logs:          {os.path.join(output_base, 'smartars.log')}")
    print("-" * 60)
    log("Termine", "END")


def main():
    """Point d'entrée : mode interactif ou ligne de commande."""
    args = sys.argv[1:]

    if len(args) == 0:
        _mode_interactif()
        return

    if len(args) < 2:
        _afficher_aide()
        return

    _mode_ligne_commande(args)


def _mode_interactif():
    """Lance le menu interactif."""
    mois_list, annees_list, regions = afficher_menu()
    if not mois_list or not annees_list:
        return

    total_combos = len(mois_list) * len(annees_list)
    combo_num = 0
    for annee in annees_list:
        for mois_num in mois_list:
            combo_num += 1
            if total_combos > 1:
                print()
                print("*" * 60)
                print(f"*  Analyse {combo_num}/{total_combos}: {MOIS_NOMS.get(mois_num)} {annee}")
                print("*" * 60)
            run_bot(mois_num, annee, regions)


def _mode_ligne_commande(args):
    """Lance l'analyse depuis les arguments de la ligne de commande."""
    mois_input = args[0]
    annee_input = args[1]

    mois_list = parser_mois_multiples(mois_input)
    annees_list = parser_annees_multiples(annee_input)

    if not mois_list:
        print(f"Erreur: mois invalide '{mois_input}'")
        return
    if not annees_list:
        print(f"Erreur: annee invalide '{annee_input}'")
        return

    skip_cache = "--force" in args
    regions = [a for a in args[2:] if not a.startswith("--")]
    if not regions:
        regions = None

    total_combos = len(mois_list) * len(annees_list)
    combo_num = 0
    for annee in annees_list:
        for mois_num in mois_list:
            combo_num += 1
            if total_combos > 1:
                print()
                print("*" * 60)
                print(f"*  Analyse {combo_num}/{total_combos}: {MOIS_NOMS.get(mois_num)} {annee}")
                print("*" * 60)
            run_bot(mois_num, annee, regions, skip_cache)


def _afficher_aide():
    """Affiche l'aide en ligne de commande."""
    print("Usage: python main.py <mois> <annee> [regions...]")
    print()
    print("Exemples:")
    print("  python main.py                         # Mode interactif")
    print("  python main.py novembre 2025           # Toutes regions")
    print("  python main.py 11 2025 bretagne        # Region specifique")
    print("  python main.py 10,11 2025              # Plusieurs mois")
    print("  python main.py 11 2024,2025            # Plusieurs annees")
    print("  python main.py 10,11,12 2024,2025      # Plusieurs mois ET annees")
    print()
    print("Options:")
    print("  --force    Ignorer le cache et re-analyser tout")
    print()
    print("Regions disponibles:")
    for r in sorted(EXTRACTEURS.keys()):
        print(f"  - {r}")
    print()
    print(f"Sortie: ~/Documents/SmartARS/results/{{annee}}_{{mois}}/{{region}}/")


if __name__ == "__main__":
    main()
