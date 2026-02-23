# -*- coding: utf-8 -*-
"""
Extracteur: Corse (3 sous-régions)
==================================
- Région Corse
- Corse du Sud  
- Haute-Corse
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, contient_date_stricte, log
from config import MOIS_NOMS, MOIS_NOMS_URL

BASE_CORSE_SUD = "https://www.corse-du-sud.gouv.fr"
BASE_HAUTE_CORSE = "https://www.haute-corse.gouv.fr"


def extraire_corse(mois_num, annee):
    log(f"Corse - {mois_num:02d}/{annee}", "SEARCH")
    
    pdf_links = []
    
    # Deux variantes du nom de mois (avec et sans accents)
    mois_variantes = [
        MOIS_NOMS_URL.get(mois_num, ""),  # Avec accents (décembre)
        MOIS_NOMS.get(mois_num, ""),       # Sans accents (decembre)
    ]
    
    # 1. Région Corse (page annuelle — le nom du fichier n'a pas toujours l'année)
    url1 = f"{BASE_CORSE_SUD}/Publications/Recueil-des-actes-administratifs/Recueil-des-actes-administratifs-de-la-Region-Corse/Recueil-des-actes-administratifs-de-la-Region-Corse-pour-l-annee-{annee}"
    soup = get_soup(url1)
    if soup:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower():
                text = a.get_text(strip=True)
                if contient_date_stricte(text, mois_num, annee, page_annuelle=True) or contient_date_stricte(href, mois_num, annee):
                    if href.startswith('/'):
                        href = BASE_CORSE_SUD + href
                    if href not in pdf_links:
                        pdf_links.append(href)
    
    # 2. Corse du Sud (page annuelle — même logique)
    url2 = f"{BASE_CORSE_SUD}/Publications/Recueil-des-actes-administratifs/Recueil-des-actes-administratifs-de-la-prefecture-de-la-Corse-du-Sud/Recueils-des-actes-administratifs-de-l-annee-{annee}"
    soup = get_soup(url2)
    if soup:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower():
                text = a.get_text(strip=True)
                if contient_date_stricte(text, mois_num, annee, page_annuelle=True) or contient_date_stricte(href, mois_num, annee):
                    if href.startswith('/'):
                        href = BASE_CORSE_SUD + href
                    if href not in pdf_links:
                        pdf_links.append(href)
    
    # 3. Haute-Corse - Essayer les deux variantes de nom de mois
    for mois_nom in mois_variantes:
        # URL avec "de"
        url3 = f"{BASE_HAUTE_CORSE}/Publications/Publications-administratives-et-legales/Recueils-des-actes-administratifs/Recueils-des-actes-administratifs-{annee}/RAA-du-mois-de-{mois_nom}-{annee}"
        soup = get_soup(url3)
        if soup:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '.pdf' in href.lower():
                    if href.startswith('/'):
                        href = BASE_HAUTE_CORSE + href
                    if href not in pdf_links:
                        pdf_links.append(href)
        
        # URL sans "de"
        url3b = f"{BASE_HAUTE_CORSE}/Publications/Publications-administratives-et-legales/Recueils-des-actes-administratifs/Recueils-des-actes-administratifs-{annee}/RAA-du-mois-{mois_nom}-{annee}"
        soup = get_soup(url3b)
        if soup:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '.pdf' in href.lower():
                    if href.startswith('/'):
                        href = BASE_HAUTE_CORSE + href
                    if href not in pdf_links:
                        pdf_links.append(href)
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
