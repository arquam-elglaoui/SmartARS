import pandas as pd, glob, fitz, os, textwrap
excel=r'C:\Users\z00568tb\Documents\SmartARS\SmartARS_Historique.xlsx'
print('=== EXCEL ===')
try:
    xls=pd.ExcelFile(excel)
    print('Feuilles:', xls.sheet_names)
    for sheet in xls.sheet_names:
        df=pd.read_excel(xls, sheet_name=sheet)
        print(f"\n--- {sheet} ---")
        print('Lignes:', len(df), '| Colonnes:', list(df.columns))
        print(df.head(8).to_string(index=False))
except Exception as e:
    print('Erreur lecture Excel:', e)

print('\n=== PDF EXTRACTS ===')
pdf_paths=sorted(glob.glob(r'C:\Users\z00568tb\Documents\SmartARS\results\**\*_EXTRACT.pdf', recursive=True))
if not pdf_paths:
    print('Aucun PDF extrait trouvé')
for path in pdf_paths:
    try:
        doc=fitz.open(path)
        pages=len(doc)
        page_idx=max(0,pages-1)
        text=doc[page_idx].get_text()
        snippet='\n'.join(textwrap.wrap(text.strip().replace('\n',' '), 120))[:800]
        print(f"\n{os.path.basename(path)} | pages: {pages} | extrait page {page_idx+1}:")
        print(snippet if snippet else '[page vide]')
    except Exception as e:
        print(f"\n{os.path.basename(path)} | ERREUR: {e}")
