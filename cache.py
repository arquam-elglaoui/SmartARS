# -*- coding: utf-8 -*-
"""
SmartARS - Gestion du cache anti-doublons
==========================================
Stocke les URLs déjà traitées pour éviter de re-télécharger
les mêmes PDFs lors d'exécutions successives.

Le cache est un fichier JSON dans ~/Documents/SmartARS/.cache.json
"""

import hashlib
import json
import os

BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SmartARS")
CACHE_FILE = os.path.join(BASE_DIR, ".cache.json")


def load_cache():
    """Charge le cache des URLs déjà traitées depuis le disque."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"processed_urls": {}}


def save_cache(cache):
    """Sauvegarde le cache sur le disque."""
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def get_url_hash(url):
    """Génère un hash court (12 caractères) pour identifier une URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def is_already_processed(cache, url, mois_num, annee):
    """Vérifie si une URL a déjà été traitée pour ce mois/année."""
    key = f"{annee}_{mois_num}"
    url_hash = get_url_hash(url)
    return (
        key in cache.get("processed_urls", {})
        and url_hash in cache["processed_urls"].get(key, [])
    )


def mark_as_processed(cache, url, mois_num, annee):
    """Marque une URL comme traitée dans le cache."""
    key = f"{annee}_{mois_num}"
    url_hash = get_url_hash(url)

    if "processed_urls" not in cache:
        cache["processed_urls"] = {}
    if key not in cache["processed_urls"]:
        cache["processed_urls"][key] = []

    if url_hash not in cache["processed_urls"][key]:
        cache["processed_urls"][key].append(url_hash)
