# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['TriviaRoyale.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),  # assets directory
        ('.env', '.'),  # Add this line to include .env file
    ],
    hiddenimports=[
        'google.generativeai',
        'mistralai',
        'pyttsx3.drivers',
        'pyttsx3.drivers.nsss',  # for macOS
        'pyttsx3.drivers.sapi5',  # for Windows
        'pyttsx3.drivers.espeak'  # for Linux
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
    name='TriviaRoyale',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep True for debugging during development
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None
)

# For macOS, create an app bundle
app = BUNDLE(
    exe,
    name='TriviaRoyale.app',
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    bundle_identifier='com.trivia.royale'
)
