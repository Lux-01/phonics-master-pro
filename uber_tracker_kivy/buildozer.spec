[app]

# Title of your application
title = Uber Distance Tracker

# Package name
package.name = ubertracker

# Package domain (needed for android/ios packaging)
package.domain = com.ubertracker

# Source code where the main.py lives
source.dir = .

# Application versioning
version = 1.0

# Requirements - these are the Python packages needed
requirements = python3,kivy,plyer

# Android specific requirements
android.requirements = android,pyjnius

# Orientation (portrait/landscape)
orientation = portrait

# Icon
# icon.filename = icon.png

# Presplash image
# presplash.filename = presplash.png

# Android API level
android.api = 33

# Minimum Android API
android.minapi = 21

# Android SDK version
android.sdk = 33

# Android NDK version
android.ndk = 25b

# Android permissions
android.permissions = 
    INTERNET,
    ACCESS_FINE_LOCATION,
    ACCESS_COARSE_LOCATION,
    ACCESS_NETWORK_STATE,
    WAKE_LOCK

# Android features
android.features = 
    android.hardware.location,
    android.hardware.location.gps

# Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# Fullscreen
android.fullscreen = 0

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Android logcat filters
android.logcat_filters = *:S python:D

# Android additional libraries
# android.add_libs_arm64_v8a = 

# Android gradle dependencies
# android.gradle_dependencies = 

# Android add java src
# android.add_src = 

# Android add aar
# android.add_aars = 

# Android add jars
# android.add_jars = 

# Android add assets
# android.add_assets = 

# Android private storage
android.private_storage = True

# Android window flags
# android.window_flags = 

# Android presplash color
android.presplash_color = #276EF1

# Android presplash drawable
# android.presplash_drawable = 

# Android add resources
# android.add_resources = 

# Android manifest xml additions
android.manifest_placeholders = 
    [app: "com.ubertracker"]

# Android xml additions
android.add_xml = 
    <uses-feature android:name="android.hardware.location" android:required="true" />,
    <uses-feature android:name="android.hardware.location.gps" android:required="true" />

# Build options
# android.build_tools_version = 

# Android arch
android.archs = arm64-v8a, armeabi-v7a

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.12.2
ios.codesign.allowed = false

# Build directory
# build.dir = 

# Bin directory
# bin.dir = 

[buildozer]

# Buildozer version
log_level = 2

# Warn on root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Bin directory
bin_dir = ./bin

# Buildozer commands
# commands = 
