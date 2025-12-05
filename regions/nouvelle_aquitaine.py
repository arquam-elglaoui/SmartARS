# -*- coding: utf-8 -*-
"""Extracteur: Nouvelle-Aquitaine - URL directe par mois"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, log, get_mois_variantes

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_nouvelle_aquitaine(mois_num, annee):
    log(f"Nouvelle-Aquitaine - {mois_num:02d}/{annee}", "SEARCH")
    
    pdf_links = []
    
    # Essayer les variantes avec/sans accents
    for mois_nom in get_mois_variantes(mois_num):
        url = f"{BASE_URL}/nouvelle-aquitaine/Documents-publications/Recueil-des-Actes-Administratifs/Recueil-des-Actes-Administratifs-pour-l-annee-{annee}/{mois_nom.capitalize()}-{annee}/"
        
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
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
