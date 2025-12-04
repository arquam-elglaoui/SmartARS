# -*- coding: utf-8 -*-
"""Extracteurs par région"""

from .auvergne_rhone_alpes import extraire_auvergne_rhone_alpes
from .bourgogne_franche_comte import extraire_bourgogne_franche_comte
from .bretagne import extraire_bretagne
from .centre_val_de_loire import extraire_centre_val_de_loire
from .corse import extraire_corse
from .grand_est import extraire_grand_est
from .guadeloupe import extraire_guadeloupe
from .guyane import extraire_guyane
from .hauts_de_france import extraire_hauts_de_france
from .ile_de_france import extraire_ile_de_france
from .martinique import extraire_martinique
from .normandie import extraire_normandie
from .nouvelle_aquitaine import extraire_nouvelle_aquitaine
from .occitanie import extraire_occitanie
from .pays_de_la_loire import extraire_pays_de_la_loire
from .provence_alpes_cote_azur import extraire_provence_alpes_cote_azur
from .reunion import extraire_reunion

EXTRACTEURS = {
    "auvergne-rhone-alpes": extraire_auvergne_rhone_alpes,
    "bourgogne-franche-comte": extraire_bourgogne_franche_comte,
    "bretagne": extraire_bretagne,
    "centre-val-de-loire": extraire_centre_val_de_loire,
    "corse": extraire_corse,
    "grand-est": extraire_grand_est,
    "guadeloupe": extraire_guadeloupe,
    "guyane": extraire_guyane,
    "hauts-de-france": extraire_hauts_de_france,
    "ile-de-france": extraire_ile_de_france,
    "martinique": extraire_martinique,
    "normandie": extraire_normandie,
    "nouvelle-aquitaine": extraire_nouvelle_aquitaine,
    "occitanie": extraire_occitanie,
    "pays-de-la-loire": extraire_pays_de_la_loire,
    "paca": extraire_provence_alpes_cote_azur,
    "reunion": extraire_reunion,
}
