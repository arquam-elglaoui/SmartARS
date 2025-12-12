# -*- coding: utf-8 -*-
"""
Script pour créer un package de distribution complet
====================================================
Crée un dossier avec l'exe + tous les fichiers nécessaires
"""

import os
import shutil
import sys

def creer_package():
    """Crée un package complet pour distribution."""
    
    print("=" * 60)
    print("   Création du package de distribution SmartARS")
    print("=" * 60)
    print()
    
    # Dossiers
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    package_dir = os.path.join(base_dir, "SmartARS_Package")
    
    # Créer le dossier package
    if os.path.exists(package_dir):
        print(f"⚠️  Suppression de l'ancien package : {package_dir}")
        shutil.rmtree(package_dir)
    
    os.makedirs(package_dir, exist_ok=True)
    print(f"✅ Dossier créé : {package_dir}")
    print()
    
    # 1. Copier l'exe
    exe_src = os.path.join(dist_dir, "SmartARS.exe")
    if not os.path.exists(exe_src):
        # Essayer avec le nom alternatif
        exe_src = os.path.join(dist_dir, "SmartARS_v1.0.exe")
    
    if os.path.exists(exe_src):
        exe_dst = os.path.join(package_dir, "SmartARS.exe")
        shutil.copy2(exe_src, exe_dst)
        print(f"✅ Exe copié : SmartARS.exe")
    else:
        print(f"❌ ERREUR : Exe introuvable dans {dist_dir}")
        print("   Lancez d'abord : python build_exe.py")
        return 1
    
    # 2. Copier le dossier regions (au cas où)
    regions_src = os.path.join(base_dir, "regions")
    regions_dst = os.path.join(package_dir, "regions")
    if os.path.exists(regions_src):
        shutil.copytree(regions_src, regions_dst)
        print(f"✅ Dossier regions copié")
    
    # 3. Copier config.py (au cas où)
    config_src = os.path.join(base_dir, "config.py")
    config_dst = os.path.join(package_dir, "config.py")
    if os.path.exists(config_src):
        shutil.copy2(config_src, config_dst)
        print(f"✅ config.py copié")
    
    # 4. Copier README.md
    readme_src = os.path.join(base_dir, "README.md")
    readme_dst = os.path.join(package_dir, "README.md")
    if os.path.exists(readme_src):
        shutil.copy2(readme_src, readme_dst)
        print(f"✅ README.md copié")
    
    # 5. Créer un fichier LISEZ_MOI.txt avec instructions
    instructions = """SMARTARS - Instructions d'installation
=====================================

1. INSTALLATION
   - Copiez TOUT le contenu de ce dossier où vous voulez
   - Pas besoin d'installer Python ou autre chose
   - Double-cliquez sur SmartARS.exe pour lancer

2. UTILISATION
   - L'interface graphique s'ouvre automatiquement
   - Choisissez les régions, mois et années
   - Cliquez sur "Lancer l'analyse"
   - Les résultats sont dans : Documents/SmartARS/

3. EN CAS DE PROBLÈME
   - Si certaines régions ne fonctionnent pas :
     * Vérifiez votre connexion internet
     * Vérifiez que Windows Defender n'bloque pas l'exe
     * Essayez de lancer en "Exécuter en tant qu'administrateur"
   
   - Si l'exe ne démarre pas :
     * Vérifiez que le dossier "regions" est bien présent
     * Vérifiez que config.py est bien présent

4. CONTACT
   - En cas de problème persistant, contactez le développeur
   - Fournissez les logs dans Documents/SmartARS/results/.../log_*.txt

Bon usage !
"""
    
    readme_dst = os.path.join(package_dir, "LISEZ_MOI.txt")
    with open(readme_dst, "w", encoding="utf-8") as f:
        f.write(instructions)
    print(f"✅ LISEZ_MOI.txt créé")
    
    print()
    print("=" * 60)
    print("✅ PACKAGE CRÉÉ AVEC SUCCÈS !")
    print("=" * 60)
    print()
    print(f"📦 Dossier : {package_dir}")
    print()
    print("📋 Contenu du package :")
    print("   - SmartARS.exe (exécutable principal)")
    print("   - regions/ (dossier avec tous les extracteurs)")
    print("   - config.py (configuration)")
    print("   - README.md (documentation)")
    print("   - LISEZ_MOI.txt (instructions)")
    print()
    print("🚀 Pour distribuer :")
    print("   1. Compressez le dossier SmartARS_Package en ZIP")
    print("   2. Envoyez le ZIP à vos collègues")
    print("   3. Ils décompressent et lancent SmartARS.exe")
    print()
    
    # Ouvrir le dossier
    os.startfile(package_dir)
    
    return 0


if __name__ == "__main__":
    sys.exit(creer_package())




