# -*- coding: utf-8 -*-
"""
SmartARS - Extraction de PDF
==============================
Crée des PDFs extraits à partir des RAA complets.

Chaque PDF extrait contient :
- Les premières pages (couverture + sommaire)
- Les pages contenant des autorisations d'équipements
"""

import logging
import os
from urllib.parse import unquote

import fitz

logger = logging.getLogger("SmartARS")


def detecter_fin_sommaire(pdf_bytes, max_pages=10):
    """
    Détecte où se termine le sommaire dans un PDF.
    Cherche des patterns indiquant le début du contenu réel
    (ex: "vu le code", "le préfet", "article 1").

    Retourne l'index de la dernière page du sommaire (0-indexed).
    Par défaut : page 2 (= 3 premières pages).
    """
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num in range(min(max_pages, len(doc))):
                text = doc[page_num].get_text().lower()

                patterns_fin_sommaire = [
                    "vu le code",
                    "le préfet",
                    "le directeur",
                    "arrête",
                    "article 1",
                    "décide",
                ]

                for pattern in patterns_fin_sommaire:
                    if pattern in text and page_num > 0:
                        return max(0, page_num - 1)

            return min(2, len(doc) - 1)
    except Exception:
        return 2


def creer_pdf_par_raa(pdf_bytes, pages_pertinentes, output_dir, nom_fichier_original):
    """
    Crée un PDF extrait d'un RAA contenant les pages de garde
    et les pages pertinentes (autorisations).

    Retourne le chemin du fichier créé ou None en cas d'erreur.
    """
    if not pages_pertinentes:
        return None

    try:
        src = fitz.open(stream=pdf_bytes, filetype="pdf")
        doc = fitz.open()

        fin_sommaire = detecter_fin_sommaire(pdf_bytes)

        # Collecter toutes les pages (sommaire + pertinentes), sans doublons
        toutes_pages = set(range(0, fin_sommaire + 1))
        toutes_pages.update(pages_pertinentes)
        toutes_pages = sorted(toutes_pages)

        for page_num in toutes_pages:
            if page_num < len(src):
                doc.insert_pdf(src, from_page=page_num, to_page=page_num)

        src.close()

        filename = _nettoyer_nom_fichier(nom_fichier_original)
        filepath = os.path.join(output_dir, filename)

        doc.save(filepath)
        doc.close()

        return filepath

    except Exception as e:
        logger.error(f"Erreur creation PDF: {e}")
        return None


def _nettoyer_nom_fichier(nom_original):
    """Nettoie le nom de fichier PDF pour le système de fichiers."""
    nom_clean = nom_original

    if nom_clean.lower().endswith('.pdf'):
        nom_clean = nom_clean[:-4]

    try:
        nom_clean = unquote(nom_clean)
    except Exception:
        pass

    nom_clean = nom_clean.replace('+', '_').replace('%', '_')
    return f"{nom_clean}_EXTRACT.pdf"
