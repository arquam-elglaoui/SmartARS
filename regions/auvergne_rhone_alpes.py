# -*- coding: utf-8 -*-
"""
Extracteur: Auvergne-Rhône-Alpes
================================
URL: https://www.prefectures-regions.gouv.fr/auvergne-rhone-alpes/Documents-publications/Recueil-regional-des-actes-administratifs-RAA

Tous les RAA sur une seule page - filtrage STRICT par mois/année.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_soup, contient_date_stricte, log, logger

BASE_URL = "https://www.prefectures-regions.gouv.fr"
URL_RAA = f"{BASE_URL}/auvergne-rhone-alpes/Documents-publications/Recueil-regional-des-actes-administratifs-RAA"


def extraire_auvergne_rhone_alpes(mois_num, annee):
    """Extrait les PDF du mois/année spécifié UNIQUEMENT."""
    log(f"Auvergne-Rhône-Alpes - {mois_num:02d}/{annee}", "SEARCH")
    
    soup = get_soup(URL_RAA)
    if not soup:
        logger.error("Auvergne-Rhône-Alpes: Impossible de charger la page")
        return []
    
    pdf_links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' not in href.lower():
            continue
        
        # Texte du lien + URL pour le filtrage
        text = a.get_text(strip=True)
        
        # Vérifier STRICTEMENT si c'est le bon mois/année
        # On vérifie dans le texte (page_annuelle car pas toujours l'année) ET dans l'URL
        if contient_date_stricte(text, mois_num, annee, page_annuelle=True) or contient_date_stricte(href, mois_num, annee):
            if href.startswith('/'):
                href = BASE_URL + href
            if href not in pdf_links:
                pdf_links.append(href)
                log(f"  {text[:55]}...", "PDF")
    
    log(f"  → {len(pdf_links)} PDF", "SUCCESS" if pdf_links else "WARNING")
    logger.info(f"Auvergne-Rhône-Alpes: {len(pdf_links)} PDF pour {mois_num:02d}/{annee}")
    return pdf_links
