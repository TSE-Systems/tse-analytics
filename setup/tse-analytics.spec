# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

pathex = os.path.abspath(os.path.join(SPECPATH, '..'))

datas = [
    ('../docs', 'docs'),
    ('../tse_analytics/styles', 'styles'),
    ('../tse_analytics/resources_rc.py', '.'),
    ('../tse_analytics/views/about/*.md', 'tse_analytics/views/about'),
    ('../tse_analytics/views/pipeline/hotkey_functions.py', 'tse_analytics/views/pipeline'),
]

datas += copy_metadata('numpy')
datas += copy_metadata('connectorx')
datas += copy_metadata('great-tables')
datas += collect_data_files('faicons')

hiddenimports = ["umap"]

a = Analysis(
    ['../tse_analytics/main.py'],
    pathex=[pathex],
    binaries=[('../.venv/Scripts/python.exe', '.'),],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['setup/hooks'],
    hooksconfig={
        'matplotlib': {
            'backends': ['QtAgg', 'SVG', 'PDF'],
        },
    },
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tse-analytics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='../resources/icons/app.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='tse-analytics'
)

app = BUNDLE(
    coll,
    name='tse-analytics.app',
    icon='../resources/icons/app.ico',
    bundle_identifier=None
)
