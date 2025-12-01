# Konfiguračný súbor Buildozer.spec - konsolidovaná verzia s opravou KivyMD závislostí.

[app]
title = Hlasenia A
package.name = hlaseniaa
package.domain = org.example

source.dir = .
# ROZŠÍRENÉ PRÍPONY: Zahrnuté všetky vaše mediálne súbory
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json,xml,webp,mp3,wav,ogg,mp4

version = 1.0

orientation = portrait
fullscreen = 0

# -----------------------------------------------------
# KRITICKÁ ÚPRAVA ZÁVISLOSTÍ PRE KivyMD 2.x:
# Pridané 'materialyoucolor', 'asynckivy', 'asyncgui'
# -----------------------------------------------------
requirements = python3,kivy==2.3.0,git+https://github.com/kivymd/KivyMD.git@master,materialyoucolor,asynckivy,asyncgui,plyer,jnius,pillow

# -----------------------------------------------------
# ANDROID NASTAVENIA: Používajú sa moderné API levely (34)
# -----------------------------------------------------
android.api = 34          
android.sdk = 34           
android.minapi = 21

android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2
android.build_tools_version = 34.0.0 
android.add_build_tools = 34.0.0

# Automatické prijatie licenčných zmlúv (prevencia chýb počas buildu)
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True
android.accept_google_androidx_license = True

# POVOLENIA: Zahrnuté VIBRATE pre plyer a úložiská
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

android.enable_androidx = True
android.logcat_filters = *:S python:D
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
