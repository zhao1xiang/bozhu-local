# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# 构建 datas 列表 - 不包含前端文件，因为前端文件会单独放在 exe 同级目录
datas = [
    ('database.py', '.'),
    ('database_compatibility.py', '.'),
    ('security.py', '.'),
    ('models', 'models'),
    ('routers', 'routers'),
]

# 如果数据库文件存在，也包含它
if os.path.exists('database.db'):
    datas.insert(0, ('database.db', '.'))
    print(f"Including database: database.db")

a = Analysis(
    ['simple_web_server.py', 'main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
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
        'sqlite3',
        'shutil',
        'logging',
        'traceback',
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
    name='backend_server',
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