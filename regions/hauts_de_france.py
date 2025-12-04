# -*- coding: utf-8 -*-
"""Extracteur: Hauts-de-France"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, contient_date_stricte, log

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_hauts_de_france(mois_num, annee):
    log(f"Hauts-de-France - {mois_num:02d}/{annee}", "SEARCH")
    
    url = f"{BASE_URL}/hauts-de-france/Documents-publications/Recueil-des-actes-administratifs/Recueil-des-actes-administratifs-de-l-Etat-en-Hauts-de-France-{annee}"
    soup = get_soup(url)
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
