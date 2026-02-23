# -*- coding: utf-8 -*-
"""
SmartARS - Utilitaires de dates et texte
==========================================
Fonctions de normalisation des mois, accents,
et validation stricte des dates dans les textes/URLs.
"""

import re

from config import MOIS_FR, MOIS_NOMS, MOIS_NOMS_URL


def normaliser_mois(mois):
    """
    Convertit un mois en tuple (nom, numero).
    Accepte un nom ("novembre"), un string numérique ("11") ou un int (11).
    """
    if isinstance(mois, int):
        return MOIS_NOMS.get(mois, ""), mois

    mois_str = str(mois).lower().strip()

    if mois_str.isdigit():
        num = int(mois_str)
        return MOIS_NOMS.get(num, ""), num

    mois_clean = mois_str.replace('é', 'e').replace('û', 'u').replace('è', 'e')
    num = MOIS_FR.get(mois_str, MOIS_FR.get(mois_clean, 0))
    return mois_clean, num


def get_mois_variantes(mois_num):
    """
    Retourne les variantes du nom de mois (avec/sans accents, majuscule).
    Utile pour essayer plusieurs URLs quand on ne sait pas
    si le site utilise des accents ou non.

    Ex pour décembre: ["decembre", "décembre", "Decembre", "Décembre"]
    """
    sans_accent = MOIS_NOMS.get(mois_num, "")
    avec_accent = MOIS_NOMS_URL.get(mois_num, "")

    return [
        sans_accent,
        avec_accent,
        sans_accent.capitalize(),
        avec_accent.capitalize(),
    ]


def normaliser_accents(texte):
    """Supprime les accents d'un texte pour faciliter la comparaison."""
    accents = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ç': 'c',
    }
    for accent, sans in accents.items():
        texte = texte.replace(accent, sans)
    return texte


def contient_mois(texte, mois_num):
    """
    Vérifie si le texte contient le mois recherché.
    Utile pour les pages annuelles où l'année est déjà dans l'URL.

    Ex: "Recueil n°614 du 04 décembre" -> True pour mois_num=12
    """
    texte_lower = normaliser_accents(texte.lower())
    mois_nom = MOIS_NOMS.get(mois_num, "")
    mois_str = str(mois_num).zfill(2)

    patterns = [
        rf'\d{{1,2}}\s+{mois_nom}',
        rf'{mois_nom}\s*:',
        rf'/{mois_str}/',
        rf'-{mois_str}-',
        rf'{mois_nom}\s+\d{{4}}',
    ]

    for pattern in patterns:
        if re.search(pattern, texte_lower):
            return True
    return False


def contient_autre_mois(texte, mois_num, annee):
    """
    Vérifie si le texte contient EXPLICITEMENT un mois DIFFERENT
    de celui recherché. Sert à exclure les faux positifs.
    """
    texte_lower = normaliser_accents(texte.lower())
    annee_str = str(annee)

    autres_mois = {k: v for k, v in MOIS_NOMS.items() if k != mois_num}

    for num, nom in autres_mois.items():
        patterns_autre = [
            rf'\d{{1,2}}\s+{nom}\s+{annee_str}',
            rf'{nom}\s+{annee_str}',
            rf'{nom}[\-_]{annee_str}',
        ]
        for pattern in patterns_autre:
            if re.search(pattern, texte_lower):
                return True

    return False


def contient_date_stricte(texte, mois_num, annee, page_annuelle=False):
    """
    Vérifie STRICTEMENT si un texte contient une date du mois/année demandé.

    Le mois et l'année doivent être ADJACENTS dans le texte.
    Gère les accents (décembre = decembre).

    Si page_annuelle=True, accepte le mois seul (l'année est implicite dans l'URL).
    """
    texte_lower = normaliser_accents(texte.lower())
    annee_str = str(annee)
    mois_nom = MOIS_NOMS.get(mois_num, "")
    mois_str = str(mois_num).zfill(2)
    mois_str_simple = str(mois_num)

    if page_annuelle:
        if _rejeter_autre_annee(texte_lower, mois_nom, mois_num, annee):
            return False
        if contient_mois(texte, mois_num):
            return True

    if contient_autre_mois(texte, mois_num, annee):
        return False

    patterns = [
        rf'\d{{1,2}}\s+{mois_nom}\s+{annee_str}',
        rf'{mois_nom}\s+{annee_str}',
        rf'\d{{1,2}}[/\-]{mois_str}[/\-]{annee_str}',
        rf'\d{{1,2}}[/\-]{mois_str_simple}[/\-]{annee_str}',
        rf'{annee_str}[/\-]{mois_str}[/\-]\d{{1,2}}',
        rf'{annee_str}[/\-]{mois_str_simple}[/\-]\d{{1,2}}',
        rf'{mois_nom}[\-_]{annee_str}',
        rf'{annee_str}[\-_]{mois_nom}',
        rf'{mois_str}[\-_]{annee_str}',
        rf'{annee_str}[\-_]{mois_str}[\-_]',
        rf'{annee_str}[\-_]{mois_str}(?:[^\d]|$)',
        rf'\d{{2}}{mois_str}{annee_str}',
    ]

    for pattern in patterns:
        if re.search(pattern, texte_lower):
            return True

    return False


def _rejeter_autre_annee(texte_lower, mois_nom, mois_num, annee):
    """Vérifie si le mois est mentionné avec une année différente (faux positif)."""
    annees_autres = [str(a) for a in range(2016, 2030) if a != annee]
    for autre_annee in annees_autres:
        if re.search(rf'\d{{1,2}}\s+{mois_nom}\s+{autre_annee}', texte_lower):
            return True
        if re.search(rf'{mois_nom}\s+{autre_annee}', texte_lower):
            return True

    autres_mois = [v for k, v in MOIS_NOMS.items() if k != mois_num]
    for autre in autres_mois:
        if re.search(rf'\d{{1,2}}\s+{autre}', texte_lower):
            return True

    return False
