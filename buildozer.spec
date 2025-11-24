[app]

# --- INFO O APLIKÁCII ---
title = Hlasenia A
package.name = hlaseniaa
package.domain = org.example

# --- SÚBORY A KÓD ---
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,ogg,ttf,zip,json

version = 1.0

# --- KIVY A ZÁVISLOSTI ---
requirements = python3,kivy==2.3.0,plyer

# --- ORIENTÁCIA ---
orientation = portrait
fullscreen = 1

# --- ANDROID NASTAVENIA ---
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2

android.bootstrap = sdl2



# sdkmanager nájde buildozer automaticky
android.accept_sdk_license = True

# --- OSTATNÉ ---
[buildozer]
log_level = 2

warn_on_root = 0
