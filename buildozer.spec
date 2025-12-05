[app]
title = MovieT
package.name = moviet
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json,xml,webp,mp3,wav,ogg,mp4

version = 1.0

orientation = portrait
fullscreen = 0

# Všetky závislosti – fungujú s moderným NDK
requirements = python3,kivy==2.3.0,git+https://github.com/kivymd/KivyMD.git@master,materialyoucolor,asynckivy,asyncgui,plyer,jnius,pillow,requests,lxml,beautifulsoup4,colorthief

# ANDROID – moderné a plne kompatibilné nastavenia (2025)
android.api = 34
android.minapi = 21

# KĽÚČOVÁ ZMENA: používame nový NDK (GitHub Actions má práve tento)
android.ndk = 27.3.13750724
android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a
android.build_tools_version = 34.0.0

# ANDROID TV (Leanback) – správne a otestované
android.extra_features = android.software.leanback
android.manifest.activity_categories = android.intent.category.LAUNCHER, android.intent.category.LEANBACK_LAUNCHER

# Oprávnenia a kompatibilita so súbormi
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE
android.old_perrmissions = True                  # nutné pre zápis na starších aj novších zariadeniach

android.enable_androidx = True
android.logcat_filters = *:S python:D

# Správne miesto pre bootstrap (android.bootstrap je už dávno zastaraný)
p4a.bootstrap = sdl2
p4a.branch = master

# Automatické prijatie všetkých licencií (GitHub Actions to potrebuje)
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True
android.accept_google_androidx_license = True

[buildozer]
log_level = 2
warn_on_root = 1
