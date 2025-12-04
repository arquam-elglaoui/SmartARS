# -*- coding: utf-8 -*-
"""Extracteur: Guadeloupe - URL directe par mois"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, log, MOIS_NOMS

BASE_URL = "https://www.guadeloupe.gouv.fr"


def extraire_guadeloupe(mois_num, annee):
    log(f"Guadeloupe - {mois_num:02d}/{annee}", "SEARCH")
    
    mois_nom = MOIS_NOMS.get(mois_num, "").capitalize()
    url = f"{BASE_URL}/Publications/Le-Recueil-des-actes-administratifs/{annee}/{mois_nom}-{annee}"
    
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
