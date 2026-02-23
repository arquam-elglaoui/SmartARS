# -*- coding: utf-8 -*-
"""
SmartARS - Utilitaires (façade)
================================
Ce module ré-exporte les fonctions depuis les modules spécialisés.
Les fichiers regions/ importent depuis utils, ce fichier assure
la compatibilité sans modifier les 17 extracteurs.

Modules internes :
- date_utils : normalisation mois, accents, validation de dates
- pdf_analyzer : analyse du contenu des PDFs
- http (ci-dessous) : téléchargement web et parsing HTML
"""

import logging
import time

import requests
import urllib3
from bs4 import BeautifulSoup

from config import (
    DELAY_BETWEEN_REQUESTS,
    HTTP_HEADERS,
    MAX_RETRIES,
    MOIS_NOMS,
    TIMEOUT_PAGE,
    TIMEOUT_PDF,
)

from date_utils import (  # noqa: F401 — ré-exporté pour les régions
    contient_autre_mois,
    contient_date_stricte,
    contient_mois,
    get_mois_variantes,
    normaliser_accents,
    normaliser_mois,
)

from pdf_analyzer import analyser_pdf_pages  # noqa: F401

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("SmartARS")


def log(message, level="INFO"):
    """Affiche un message formaté dans la console avec une icône."""
    icons = {
        "INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️",
        "FOUND": "🎉", "SEARCH": "🔍", "DOWNLOAD": "📥", "REGION": "📍",
        "START": "🚀", "END": "🏁", "PDF": "📄",
    }

    icon = icons.get(level, '•')

    if level == "ERROR":
        print()
        print("!" * 60)
        print(f"{icon} ERREUR: {message}")
        print("!" * 60)
        print()
    elif level == "WARNING":
        print(f"{icon} [ATTENTION] {message}")
    else:
        print(f"{icon} {message}")


def telecharger_page(url, timeout=None, is_pdf=False, max_retries=None):
    """
    Télécharge une page web ou un PDF avec retry automatique
    et backoff exponentiel en cas d'erreur.

    Retourne un objet Response ou None si toutes les tentatives échouent.
    """
    if timeout is None:
        timeout = TIMEOUT_PDF if is_pdf else TIMEOUT_PAGE
    if max_retries is None:
        max_retries = MAX_RETRIES

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            delay = DELAY_BETWEEN_REQUESTS * attempt
            time.sleep(delay)

            response = requests.get(
                url,
                headers=HTTP_HEADERS,
                timeout=timeout,
                verify=False,
                stream=is_pdf,
            )

            if response.status_code == 200:
                if is_pdf:
                    content = response.content
                    if len(content) < 1000:
                        logger.warning(f"PDF trop petit ({len(content)} bytes): {url}")
                        continue
                return response

            elif response.status_code == 404:
                logger.warning(f"HTTP 404 (introuvable): {url}")
                return None

            elif response.status_code == 403:
                # 403 peut être temporaire (rate limiting des sites gouv)
                last_error = f"HTTP 403"
                logger.warning(f"HTTP 403 acces refuse (tentative {attempt}/{max_retries}): {url}")

            elif response.status_code >= 500:
                last_error = f"HTTP {response.status_code}"
                logger.warning(f"HTTP {response.status_code} (tentative {attempt}/{max_retries}): {url}")

            else:
                logger.warning(f"HTTP {response.status_code}: {url}")
                return None

        except requests.exceptions.Timeout:
            last_error = "Timeout"
            logger.warning(f"Timeout (tentative {attempt}/{max_retries}): {url}")

        except requests.exceptions.ConnectionError as e:
            last_error = "Connexion"
            error_msg = str(e)
            if "IncompleteRead" in error_msg:
                logger.warning(f"Lecture incomplete (tentative {attempt}/{max_retries}): {url}")
            else:
                logger.warning(f"Erreur connexion (tentative {attempt}/{max_retries}): {url}")

        except requests.exceptions.ChunkedEncodingError:
            last_error = "Encoding"
            logger.warning(f"Erreur transfert (tentative {attempt}/{max_retries}): {url}")

        except Exception as e:
            last_error = str(e)[:50]
            logger.warning(f"Erreur {e} (tentative {attempt}/{max_retries}): {url}")

        if attempt < max_retries:
            wait_time = 2 ** (attempt - 1)
            time.sleep(wait_time)

    logger.error(f"Echec apres {max_retries} tentatives ({last_error}): {url}")
    return None


def get_soup(url):
    """Télécharge et parse une page HTML en BeautifulSoup."""
    response = telecharger_page(url)
    if response:
        return BeautifulSoup(response.text, 'html.parser')
    return None


def get_soup_multi_urls(urls):
    """
    Essaie plusieurs URLs et retourne le premier résultat valide.
    Utile quand on ne sait pas si le site utilise des accents.

    Retourne (soup, url_valide) ou (None, None).
    """
    for url in urls:
        soup = get_soup(url)
        if soup:
            return soup, url
    return None, None
