# -*- coding: utf-8 -*-
"""Extracteur: Pays de la Loire - URL directe par mois"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, log, MOIS_NOMS

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_pays_de_la_loire(mois_num, annee):
    log(f"Pays de la Loire - {mois_num:02d}/{annee}", "SEARCH")
    
    mois_nom = MOIS_NOMS.get(mois_num, "").capitalize()
    url = f"{BASE_URL}/pays-de-la-loire/DOCUMENTS-PUBLICATIONS/Publications-legales/Recueil-des-actes-administratifs-RAA/RAA-prefecture-de-region-des-Pays-de-la-Loire/RAA-de-la-prefecture-de-region-des-Pays-de-la-Loire-{annee}/{mois_nom}-{annee}/"
    
    soup = get_soup(url)
    if not soup:
        return []
    
    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' in href.lower():
            if href.startswith('/'):
                href = BASE_URL + href
            if href not in pdf_links:
                pdf_links.append(href)
                log(f"  {a.get_text(strip=True)[:55]}...", "PDF")
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
