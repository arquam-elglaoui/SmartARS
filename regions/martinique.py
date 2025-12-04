# -*- coding: utf-8 -*-
"""Extracteur: Martinique - RAA normal + spécial"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, log, MOIS_NOMS

BASE_URL = "https://www.martinique.gouv.fr"


def extraire_martinique(mois_num, annee):
    log(f"Martinique - {mois_num:02d}/{annee}", "SEARCH")
    
    mois_nom = MOIS_NOMS.get(mois_num, "").capitalize()
    pdf_links = []
    
    # RAA normal
    url1 = f"{BASE_URL}/Publications/Recueils-des-actes-administratifs-publies/RAA-{annee}/Recueil-des-Actes-Administratifs/{mois_nom}"
    soup = get_soup(url1)
    if soup:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower():
                if href.startswith('/'):
                    href = BASE_URL + href
                if href not in pdf_links:
                    pdf_links.append(href)
    
    # RAA spécial
    url2 = f"{BASE_URL}/Publications/Recueils-des-actes-administratifs-publies/RAA-{annee}/Recueil-des-Actes-Administratifs-Special/{mois_nom}"
    soup = get_soup(url2)
    if soup:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower():
                if href.startswith('/'):
                    href = BASE_URL + href
                if href not in pdf_links:
                    pdf_links.append(href)
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
