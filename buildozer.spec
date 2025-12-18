[app]
# Nome e pacchetto
title = Synthetic School
package.name = synthetic
package.domain = org.test

# Directory e file
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Versione
version = 1.0

# --- LIBRERIE NECESSARIE ---
# Qui includiamo tutto quello che serve per far girare il codice sopra
requirements = python3,kivy==2.3.0,google-generativeai,requests,urllib3,pillow,android

# --- PERMESSI ANDROID ---
# Fondamentali per usare Camera e Internet
android.permissions = INTERNET,CAMERA,RECORD_AUDIO

# Configurazioni APK
orientation = landscape
fullscreen = 0
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
p4a.branch = master