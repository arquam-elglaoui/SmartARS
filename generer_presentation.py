# -*- coding: utf-8 -*-
"""
Générateur de présentation PowerPoint pour SmartARS
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# Couleurs du thème
BLEU_FONCE = RGBColor(0, 51, 102)      # Titre principal
BLEU_CLAIR = RGBColor(0, 112, 192)     # Accents
VERT = RGBColor(0, 176, 80)            # Succès
ORANGE = RGBColor(255, 153, 0)         # Attention
GRIS = RGBColor(89, 89, 89)            # Texte secondaire


def ajouter_titre_slide(prs, titre, sous_titre=None):
    """Ajoute une slide de titre."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Rectangle de fond en haut
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.33), Inches(2.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLEU_FONCE
    shape.line.fill.background()
    
    # Titre
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(12), Inches(1))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = titre
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER
    
    # Sous-titre
    if sous_titre:
        txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(12), Inches(0.6))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = sous_titre
        p2.font.size = Pt(24)
        p2.font.color.rgb = RGBColor(200, 200, 200)
        p2.alignment = PP_ALIGN.CENTER
    
    return slide


def ajouter_slide_contenu(prs, titre, contenu_liste, icones=None):
    """Ajoute une slide avec titre et liste à puces."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    # Barre de titre
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.33), Inches(1.2))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLEU_FONCE
    shape.line.fill.background()
    
    # Titre
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.7))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = titre
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    # Contenu
    txBox2 = slide.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(11.5), Inches(5.5))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    
    for i, item in enumerate(contenu_liste):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        
        icone = icones[i] if icones and i < len(icones) else "•"
        p.text = f"{icone}  {item}"
        p.font.size = Pt(22)
        p.font.color.rgb = GRIS
        p.space_after = Pt(14)
    
    return slide


def ajouter_slide_tableau(prs, titre, headers, rows):
    """Ajoute une slide avec un tableau."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    # Barre de titre
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.33), Inches(1.2))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLEU_FONCE
    shape.line.fill.background()
    
    # Titre
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.7))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = titre
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    # Tableau
    cols = len(headers)
    table_rows = len(rows) + 1
    
    x, y = Inches(0.5), Inches(1.6)
    cx, cy = Inches(12.3), Inches(0.6 * table_rows)
    
    table = slide.shapes.add_table(table_rows, cols, x, y, cx, cy).table
    
    # En-têtes
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = BLEU_CLAIR
        para = cell.text_frame.paragraphs[0]
        para.font.bold = True
        para.font.size = Pt(16)
        para.font.color.rgb = RGBColor(255, 255, 255)
        para.alignment = PP_ALIGN.CENTER
    
    # Données
    for row_idx, row in enumerate(rows):
        for col_idx, cell_text in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = str(cell_text)
            para = cell.text_frame.paragraphs[0]
            para.font.size = Pt(14)
            para.alignment = PP_ALIGN.CENTER
    
    return slide


