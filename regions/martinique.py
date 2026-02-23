# -*- coding: utf-8 -*-
"""
Extracteur: Martinique - RAA normal + spécial

Deux formats d'URL coexistent :
- Jusqu'en 2025 : une page par mois  .../RAA-{AAAA}/Recueil-...//{Mois}
- A partir de 2026 : tous les RAA de l'année sur une seule page .../RAA-{AAAA}/Recueil-...
  (filtrage par date dans le nom du fichier, comme Bourgogne-Franche-Comté)

On essaie les deux formats : si l'un ne marche pas, l'autre prend le relais.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_soup, log, get_mois_variantes, contient_date_stricte

BASE_URL = "https://www.martinique.gouv.fr"


def extraire_martinique(mois_num, annee):
    """Extrait les PDF des RAA de Martinique (normal + spécial)."""
    log(f"Martinique - {mois_num:02d}/{annee}", "SEARCH")

    pdf_links = _extraire_par_mois(mois_num, annee)

    if not pdf_links:
        pdf_links = _extraire_par_annee(mois_num, annee)

    log(f"  -> {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links


def _extraire_par_mois(mois_num, annee):
    """Format avec mois dans l'URL (jusqu'en 2025)."""
    pdf_links = []

    for mois_nom in get_mois_variantes(mois_num):
        mois_cap = mois_nom.capitalize()

        urls = [
            f"{BASE_URL}/Publications/Recueils-des-actes-administratifs-publies/RAA-{annee}/Recueil-des-Actes-Administratifs/{mois_cap}",
            f"{BASE_URL}/Publications/Recueils-des-actes-administratifs-publies/RAA-{annee}/Recueil-des-Actes-Administratifs-Special/{mois_cap}",
        ]

        for url in urls:
            _collecter_pdfs_page(url, pdf_links)

        if pdf_links:
            break

    return pdf_links


def _extraire_par_annee(mois_num, annee):
    """Format annuel sans mois dans l'URL (2026+), filtrage par date."""
    pdf_links = []

    urls = [
        f"{BASE_URL}/Publications/Recueils-des-actes-administratifs-publies/RAA-{annee}/Recueil-des-Actes-Administratifs",
        f"{BASE_URL}/Publications/Recueils-des-actes-administratifs-publies/RAA-{annee}/Recueil-des-Actes-Administratifs-Special",
    ]

    for url in urls:
        soup = get_soup(url)
        if not soup:
            continue

        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' not in href.lower():
                continue

            text = a.get_text(strip=True)
            # page_annuelle=True : le mois n'est pas dans l'URL mais dans le nom du fichier
            if contient_date_stricte(text, mois_num, annee, page_annuelle=True) or contient_date_stricte(href, mois_num, annee):
                if href.startswith('/'):
                    href = BASE_URL + href
                if href not in pdf_links:
                    pdf_links.append(href)

    return pdf_links


def _collecter_pdfs_page(url, pdf_links):
    """Récupère tous les liens PDF d'une page."""
    soup = get_soup(url)
    if not soup:
        return

    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' in href.lower():
            if href.startswith('/'):
                href = BASE_URL + href
            if href not in pdf_links:
                pdf_links.append(href)
