# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('single.py', '.'),
        ('load_plots.py', '.'),
        ('add_roi.py', '.'),
        ('periodic_table.py', '.'),
        ('analyse.py', '.'),
        ('PDA.py', '.'),
        ('batch.py', '.'),
        ('stitch.py', '.'),
        ('main.ui', '.'),
        ('single.ui', '.'),
        ('add_roi.ui', '.'),
        ('periodic_table.ui', '.'),
        ('analyse.ui', '.'),
        ('batch.ui', '.'),
        ('stitch.ui', '.'),
        ('icon.png', '.'),
        ('_dante_Ecallibration.mat', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5',
        'PySide2',
        'PySide5',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PolyX-XRF-Data-Analyser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PolyX-XRF-Data-Analyser',
)
