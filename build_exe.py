# -*- coding: utf-8 -*-
"""
Script pour créer l'exécutable SmartARS.exe
===========================================
"""

import os
import subprocess
import sys

def build():
    """Crée l'exécutable avec PyInstaller."""
    
    print("=" * 60)
    print("   Construction de SmartARS.exe")
    print("=" * 60)
    print()
    
    # Vérifier que PyInstaller est installé
    try:
        import PyInstaller
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Chemin du script principal
    script_path = os.path.join(os.path.dirname(__file__), "smartars_gui.py")
    
    # Options PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SmartARS",           # Nom de l'exe
        "--onefile",                  # Un seul fichier
        "--windowed",                 # Pas de console
        "--clean",                    # Nettoyer avant build
        "--noconfirm",                # Pas de confirmation
        # Icône (optionnel)
        # "--icon=icon.ico",
        
        # === IMPORTS EXPLICITES DES RÉGIONS ===
        "--hidden-import=regions",
        "--hidden-import=regions.__init__",
        "--hidden-import=regions.auvergne_rhone_alpes",
        "--hidden-import=regions.bourgogne_franche_comte",
        "--hidden-import=regions.bretagne",
        "--hidden-import=regions.centre_val_de_loire",
        "--hidden-import=regions.corse",
        "--hidden-import=regions.grand_est",
        "--hidden-import=regions.guadeloupe",
        "--hidden-import=regions.guyane",
        "--hidden-import=regions.hauts_de_france",
        "--hidden-import=regions.ile_de_france",
        "--hidden-import=regions.martinique",
        "--hidden-import=regions.normandie",
        "--hidden-import=regions.nouvelle_aquitaine",
        "--hidden-import=regions.occitanie",
        "--hidden-import=regions.pays_de_la_loire",
        "--hidden-import=regions.provence_alpes_cote_azur",
        "--hidden-import=regions.reunion",
        
        # === MODULES PRINCIPAUX ===
        "--hidden-import=config",
        "--hidden-import=utils",
        "--hidden-import=date_utils",
        "--hidden-import=pdf_analyzer",
        "--hidden-import=pdf_extractor",
        "--hidden-import=analyzer",
        "--hidden-import=cache",
        "--hidden-import=excel_export",
        "--hidden-import=main",
        
        # === BIBLIOTHÈQUES EXTERNES ===
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=fitz",
        "--hidden-import=PyMuPDF",
        "--hidden-import=requests",
        "--hidden-import=bs4",
        "--hidden-import=beautifulsoup4",
        "--hidden-import=urllib3",
        "--hidden-import=logging",
        "--hidden-import=json",
        "--hidden-import=hashlib",
        "--hidden-import=datetime",
        "--hidden-import=io",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=time",
        "--hidden-import=re",
        
        # === COLLECTER LES DONNÉES ===
        "--collect-data=customtkinter",
        "--collect-all=customtkinter",
        "--collect-all=PIL",
        
        # === OPTIONS DE SÉCURITÉ ===
        "--noupx",  # Désactiver UPX (peut causer des problèmes avec antivirus)
        
        # Script principal
        script_path
    ]
    
    print("Commande:", " ".join(cmd))
    print()
    print("Construction en cours (peut prendre quelques minutes)...")
    print()
    
    # Exécuter PyInstaller
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        exe_path = os.path.join(os.path.dirname(__file__), "dist", "SmartARS.exe")
        print()
        print("=" * 60)
        print("SUCCES !")
        print("=" * 60)
        print()
        print(f"Exécutable créé : {exe_path}")
        print()
        print("Vous pouvez maintenant :")
        print("  1. Copier SmartARS.exe sur un partage réseau")
        print("  2. L'envoyer par email")
        print("  3. Le distribuer à vos collègues")
        print()
        
        # Ouvrir le dossier dist
        os.startfile(os.path.join(os.path.dirname(__file__), "dist"))
    else:
        print()
        print("ERREUR: Erreur lors de la construction")
        print("Vérifiez les messages d'erreur ci-dessus")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())




