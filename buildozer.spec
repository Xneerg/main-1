[app]
# --- INFO O APLIKÁCII ---
title = Hlasenia A
package.name = hlaseniaa
package.domain = org.example

# --- KÓD A SÚBORY ---
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,xml,webp,mp3,wav

version = 1.0

# --- KIVY + KIVYMD DEV VERZIA ---
# POZOR: vetva "dev" NEEXISTUJE, musíme použiť master (obsahuje 2.0.1-dev)
requirements = python3, kivy==2.3.0, kivymd@git+https://github.com/kivymd/KivyMD.git@master, plyer

orientation = portrait
fullscreen = 0

# --- ANDROID NASTAVENIA ---
android.api = 33
android.minapi = 21

# KivyMD 2.0.1-dev potrebuje NDK 25.x
android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a
android.bootstrap = sdl2
android.build_tools_version = 33.0.2

# GitHub Actions – automatické prijatie licencií
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True

# Internet povolený
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
