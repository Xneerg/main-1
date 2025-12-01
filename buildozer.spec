[app]
title = Hlasenia A
package.name = hlaseniaa
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json,xml,webp,mp3,wav,ogg,mp4

version = 1.0

orientation = portrait
fullscreen = 0

# -----------------------------------------
# ZÁVISLOSTI – PRIDANÉ KRITICKÉ BALÍKY (jnius, pillow)
# -----------------------------------------
requirements = python3,kivy==2.3.0,https://github.com/kivymd/KivyMD/archive/master.zip,plyer,jnius,pillow

# -----------------------------------------
# ANDROID NASTAVENIA (Zvýšenie API pre novšie Androidy, ale stabilný NDK)
# -----------------------------------------
android.api = 34          
android.sdk = 34           
android.minapi = 21

android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2
android.build_tools_version = 34.0.0 

# -----------------------------------------
# RIEŠENIE LICENČNEJ CHYBY: Pridaná automatická akceptácia (ak už nebola)
# Kľúčové na vyriešenie "license is not accepted"
# -----------------------------------------
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True
android.accept_google_androidx_license = True

# -----------------------------------------
# PRIDANIE EXPLICITNEJ ZÁVISLOSTI NA BUILD-TOOLS
# Aj keď by to malo byť automatické, Buildozer to niekedy potrebuje.
# Týmto sa uistíme, že sa nástroje 34.0.0 stiahnu a nainštalujú.
# -----------------------------------------
android.add_build_tools = 34.0.0

# -----------------------------------------
# POVOLENIA (Android 10+ si vyžaduje ACCESS_FINE_LOCATION pre WRITE_EXTERNAL_STORAGE
#            pretože to už nie je považované za bezpečné povolenie)
# -----------------------------------------
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

# -----------------------------------------
# KIVY/P4A NASTAVENIA
# -----------------------------------------
android.enable_androidx = True
android.logcat_filters = *:S python:D
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1

