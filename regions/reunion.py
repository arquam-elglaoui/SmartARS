# -*- coding: utf-8 -*-
"""Extracteur: La Réunion - URL directe par mois (MAJUSCULES)"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, log, get_mois_variantes

BASE_URL = "https://www.reunion.gouv.fr"


def extraire_reunion(mois_num, annee):
    log(f"La Réunion - {mois_num:02d}/{annee}", "SEARCH")
    
    pdf_links = []
    
    # Essayer toutes les variantes (avec/sans accents, différentes casses)
    for mois_nom in get_mois_variantes(mois_num):
        url = f"{BASE_URL}/Publications/Publications-administratives-et-legales/Recueil-des-actes-administratifs-RAA/Recueil-des-actes-administratifs-{annee}/{mois_nom.upper()}"
        
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
            break  # Trouvé, pas besoin d'essayer les autres variantes
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
