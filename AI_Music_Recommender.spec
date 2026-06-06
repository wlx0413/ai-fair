# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path.cwd()

datas = [
    (str(project_root / "templates"), "templates"),
    (str(project_root / "static"), "static"),
    (str(project_root / "data"), "data"),
    (str(project_root / "models"), "models"),
    (str(project_root / "docs"), "docs"),
    (str(project_root / "README.md"), "."),
    (str(project_root / "TEMPLATE_LICENSE.md"), "."),
]

hiddenimports = []
hiddenimports += collect_submodules("lightfm")
hiddenimports += collect_submodules("webview")
hiddenimports += [
    "AppKit",
    "Cocoa",
    "Foundation",
    "Quartz",
    "Security",
    "UniformTypeIdentifiers",
    "WebKit",
    "objc",
]

block_cipher = None

a = Analysis(
    ["mac_app_launcher.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "IPython",
        "matplotlib",
        "pyarrow",
        "pytest",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AI Music Recommender",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AI Music Recommender",
)

app = BUNDLE(
    coll,
    name="AI Music Recommender.app",
    icon=str(project_root / "mac_app_assets" / "AI_Music_Recommender.icns"),
    bundle_identifier="com.aifair.musicrecommender",
    info_plist={
        "CFBundleName": "AI Music Recommender",
        "CFBundleDisplayName": "AI Music Recommender",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "LSMinimumSystemVersion": "10.15.0",
        "NSHighResolutionCapable": True,
    },
)
