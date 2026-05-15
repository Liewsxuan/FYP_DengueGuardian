[app]

title = DengueGuardian
package.name = dengueguardian
package.domain = org.sibu.dengueguardian

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

# ---------------------------------------------------------------
# REQUIREMENTS
# ---------------------------------------------------------------
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,certifi,charset-normalizer,idna,plyer,pillow,mapview

orientation = portrait
fullscreen = 0

# ---------------------------------------------------------------
# ANDROID — API 34 target, supports Android 5.0 (API 21) to Android 14+
# ---------------------------------------------------------------

# Permission strategy:
#   - CAMERA                    : camera on all versions
#   - INTERNET                  : network on all versions
#   - ACCESS_FINE_LOCATION      : GPS on all versions
#   - ACCESS_COARSE_LOCATION    : network location on all versions
#   - READ_EXTERNAL_STORAGE     : gallery read on Android <= 12 (API 32), ignored on 13+
#   - WRITE_EXTERNAL_STORAGE    : file write on Android <= 9 (API 28), ignored on 10+
#   - READ_MEDIA_IMAGES         : gallery read on Android 13+ (API 33+)
android.permissions = CAMERA,INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.sdk = 34

android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True

# arm64-v8a  → all modern Android phones (2018+)
# armeabi-v7a → older/budget devices still on 32-bit ARM
android.archs = arm64-v8a, armeabi-v7a

# AndroidX libraries needed for modern file access and activity result APIs
android.gradle_dependencies = androidx.activity:activity:1.7.2,androidx.core:core:1.10.1

# ---------------------------------------------------------------
# P4A
# ---------------------------------------------------------------
p4a.url = https://github.com/kivy/python-for-android/archive/refs/tags/2023.05.21.zip
p4a.bootstrap = sdl2

[buildozer]

log_level = 2
warn_on_root = 1
