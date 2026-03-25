# -*- mode: python ; coding: utf-8 -*-
"""
SQL Server 检测工具打包配置
"""

block_cipher = None

a = Analysis(
    ['sql_test.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pymssql',
        'socket',
        'subprocess',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='sql_test',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=None,
)