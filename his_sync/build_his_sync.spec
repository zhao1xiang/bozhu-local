# -*- mode: python ; coding: utf-8 -*-
"""
HIS 同步服务打包配置
打包命令：
D:\workpath\python3.7.9\Scripts\pyinstaller.exe --distpath his-sync-package --workpath temp-build his_sync\build_his_sync.spec
"""

import sys
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pyodbc',
        'yaml',
        'pyyaml',
        'uuid',
        'json',
        'signal',
        'contextlib',
        # 子模块显式引入
        'core.logger',
        'core.db_mssql',
        'core.db_sqlite',
        'core.health_check',
        'sync.patient_sync',
        'adapter.vegf_adapter',
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
    name='his_sync',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保留控制台窗口，方便查看日志
    icon=None,
)
