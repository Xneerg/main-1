[app]
title = Hlasenia A
package.name = hlaseniaa
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json,xml,webp,mp3,wav,ogg,mp4

version = 1.0

# ICONY (ak nemáš, pokojne odstráň tieto dve)
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

orientation = portrait
fullscreen = 0

# -----------------------------------------
# ZÁVISLOSTI – KivyMD 2.0.1-dev !!!!! (master)
# -----------------------------------------
requirements = python3,kivy==2.3.0,https://github.com/kivymd/KivyMD/archive/master.zip,plyer

# -----------------------------------------
# ANDROID NASTAVENIA (kompatibilné s workflow)
# -----------------------------------------
android.api = 33
android.sdk = 33
android.minapi = 21

# presná NDK verzia pre p4a + KivyMD 2.x
android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2
android.build_tools_version = 33.0.2

# -----------------------------------------
# LICENCIE (pre GitHub Actions CI)
# -----------------------------------------
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True
android.accept_google_androidx_license = True

# -----------------------------------------
# POVOLENIA
# -----------------------------------------
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

# -----------------------------------------
# LOGY A ANDROIDX
# -----------------------------------------
android.enable_androidx = True
android.logcat_filters = *:S python:D
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
