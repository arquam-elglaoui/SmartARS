# -*- coding: utf-8 -*-
"""
SmartARS - Interface Graphique
==============================
Application de veille réglementaire pour les autorisations EML
"""

import datetime
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MOIS_FR
from regions import EXTRACTEURS
from utils import MOIS_NOMS, normaliser_mois

# === FORCER L'IMPORT DE TOUTES LES RÉGIONS (pour PyInstaller) ===
# Cela garantit que tous les modules sont embarqués dans l'exe
try:
    import regions.auvergne_rhone_alpes
    import regions.bourgogne_franche_comte
    import regions.bretagne
    import regions.centre_val_de_loire
    import regions.corse
    import regions.grand_est
    import regions.guadeloupe
    import regions.guyane
    import regions.hauts_de_france
    import regions.ile_de_france
    import regions.martinique
    import regions.normandie
    import regions.nouvelle_aquitaine
    import regions.occitanie
    import regions.pays_de_la_loire
    import regions.provence_alpes_cote_azur
    import regions.reunion
except ImportError:
    # En cas d'erreur, on continue quand même
    pass

# Configuration de l'apparence
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")

# Constantes
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "SmartARS")
HISTORIQUE_EXCEL = os.path.join(BASE_DIR, "SmartARS_Historique.xlsx")


class SmartARSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("🏥 SmartARS - Veille Réglementaire EML")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Variables
        self.mois_vars = {}
        self.region_vars = {}
        self.is_running = False
        self.should_stop = False
        self.log_queue = queue.Queue()
        self.analysis_thread = None
        
        # Créer l'interface
        self.create_widgets()
        
        # Vérifier la queue de logs périodiquement
        self.after(100, self.process_log_queue)
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        
        # === Frame principal avec grid ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # === En-tête ===
        self.create_header()
        
        # === Section Sélection (Mois/Année) ===
        self.create_selection_frame()
        
        # === Section Régions ===
        self.create_regions_frame()
        
        # === Zone de log ===
        self.create_log_frame()
        
        # === Boutons d'action ===
        self.create_action_buttons()
    
    def create_header(self):
        """Crée l'en-tête avec le titre."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Titre principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="🏥 SmartARS",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title_label.pack()
        
        # Sous-titre
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Robot de Veille Réglementaire - Autorisations d'Équipements d'Imagerie Médicale",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack()
    
    def create_selection_frame(self):
        """Crée la section de sélection mois/année."""
        selection_frame = ctk.CTkFrame(self)
        selection_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        selection_frame.grid_columnconfigure((0, 1), weight=1)
        
        # === Colonne Mois ===
        mois_frame = ctk.CTkFrame(selection_frame)
        mois_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        mois_label = ctk.CTkLabel(
            mois_frame,
            text="📅 Mois (sélection multiple)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        mois_label.pack(pady=(10, 5))
        
        # Boutons Tous/Aucun pour mois
        mois_btn_frame = ctk.CTkFrame(mois_frame, fg_color="transparent")
        mois_btn_frame.pack(fill="x", padx=10)
        
        ctk.CTkButton(
            mois_btn_frame,
            text="Tous",
            width=60,
            height=25,
            command=lambda: self.select_all_mois(True)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            mois_btn_frame,
            text="Aucun",
            width=60,
            height=25,
            command=lambda: self.select_all_mois(False)
        ).pack(side="left", padx=2)
        
        # Grille des mois
        mois_grid = ctk.CTkFrame(mois_frame, fg_color="transparent")
        mois_grid.pack(fill="both", expand=True, padx=10, pady=5)
        
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                     "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        
        for i, mois in enumerate(mois_noms):
            var = ctk.BooleanVar(value=(i+1 == datetime.datetime.now().month))
            self.mois_vars[i+1] = var
            
            cb = ctk.CTkCheckBox(
                mois_grid,
                text=mois,
                variable=var,
                width=100
            )
            cb.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
        
        # === Colonne Année ===
        annee_frame = ctk.CTkFrame(selection_frame)
        annee_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        annee_label = ctk.CTkLabel(
            annee_frame,
            text="📆 Année",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        annee_label.pack(pady=(10, 5))
        
        current_year = datetime.datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 2)]
        
        self.annee_var = ctk.StringVar(value=str(current_year))
        self.annee_menu = ctk.CTkOptionMenu(
            annee_frame,
            values=years,
            variable=self.annee_var,
            width=200,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.annee_menu.pack(pady=10)
        
        # Info
        info_label = ctk.CTkLabel(
            annee_frame,
            text="💡 Astuce: Vous pouvez sélectionner\nplusieurs mois à la fois",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=10)
    
    def create_regions_frame(self):
        """Crée la section de sélection des régions."""
        regions_frame = ctk.CTkFrame(self)
        regions_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # En-tête régions
        header_frame = ctk.CTkFrame(regions_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        regions_label = ctk.CTkLabel(
            header_frame,
            text="🗺️ Régions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        regions_label.pack(side="left")
        
        # Boutons Toutes/Aucune
        ctk.CTkButton(
            header_frame,
            text="Toutes",
            width=70,
            height=25,
            command=lambda: self.select_all_regions(True)
        ).pack(side="right", padx=2)
        
        ctk.CTkButton(
            header_frame,
            text="Aucune",
            width=70,
            height=25,
            command=lambda: self.select_all_regions(False)
        ).pack(side="right", padx=2)
        
        # Grille des régions
        regions_grid = ctk.CTkFrame(regions_frame, fg_color="transparent")
        regions_grid.pack(fill="both", expand=True, padx=10, pady=5)
        
        regions_list = sorted(EXTRACTEURS.keys())
        
        # Affichage des noms propres
        noms_propres = {
            "auvergne-rhone-alpes": "Auvergne-Rhône-Alpes",
            "bourgogne-franche-comte": "Bourgogne-Franche-Comté",
            "bretagne": "Bretagne",
            "centre-val-de-loire": "Centre-Val de Loire",
            "corse": "Corse",
            "grand-est": "Grand Est",
            "guadeloupe": "Guadeloupe",
            "guyane": "Guyane",
            "hauts-de-france": "Hauts-de-France",
            "ile-de-france": "Île-de-France",
            "martinique": "Martinique",
            "normandie": "Normandie",
            "nouvelle-aquitaine": "Nouvelle-Aquitaine",
            "occitanie": "Occitanie",
            "pays-de-la-loire": "Pays de la Loire",
            "paca": "PACA",
            "reunion": "La Réunion",
        }
        
        for i, region in enumerate(regions_list):
            var = ctk.BooleanVar(value=True)
            self.region_vars[region] = var
            
            nom_affiche = noms_propres.get(region, region.replace("-", " ").title())
            
            cb = ctk.CTkCheckBox(
                regions_grid,
                text=nom_affiche,
                variable=var,
                width=180
            )
            cb.grid(row=i//4, column=i%4, sticky="w", padx=5, pady=2)
    
    def create_log_frame(self):
        """Crée la zone de log."""
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="📋 Progression",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Zone de texte pour les logs
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(log_frame)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
    
    def create_action_buttons(self):
        """Crée les boutons d'action."""
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Bouton Lancer
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 Lancer l'analyse",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self.start_analysis
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Bouton Arrêter (initialement caché)
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️ Arrêter la recherche",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="red",
            hover_color="darkred",
            command=self.stop_analysis
        )
        # Ne pas pack pour l'instant, sera affiché pendant l'analyse
        
        # Bouton Ouvrir résultats
        self.results_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Ouvrir les résultats",
            font=ctk.CTkFont(size=16),
            height=45,
            fg_color="gray",
            command=self.open_results
        )
        self.results_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Bouton Ouvrir Excel
        self.excel_btn = ctk.CTkButton(
            btn_frame,
            text="📊 Ouvrir Excel",
            font=ctk.CTkFont(size=16),
            height=45,
            fg_color="green",
            command=self.open_excel
        )
        self.excel_btn.pack(side="left", expand=True, fill="x", padx=5)
    
    def select_all_mois(self, value):
        """Sélectionne ou désélectionne tous les mois."""
        for var in self.mois_vars.values():
            var.set(value)
    
    def select_all_regions(self, value):
        """Sélectionne ou désélectionne toutes les régions."""
        for var in self.region_vars.values():
            var.set(value)
    
    def log(self, message):
        """Ajoute un message au log (thread-safe)."""
        self.log_queue.put(message)
    
    def process_log_queue(self):
        """Traite les messages de log en attente."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert("end", message + "\n")
                self.log_text.see("end")
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)
    
    def start_analysis(self):
        """Lance l'analyse dans un thread séparé."""
        if self.is_running:
            messagebox.showwarning("En cours", "Une analyse est déjà en cours !")
            return
        
        # Récupérer les sélections
        mois_selectionnes = [m for m, var in self.mois_vars.items() if var.get()]
        regions_selectionnees = [r for r, var in self.region_vars.items() if var.get()]
        annee = int(self.annee_var.get())
        
        if not mois_selectionnes:
            messagebox.showwarning("Sélection", "Veuillez sélectionner au moins un mois.")
            return
        
        if not regions_selectionnees:
            messagebox.showwarning("Sélection", "Veuillez sélectionner au moins une région.")
            return
        
        # Warning pour La Réunion si mois en cours
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        if "reunion" in regions_selectionnees:
            for mois in mois_selectionnes:
                if annee == current_year and mois >= current_month:
                    messagebox.showinfo(
                        "⚠️ Info La Réunion",
                        "La Réunion publie les RAA du mois le 1er ou 2 du mois suivant.\n\n"
                        f"Les RAA de {MOIS_NOMS.get(mois, str(mois))} {annee} ne seront disponibles "
                        f"qu'à partir du 1er {MOIS_NOMS.get((mois % 12) + 1, 'janvier')} {annee if mois < 12 else annee + 1}."
                    )
                    break
        
        # Confirmation
        mois_noms = [MOIS_NOMS.get(m, str(m)) for m in mois_selectionnes]
        msg = f"Lancer l'analyse pour :\n\n"
        msg += f"📅 Mois : {', '.join(mois_noms)}\n"
        msg += f"📆 Année : {annee}\n"
        msg += f"🗺️ Régions : {len(regions_selectionnees)} sélectionnée(s)\n\n"
        msg += "Continuer ?"
        
        if not messagebox.askyesno("Confirmation", msg):
            return
        
        # Nettoyer le log
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)
        
        # Réinitialiser le flag d'arrêt
        self.should_stop = False
        
        # Cacher le bouton Lancer et afficher le bouton Arrêter
        self.is_running = True
        self.start_btn.pack_forget()  # Cacher le bouton Lancer
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=5)  # Afficher le bouton Arrêter
        
        # Lancer dans un thread
        self.analysis_thread = threading.Thread(
            target=self.run_analysis,
            args=(mois_selectionnes, annee, regions_selectionnees)
        )
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop_analysis(self):
        """Arrête l'analyse en cours."""
        if not self.is_running:
            return
        
        if messagebox.askyesno("Arrêter", "Voulez-vous vraiment arrêter l'analyse en cours ?"):
            self.should_stop = True
            self.log("\n⚠️ Arrêt demandé... Fin de l'analyse en cours...")
    
    def run_analysis(self, mois_list, annee, regions):
        """Exécute l'analyse (dans un thread séparé)."""
        try:
            # Import ici pour éviter les imports circulaires
            from main import run_bot
            
            total_combos = len(mois_list)
            
            for i, mois_num in enumerate(mois_list):
                # Vérifier si l'arrêt a été demandé
                if self.should_stop:
                    self.log(f"\n{'='*50}")
                    self.log("⏹️ ANALYSE ARRÊTÉE PAR L'UTILISATEUR")
                    self.log(f"{'='*50}")
                    break
                
                mois_nom = MOIS_NOMS.get(mois_num, str(mois_num))
                self.log(f"\n{'='*50}")
                self.log(f"📅 Analyse: {mois_nom} {annee}")
                self.log(f"{'='*50}\n")
                
                # Mettre à jour la progression
                progress = (i + 0.5) / total_combos
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                
                # Rediriger la sortie standard
                import io
                from contextlib import redirect_stdout
                
                # Capturer les prints
                old_stdout = sys.stdout
                sys.stdout = OutputRedirector(self.log)
                
                try:
                    # Passer le callback should_stop à run_bot
                    run_bot(mois_num, annee, regions, should_stop=lambda: self.should_stop)
                except Exception as e:
                    if not self.should_stop:
                        self.log(f"❌ Erreur: {str(e)}")
                finally:
                    sys.stdout = old_stdout
                
                # Vérifier à nouveau après chaque mois
                if self.should_stop:
                    self.log(f"\n{'='*50}")
                    self.log("⏹️ ANALYSE ARRÊTÉE PAR L'UTILISATEUR")
                    self.log(f"{'='*50}")
                    break
                
                # Progression
                progress = (i + 1) / total_combos
                self.after(0, lambda p=progress: self.progress_bar.set(p))
            
            if not self.should_stop:
                self.log(f"\n{'='*50}")
                self.log("✅ ANALYSE TERMINÉE !")
                self.log(f"{'='*50}")
                self.log(f"\n📂 Résultats: {BASE_DIR}")
                self.log(f"📊 Excel: {HISTORIQUE_EXCEL}")
                
                # Notification
                self.after(0, lambda: messagebox.showinfo(
                    "Terminé",
                    f"Analyse terminée !\n\nRésultats dans :\n{BASE_DIR}"
                ))
            else:
                self.after(0, lambda: messagebox.showinfo(
                    "Arrêté",
                    "L'analyse a été arrêtée par l'utilisateur."
                ))
            
        except Exception as e:
            if not self.should_stop:
                self.log(f"\n❌ ERREUR: {str(e)}")
                self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        
        finally:
            # Réafficher le bouton Lancer et cacher le bouton Arrêter
            self.is_running = False
            self.should_stop = False
            self.after(0, lambda: self.stop_btn.pack_forget())  # Cacher le bouton Arrêter
            self.after(0, lambda: self.start_btn.pack(side="left", expand=True, fill="x", padx=5))  # Réafficher le bouton Lancer
    
    def open_results(self):
        """Ouvre le dossier des résultats."""
        if os.path.exists(BASE_DIR):
            os.startfile(BASE_DIR)
        else:
            messagebox.showinfo("Info", f"Le dossier n'existe pas encore.\n{BASE_DIR}")
    
    def open_excel(self):
        """Ouvre le fichier Excel historique."""
        if os.path.exists(HISTORIQUE_EXCEL):
            os.startfile(HISTORIQUE_EXCEL)
        else:
            messagebox.showinfo("Info", "Aucun fichier Excel n'a encore été généré.")


class OutputRedirector:
    """Redirige stdout vers la fonction de log."""
    def __init__(self, log_func):
        self.log_func = log_func
        self.buffer = ""
    
    def write(self, text):
        if text.strip():
            self.log_func(text.rstrip())
    
    def flush(self):
        pass


def main():
    app = SmartARSApp()
    app.mainloop()


if __name__ == "__main__":
    main()

