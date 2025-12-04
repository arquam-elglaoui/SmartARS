# -*- coding: utf-8 -*-
"""
Extracteur: Grand Est
=====================
Page annuelle avec filtrage STRICT par mois/année.
CORRIGÉ: Ne pas utiliser parent_text qui cause des faux positifs.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, contient_date_stricte, log

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_grand_est(mois_num, annee):
    log(f"Grand Est - {mois_num:02d}/{annee}", "SEARCH")
    
    url = f"{BASE_URL}/grand-est/Documents-publications/Recueil-des-actes-administratifs-regional/Recueil-des-actes-administratifs/RAA-Annee-{annee}/"
    soup = get_soup(url)
    if not soup:
        return []
    
    pdf_links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' not in href.lower():
            continue
        
        text = a.get_text(strip=True)
        
        # Filtrage STRICT: uniquement texte du lien ET URL
        # (pas de parent_text qui peut contenir plusieurs mois)
        if contient_date_stricte(text, mois_num, annee) or contient_date_stricte(href, mois_num, annee):
            if href.startswith('/'):
                href = BASE_URL + href
            if href not in pdf_links:
                pdf_links.append(href)
                log(f"  {text[:55]}...", "PDF")
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
