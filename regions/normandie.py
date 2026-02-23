# -*- coding: utf-8 -*-
"""
Extracteur: Normandie - URL directe par mois

Deux formats d'URL coexistent :
- Jusqu'en 2025 : "Recueils-des-actes-administratifs-regionaux-{Mois}-{AAAA}" (avec S)
- A partir de 2026 : "Recueil-des-actes-administratifs-regionaux-{Mois}-{AAAA}" (sans S)
  + le dossier parent change aussi de casse

On essaie les deux formats : si l'un ne marche pas, l'autre prend le relais.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_soup, log, get_mois_variantes

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_normandie(mois_num, annee):
    """Extrait les PDF des RAA de Normandie."""
    log(f"Normandie - {mois_num:02d}/{annee}", "SEARCH")

    pdf_links = []

    for mois_nom in get_mois_variantes(mois_num):
        mois_cap = mois_nom.capitalize()

        urls_a_essayer = _construire_urls(mois_cap, annee)

        for url in urls_a_essayer:
            soup = get_soup(url)
            if not soup:
                continue

            for a in soup.find_all('a', href=True):
                href = a['href']
                if '.pdf' in href.lower():
                    if href.startswith('/'):
                        href = BASE_URL + href
                    if href not in pdf_links:
                        pdf_links.append(href)
                        log(f"  {a.get_text(strip=True)[:55]}...", "PDF")

            if pdf_links:
                break

        if pdf_links:
            break

    log(f"  -> {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links


def _construire_urls(mois_cap, annee):
    """
    Construit la liste d'URLs à essayer pour un mois/année donné.
    On essaie les deux formats connus + les deux casses du dossier parent.
    """
    return [
        # Format 2026+ : "Recueil" sans S, dossier parent en minuscules
        f"{BASE_URL}/normandie/Documents-publications/Recueil-des-Actes-Administratifs/Recueil-des-actes-administratifs-{annee}/Recueil-des-actes-administratifs-regionaux-{mois_cap}-{annee}",
        # Format <=2025 : "Recueils" avec S, dossier parent en majuscules
        f"{BASE_URL}/normandie/Documents-publications/Recueil-des-Actes-Administratifs/Recueil-des-Actes-Administratifs-{annee}/Recueils-des-actes-administratifs-regionaux-{mois_cap}-{annee}",
    ]
