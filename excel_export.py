# -*- coding: utf-8 -*-
"""
SmartARS - Export Excel historique
===================================
Gère le fichier Excel unique SmartARS_Historique.xlsx
qui centralise toutes les autorisations trouvées.

Chaque mois/année a sa propre feuille (ex: "2025_novembre").
Les doublons sont détectés via une clé unique par ligne.
"""

import logging
import os

import pandas as pd

from utils import MOIS_NOMS

BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SmartARS")
HISTORIQUE_EXCEL = os.path.join(BASE_DIR, "SmartARS_Historique.xlsx")

logger = logging.getLogger("SmartARS")


def _creer_cle_unique(row):
    """Crée une clé unique pour identifier une ligne (évite les doublons)."""
    return f"{row['Region']}|{row['Source']}|{row['Page']}|{row['Equipements']}"


def maj_historique_excel(resultats, mois_num, annee):
    """
    Met à jour le fichier Excel historique unique.
    Crée ou complète la feuille du mois/année concerné.

    Retourne le nombre de nouvelles lignes ajoutées.
    """
    if not resultats:
        return 0

    mois_nom = MOIS_NOMS.get(mois_num, str(mois_num).zfill(2))
    sheet_name = f"{annee}_{mois_nom}"

    os.makedirs(BASE_DIR, exist_ok=True)

    df_new = pd.DataFrame(resultats)
    df_new["_cle_unique"] = df_new.apply(_creer_cle_unique, axis=1)

    nb_ajoutes = 0

    try:
        if os.path.exists(HISTORIQUE_EXCEL):
            nb_ajoutes = _mettre_a_jour_fichier_existant(
                df_new, sheet_name
            )
        else:
            nb_ajoutes = _creer_nouveau_fichier(df_new, sheet_name)

    except Exception as e:
        logger.error(f"Erreur maj historique Excel: {e}")
        return 0

    return nb_ajoutes


def _mettre_a_jour_fichier_existant(df_new, sheet_name):
    """Ajoute les résultats à un fichier Excel existant."""
    with pd.ExcelFile(HISTORIQUE_EXCEL) as xls:
        existing_sheets = xls.sheet_names

    if sheet_name in existing_sheets:
        df_final, nb_ajoutes = _fusionner_avec_feuille(df_new, sheet_name)
    else:
        df_final = df_new
        nb_ajoutes = len(df_new)

    all_sheets = {}
    with pd.ExcelFile(HISTORIQUE_EXCEL) as xls:
        for sheet in xls.sheet_names:
            if sheet != sheet_name:
                all_sheets[sheet] = pd.read_excel(xls, sheet_name=sheet)

    all_sheets[sheet_name] = df_final

    with pd.ExcelWriter(HISTORIQUE_EXCEL, engine='openpyxl') as writer:
        for sname, sdf in sorted(all_sheets.items(), reverse=True):
            if "_cle_unique" in sdf.columns:
                sdf = sdf.drop(columns=["_cle_unique"])
            sdf.to_excel(writer, sheet_name=sname, index=False)

    return nb_ajoutes


def _fusionner_avec_feuille(df_new, sheet_name):
    """Fusionne les nouvelles données avec une feuille existante."""
    df_existing = pd.read_excel(HISTORIQUE_EXCEL, sheet_name=sheet_name)

    if "_cle_unique" not in df_existing.columns:
        df_existing["_cle_unique"] = df_existing.apply(
            lambda r: f"{r.get('Region', '')}|{r.get('Source', '')}|{r.get('Page', '')}|{r.get('Equipements', '')}",
            axis=1
        )

    cles_existantes = set(df_existing["_cle_unique"].tolist())
    df_nouvelles = df_new[~df_new["_cle_unique"].isin(cles_existantes)]

    nb_ajoutes = len(df_nouvelles)

    if nb_ajoutes > 0:
        df_final = pd.concat([df_existing, df_nouvelles], ignore_index=True)
    else:
        df_final = df_existing

    return df_final, nb_ajoutes


def _creer_nouveau_fichier(df_new, sheet_name):
    """Crée un nouveau fichier Excel historique."""
    df_final = df_new.drop(columns=["_cle_unique"])
    nb_ajoutes = len(df_final)

    with pd.ExcelWriter(HISTORIQUE_EXCEL, engine='openpyxl') as writer:
        df_final.to_excel(writer, sheet_name=sheet_name, index=False)

    return nb_ajoutes
