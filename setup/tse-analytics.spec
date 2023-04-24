# -*- mode: python -*-

import os

pathex = os.path.abspath(os.path.join(SPECPATH, '..'))

block_cipher = None


a = Analysis(['../tse_analytics/__main__.py'],
             pathex=[pathex],
             binaries=[],
             datas=[
                ('../tse_analytics/docs', 'docs'),
                ('../tse_analytics/resources_rc.py', '.')
             ],
             hiddenimports=[
                'pywt._extensions._cwt',
                'pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyside6',
                'pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyside6',
                'pyqtgraph.imageview.ImageViewTemplate_pyside6',
                'sklearn.metrics._pairwise_distances_reduction._datasets_pair',
                'sklearn.metrics._pairwise_distances_reduction._middle_term_computer',
             ],
             hookspath=['setup/hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='tse-analytics',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='..\\resources\\icons\\app.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='tse-analytics')

app = BUNDLE(coll,
             name='tse-analytics.app',
             icon='..\\resources\\icons\\app.icns',
             bundle_identifier=None)
