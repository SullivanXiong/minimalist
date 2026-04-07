# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Minimalist desktop client."""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'supyx',
        'supyx.wxnavimgation',
        'websocket',
        'requests',
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
    name='Minimalist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/minimalist.icns' if sys.platform == 'darwin' else (
        'resources/minimalist.ico' if sys.platform == 'win32' else None
    ),
)

# macOS: create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Minimalist.app',
        icon='resources/minimalist.icns',
        bundle_identifier='com.sullivanxiong.minimalist',
        info_plist={
            'CFBundleShortVersionString': '0.1.0',
            'CFBundleVersion': '0.1.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15',
        },
    )
