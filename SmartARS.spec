# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['regions', 'regions.__init__', 'regions.auvergne_rhone_alpes', 'regions.bourgogne_franche_comte', 'regions.bretagne', 'regions.centre_val_de_loire', 'regions.corse', 'regions.grand_est', 'regions.guadeloupe', 'regions.guyane', 'regions.hauts_de_france', 'regions.ile_de_france', 'regions.martinique', 'regions.normandie', 'regions.nouvelle_aquitaine', 'regions.occitanie', 'regions.pays_de_la_loire', 'regions.provence_alpes_cote_azur', 'regions.reunion', 'config', 'utils', 'main', 'customtkinter', 'PIL', 'PIL.Image', 'pandas', 'openpyxl', 'fitz', 'PyMuPDF', 'requests', 'bs4', 'beautifulsoup4', 'urllib3', 'logging', 'json', 'hashlib', 'datetime', 'io', 'os', 'sys', 'time', 're']
datas += collect_data_files('customtkinter')
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Program Files\\SmartARS\\smartars_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
