[app]
# (c) Hlasenia A – aplikácia s KivyMD 2.0.1-dev
title = Hlasenia A
package.name = hlaseniaa
package.domain = org.example

# Hlavný python súbor (ak sa volá inak ako main.py, zmeň)
# source.dir = .

# Ak máš main.py v podpriečinku, napr. src/main.py → source.dir = src

source.include_exts = py,png,jpg,kkv,atlas,ttf,txt,json,xml,webp,mp3,wav,ogg,mp4,m4a

version = 1.0
version.regex = .*
version.filename = %(source.dir)s/version.txt

# IKONA A OBRÁZKY
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/presplash.png

# ORIENTÁCIA A REŽIM
orientation = portrait
fullscreen = 0
osx.python_version = 3
osx.kivy_version = 2.3.0

# ZÁVISLOSTI – TU JE TO DÔLEŽITÉ
# KivyMD 2.0.1-dev (master) + potrebné balíčky
requirements = python3, \
    kivy==2.3.0, \
    https://github.com/kivymd/KivyMD/archive/master.zip, \
    plyer, \
    materialyoucolor, \
    certifi

# ANDROID NASTAVENIA
android.api = 34                    # najnovšie stabilné (november 2025)
android.minapi = 21
android.sdk = 34
android.ndk = 25b                   # KivyMD 2.0+ vyžaduje NDK 25
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2
android.build_tools_version = 34.0.0

# Automatické prijatie všetkých licencií (GitHub Actions)
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True
android.accept_google_androidx_license = True

# POVOLENIA
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

# LOGOVANIE A LADENIE
log_level = 2
android.logcat_filters = *:S python:D

# OSTATNÉ
p4a.branch = master
android.enable_androidx = True

[buildozer]
# Viac výstupu pri builde
log_level = 2
warn_on_root = 1
