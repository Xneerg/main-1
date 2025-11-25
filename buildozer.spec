[app]
title = MyApp
package.name = myapp
package.domain = org.mycompany

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,xml,json,webp

version = 0.1

# KivyMD verzia MUST HAVE !!!
requirements = python3,kivy==2.3.0,kivymd@git+https://github.com/kivymd/KivyMD.git@master

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

android.build_tools_version = 33.0.2
android.bootstrap = sdl2

android.accept_sdk_license = True
android.accept_android_sdk_license = True
android.accept_android_ndk_license = True

p4a.local_recipes = ./p4a-recipes

# Gradle fix
android.gradle_version = 8.0.2
android.gradle_dependencies =

android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
