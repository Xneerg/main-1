[app]
title = MyApp
package.name = myapp
package.domain = org.mycompany

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,xml

version = 0.1
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a

android.build_tools_version = 33.0.2
android.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
