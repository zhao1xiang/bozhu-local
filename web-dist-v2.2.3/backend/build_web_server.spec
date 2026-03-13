# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['web_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含所有必要的数据文件
        ('database.db', '.'),
        ('../frontend/dist', 'frontend'),  # 前端构建文件
        ('main_web.py', '.'),  # Web版本的主应用文件
        ('main.py', '.'),      # 原始主应用文件
        ('database.py', '.'),
        ('security.py', '.'),
        ('models', 'models'),
        ('routers', 'routers'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'passlib.handlers.bcrypt',
        'sqlalchemy.sql.default_comparator',
        'webbrowser',
        'threading',
        'socket',
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.responses',
        'fastapi.middleware.cors',
        'sqlmodel',
        'pydantic',
        'starlette',
        'starlette.staticfiles',
        'starlette.responses',
        'starlette.middleware',
        'starlette.middleware.cors',
        'jose',
        'jose.jwt',
        'jose.exceptions',
        'python_jose',
        'python_jose.jwt',
        'python_jose.exceptions',
        'datetime',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='眼科注射预约系统-Web版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台，方便查看启动信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)