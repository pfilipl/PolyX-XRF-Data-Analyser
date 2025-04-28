# -*- mode: python ; coding: utf-8 -*-


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
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='PolyX Data Analyser',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PolyX Data Analyser',
)
