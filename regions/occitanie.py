# -*- coding: utf-8 -*-
"""
Extracteur: Occitanie
=====================
Site avec pagination - recherche des RAA du mois spécifique.
AMÉLIORÉ: Filtrage plus strict et meilleure gestion de la pagination.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_soup, contient_date_stricte, log

BASE_URL = "https://www.prefectures-regions.gouv.fr"
URL_TAGS = f"{BASE_URL}/occitanie/tags/view/Occitanie/Documents+et+publications/Recueil+des+actes+administratifs/"


def extraire_occitanie(mois_num, annee):
    log(f"Occitanie - {mois_num:02d}/{annee}", "SEARCH")
    
    pdf_links = []
    pages_a_visiter = []
    
    # Parcourir les pages de listing (max 5 pages)
    for offset in range(0, 50, 10):
        url = URL_TAGS if offset == 0 else f"{URL_TAGS}(offset)/{offset}"
        soup = get_soup(url)
        if not soup:
            break
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # Filtrage STRICT sur texte du lien ET URL
            # page_annuelle=True pour le texte car parfois l'année n'est pas explicite
            if not (contient_date_stricte(text, mois_num, annee, page_annuelle=True) or contient_date_stricte(href, mois_num, annee)):
                continue
            
            if href.startswith('/'):
                href = BASE_URL + href
            
            if '.pdf' in href.lower():
                if href not in pdf_links:
                    pdf_links.append(href)
                    log(f"  {text[:55]}...", "PDF")
            else:
                # C'est probablement une page de détail à visiter
                if href not in pages_a_visiter and 'recueil' in href.lower():
                    pages_a_visiter.append(href)
    
    # Visiter les sous-pages de détail (max 10)
    for page_url in pages_a_visiter[:10]:
        soup = get_soup(page_url)
        if not soup:
            continue
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower():
                if href.startswith('/'):
                    href = BASE_URL + href
                if href not in pdf_links:
                    text = a.get_text(strip=True)
                    pdf_links.append(href)
                    log(f"  {text[:55]}...", "PDF")
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    return pdf_links
