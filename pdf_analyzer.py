# -*- coding: utf-8 -*-
"""
SmartARS - Analyse du contenu PDF
====================================
Analyse les pages d'un PDF pour détecter les autorisations
d'équipements d'imagerie médicale (IRM, Scanner, TEP, etc.).

Utilise des regex pour une détection précise,
puis vérifie que c'est bien une autorisation (pas juste une mention).
"""

import logging
import re

import fitz

from config import KEYWORDS_AUTORISATION, KEYWORDS_REGEX

logger = logging.getLogger("SmartARS")


def analyser_pdf_pages(pdf_bytes):
    """
    Analyse un PDF page par page et retourne celles
    qui contiennent des autorisations d'équipements.

    Retourne une liste de dicts avec : page_num, equipements,
    texte, est_autorisation, etablissement, ville.
    """
    pages_pertinentes = []

    compiled_patterns = _compiler_patterns()

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc):
                text = page.get_text()

                equipements_trouves = _chercher_equipements(text, compiled_patterns)
                if not equipements_trouves:
                    continue

                est_autorisation = _est_autorisation(text)
                info = _extraire_infos_page(text)

                pages_pertinentes.append({
                    "page_num": page_num,
                    "equipements": equipements_trouves,
                    "texte": text,
                    "est_autorisation": est_autorisation,
                    "etablissement": info.get("etablissement", ""),
                    "ville": info.get("ville", ""),
                })

    except Exception as e:
        logger.error(f"Erreur lecture PDF: {e}")

    return pages_pertinentes


def _compiler_patterns():
    """Compile les regex de détection d'équipements une seule fois."""
    compiled = []
    for pattern_str in KEYWORDS_REGEX:
        try:
            compiled.append((pattern_str, re.compile(pattern_str, re.IGNORECASE)))
        except re.error:
            logger.warning(f"Regex invalide: {pattern_str}")
    return compiled


def _chercher_equipements(text, compiled_patterns):
    """Cherche les équipements médicaux dans le texte d'une page."""
    equipements = []
    for pattern_str, pattern in compiled_patterns:
        if pattern.search(text):
            nom = pattern_str.replace(r'\b', '').replace(r'\s+', ' ').replace(r'\s{1,2}', ' ')
            nom = nom.replace('(?:s)?', '').replace('(?:s)', '').strip()
            if nom not in equipements:
                equipements.append(nom)
    return equipements


def _est_autorisation(text):
    """Vérifie si le texte contient des mots-clés d'autorisation."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in KEYWORDS_AUTORISATION)


def _extraire_infos_page(text):
    """Extrait le nom d'établissement et le code postal d'une page."""
    info = {"etablissement": "", "ville": ""}
    text_lower = text.lower()

    patterns_etab = [
        r"(?:centre hospitalier|ch |chu |chru |clinique|hôpital|hopital)[^,\n]{3,60}",
        r"(?:groupe hospitalier|ghm |gh )[^,\n]{3,60}",
        r"(?:établissement|etablissement)[^:]*:\s*([^\n,]{5,60})",
    ]

    for pattern in patterns_etab:
        match = re.search(pattern, text_lower)
        if match:
            info["etablissement"] = match.group(0).strip().title()[:60]
            break

    match_cp = re.search(r'\(?\s*(\d{5})\s*\)?', text)
    if match_cp:
        info["ville"] = match_cp.group(1)

    return info