def ajouter_slide_flux(prs):
    """Ajoute une slide montrant le flux de travail."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    # Barre de titre
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.33), Inches(1.2))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLEU_FONCE
    shape.line.fill.background()
    
    # Titre
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.7))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "Flux de fonctionnement"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    # Étapes du flux
    etapes = [
        ("1", "ENTRÉE", "Mois + Année + Régions", BLEU_CLAIR),
        ("2", "SCRAPING", "17 préfectures", BLEU_CLAIR),
        ("3", "ANALYSE", "Recherche mots-clés EML", BLEU_CLAIR),
        ("4", "EXTRACTION", "PDFs + Excel", VERT),
    ]
    
    y_start = 1.8
    box_width = 2.8
    spacing = 0.3
    
    for i, (num, titre, desc, color) in enumerate(etapes):
        x = 0.5 + i * (box_width + spacing)
        
        # Boîte
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y_start), Inches(box_width), Inches(1.8))
        box.fill.solid()
        box.fill.fore_color.rgb = color
        box.line.fill.background()
        
        # Numéro
        txNum = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y_start + 0.1), Inches(0.5), Inches(0.5))
        pNum = txNum.text_frame.paragraphs[0]
        pNum.text = num
        pNum.font.size = Pt(28)
        pNum.font.bold = True
        pNum.font.color.rgb = RGBColor(255, 255, 255)
        
        # Titre étape
        txTitre = slide.shapes.add_textbox(Inches(x), Inches(y_start + 0.5), Inches(box_width), Inches(0.5))
        pTitre = txTitre.text_frame.paragraphs[0]
        pTitre.text = titre
        pTitre.font.size = Pt(18)
        pTitre.font.bold = True
        pTitre.font.color.rgb = RGBColor(255, 255, 255)
        pTitre.alignment = PP_ALIGN.CENTER
        
        # Description
        txDesc = slide.shapes.add_textbox(Inches(x), Inches(y_start + 1.0), Inches(box_width), Inches(0.6))
        pDesc = txDesc.text_frame.paragraphs[0]
        pDesc.text = desc
        pDesc.font.size = Pt(14)
        pDesc.font.color.rgb = RGBColor(255, 255, 255)
        pDesc.alignment = PP_ALIGN.CENTER
        
        # Flèche (sauf dernière)
        if i < len(etapes) - 1:
            arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, 
                                           Inches(x + box_width + 0.05), 
                                           Inches(y_start + 0.7), 
                                           Inches(0.2), Inches(0.4))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = GRIS
            arrow.line.fill.background()
    
    # Section livrables en bas
    y_livrable = 4.2
    
    # PDF
    pdf_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(y_livrable), Inches(5), Inches(2))
    pdf_box.fill.solid()
    pdf_box.fill.fore_color.rgb = RGBColor(240, 240, 240)
    pdf_box.line.color.rgb = BLEU_CLAIR
    
    txPdf = slide.shapes.add_textbox(Inches(1.2), Inches(y_livrable + 0.2), Inches(4.6), Inches(1.8))
    tfPdf = txPdf.text_frame
    tfPdf.word_wrap = True
    p1 = tfPdf.paragraphs[0]
    p1.text = "📄 PDFs Extraits"
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = BLEU_FONCE
    
    p2 = tfPdf.add_paragraph()
    p2.text = "• 1 PDF par RAA pertinent"
    p2.font.size = Pt(14)
    p2.font.color.rgb = GRIS
    
    p3 = tfPdf.add_paragraph()
    p3.text = "• Pages 1-3 (couverture + sommaire)"
    p3.font.size = Pt(14)
    p3.font.color.rgb = GRIS
    
    p4 = tfPdf.add_paragraph()
    p4.text = "• + Pages d'autorisations"
    p4.font.size = Pt(14)
    p4.font.color.rgb = GRIS
    
    # Excel
    excel_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7), Inches(y_livrable), Inches(5), Inches(2))
    excel_box.fill.solid()
    excel_box.fill.fore_color.rgb = RGBColor(240, 240, 240)
    excel_box.line.color.rgb = VERT
    
    txExcel = slide.shapes.add_textbox(Inches(7.2), Inches(y_livrable + 0.2), Inches(4.6), Inches(1.8))
    tfExcel = txExcel.text_frame
    tfExcel.word_wrap = True
    e1 = tfExcel.paragraphs[0]
    e1.text = "📊 Excel Historique"
    e1.font.size = Pt(20)
    e1.font.bold = True
    e1.font.color.rgb = BLEU_FONCE
    
    e2 = tfExcel.add_paragraph()
    e2.text = "• Fichier unique cumulatif"
    e2.font.size = Pt(14)
    e2.font.color.rgb = GRIS
    
    e3 = tfExcel.add_paragraph()
    e3.text = "• 1 feuille par mois/année"
    e3.font.size = Pt(14)
    e3.font.color.rgb = GRIS
    
    e4 = tfExcel.add_paragraph()
    e4.text = "• Anti-doublons intégré"
    e4.font.size = Pt(14)
    e4.font.color.rgb = GRIS
    
    return slide


def generer_presentation():
    """Génère la présentation complète."""
    prs = Presentation()
    prs.slide_width = Inches(13.33)  # 16:9
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Titre
    ajouter_titre_slide(prs, "🏥 SmartARS", "Robot de Veille Réglementaire - Autorisations EML")
    
    # Slide 2: Contexte
    ajouter_slide_contenu(prs, "📋 Contexte & Objectif", [
        "Les autorisations d'Équipements d'Imagerie Médicale Lourde (EML) sont publiées dans les RAA des préfectures",
        "17 préfectures régionales à surveiller (métropole + DOM)",
        "Publications mensuelles, formats PDF variables",
        "Objectif : Automatiser la veille et centraliser les informations"
    ], ["📍", "🗺️", "📄", "🎯"])
    
    # Slide 3: Équipements ciblés
    ajouter_slide_tableau(prs, "🔍 Équipements recherchés", 
        ["Mot-clé", "Équipement"],
        [
            ["IRM", "Imagerie par Résonance Magnétique"],
            ["Scanner / Scanographe", "Tomodensitométrie"],
            ["TEP", "Tomographie par Émission de Positons"],
            ["Gamma caméra", "Caméra à scintillation"],
            ["Radiologie", "Équipements radiologiques lourds"],
            ["Imagerie en coupes", "Modalités d'imagerie en coupes"],
        ])
    
    # Slide 4: Flux
    ajouter_slide_flux(prs)
    
    # Slide 5: Régions couvertes
    ajouter_slide_contenu(prs, "🗺️ Couverture nationale", [
        "13 régions métropolitaines",
        "4 régions d'Outre-mer (Guadeloupe, Guyane, Martinique, Réunion)",
        "Sources : Sites officiels des préfectures de région",
        "Adaptation automatique aux différents formats de sites web"
    ], ["🇫🇷", "🌴", "🌐", "⚙️"])
    
    # Slide 6: Fonctionnalités
    ajouter_slide_contenu(prs, "⚡ Fonctionnalités clés", [
        "Analyse multi-mois et multi-années en une commande",
        "Filtrage strict par date (pas de faux positifs)",
        "Système anti-doublons avec cache intelligent",
        "Retry automatique (3 tentatives) en cas d'erreur réseau",
        "Logs détaillés pour traçabilité complète"
    ], ["📅", "🎯", "🔄", "🔁", "📝"])
    
    # Slide 7: Comparaison Avant/Après
    ajouter_slide_tableau(prs, "📈 Gain de productivité",
        ["", "Avant (manuel)", "Après (SmartARS)"],
        [
            ["Temps / mois", "2-3 heures", "~10 minutes"],
            ["Risque d'oubli", "Élevé", "Aucun"],
            ["Historique", "Non centralisé", "Excel cumulatif"],
            ["Traçabilité", "Aucune", "Logs complets"],
        ])
    
    # Slide 8: Utilisation
    ajouter_slide_contenu(prs, "💻 Utilisation simple", [
        "Mode interactif : python main.py (menu guidé)",
        "Ligne de commande : python main.py 11 2025",
        "Multi-mois : python main.py 10,11,12 2025",
        "Multi-années : python main.py 11 2024,2025",
        "Régions spécifiques : python main.py 11 2025 bretagne paca"
    ], ["🖱️", "⌨️", "📅", "📆", "🗺️"])
    
    # Slide 9: Résultats
    ajouter_slide_contenu(prs, "📂 Structure des résultats", [
        "Documents/SmartARS/SmartARS_Historique.xlsx → Fichier maître",
        "Documents/SmartARS/results/{année}_{mois}/{région}/ → PDFs extraits",
        "Chaque PDF extrait = Couverture + Sommaire + Pages pertinentes",
        "Nom du fichier = Nom RAA original + \"_EXTRACT.pdf\""
    ], ["📊", "📁", "📄", "🏷️"])
    
    # Slide 10: Conclusion
    slide = ajouter_titre_slide(prs, "✅ SmartARS", "Veille réglementaire automatisée et fiable")
    
    # Ajouter les points clés en bas
    txBox = slide.shapes.add_textbox(Inches(1), Inches(3.5), Inches(11), Inches(3))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    points = [
        "🚀  Gain de temps significatif",
        "🎯  Exhaustivité garantie sur 17 régions",
        "📊  Centralisation dans un fichier Excel unique",
        "🔄  Exécution programmable (automatisation possible)"
    ]
    
    for i, point in enumerate(points):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = point
        p.font.size = Pt(26)
        p.font.color.rgb = GRIS
        p.space_after = Pt(20)
        p.alignment = PP_ALIGN.CENTER
    
    # Sauvegarder
    output_path = os.path.join(os.path.expanduser("~"), "Documents", "SmartARS", "SmartARS_Presentation.pptx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    
    print(f"✅ Présentation générée : {output_path}")
    return output_path


if __name__ == "__main__":
    generer_presentation()

