# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['sql_test_odbc.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['pyodbc', 'yaml'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='sql_test_odbc',
    debug=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
)
