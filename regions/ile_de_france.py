# -*- coding: utf-8 -*-
"""Extracteur: Île-de-France - URL directe par mois"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, log
from config import MOIS_NOMS, MOIS_NOMS_URL

BASE_URL = "https://www.prefectures-regions.gouv.fr"


def extraire_ile_de_france(mois_num, annee):
    log(f"Île-de-France - {mois_num:02d}/{annee}", "SEARCH")
    
    pdf_links = []
    
    # Essayer les deux variantes (avec et sans accents)
    mois_variantes = [
        MOIS_NOMS_URL.get(mois_num, "").capitalize(),  # Avec accents (Décembre)
        MOIS_NOMS.get(mois_num, "").capitalize(),       # Sans accents (Decembre)
    ]
    
    for mois_nom in mois_variantes:
        url = f"{BASE_URL}/ile-de-france/Documents-publications/Recueil-des-actes-administratifs/RAA-de-la-region-Ile-de-France-{annee}/{mois_nom}/"
        
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
        
        # Si on a trouvé des PDFs, pas besoin d'essayer l'autre variante
        if pdf_links:
            break
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
