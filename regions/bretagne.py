# -*- coding: utf-8 -*-
"""Extracteur: Bretagne"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, contient_date_stricte, log, logger

BASE_URL = "https://www.prefectures-regions.gouv.fr"
URL_RAA = f"{BASE_URL}/bretagne/Documents-publications/Recueils-des-actes-administratifs/Recueil-des-actes-administratifs"


def extraire_bretagne(mois_num, annee):
    log(f"Bretagne - {mois_num:02d}/{annee}", "SEARCH")
    
    soup = get_soup(URL_RAA)
    if not soup:
        return []
    
    pdf_links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' not in href.lower():
            continue
        
        text = a.get_text(strip=True)
        if contient_date_stricte(text, mois_num, annee) or contient_date_stricte(href, mois_num, annee):
            if href.startswith('/'):
                href = BASE_URL + href
            if href not in pdf_links:
                pdf_links.append(href)
                log(f"  {text[:55]}...", "PDF")
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
