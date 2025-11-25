[app]
# --- ZÁKLAD ---
title = MyApp
package.name = myapp
package.domain = org.mycompany

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,xml

version = 0.1
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# --- ANDROID ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

android.build_tools_version = 33.0.2
android.bootstrap = sdl2

# Automaticky prijme licencie (potrebné pre GitHub Actions)
android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True

# Voliteľné zrýchlenie buildu
p4a.local_recipes = ./p4a-recipes

# Zákaz starých a rozbitých JDK/Gradle nastavení
# GitHub workflow nastaví Java 17, Buildozer to nemá meniť
android.gradle_dependencies =
android.gradle_version = 8.0.2

# Ak potrebuješ internet v app:
android.permissions = INTERNET

# Ak chceš include KivyMD
# requirements = python3,kivy==2.3.0,kivymd


[buildozer]
log_level = 2
warn_on_root = 0
