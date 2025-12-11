# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = []
datas += collect_data_files('customtkinter')


a = Analysis(
    ['C:\\Program Files\\SmartARS\\smartars_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['regions', 'regions.auvergne_rhone_alpes', 'regions.bourgogne_franche_comte', 'regions.bretagne', 'regions.centre_val_de_loire', 'regions.corse', 'regions.grand_est', 'regions.guadeloupe', 'regions.guyane', 'regions.hauts_de_france', 'regions.ile_de_france', 'regions.martinique', 'regions.normandie', 'regions.nouvelle_aquitaine', 'regions.occitanie', 'regions.pays_de_la_loire', 'regions.provence_alpes_cote_azur', 'regions.reunion', 'customtkinter', 'PIL', 'pandas', 'openpyxl', 'fitz', 'requests', 'bs4'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SmartARS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
