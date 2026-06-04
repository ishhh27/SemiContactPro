# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for SemiContact Pro
Build command:  pyinstaller SemiContactPro.spec
"""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        ('themes',   'themes'),
        ('ui',       'ui'),
        ('analysis', 'analysis'),
        ('graphs',   'graphs'),
        ('exports',  'exports'),
        ('utils',    'utils'),
        ('assets',   'assets'),
        ('data',     'data'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'numpy',
        'scipy',
        'scipy.stats',
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'PIL',
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
    name='SemiContactPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no console window in production
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # uncomment when icon is added
)
