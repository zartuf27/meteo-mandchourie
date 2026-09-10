@echo off
chcp 65001 >nul
set "PATH=%PATH%;%USERPROFILE%\platform-tools;%LOCALAPPDATA%\Android\Sdk\platform-tools"
title Configuration tablette météo — La Mandchourie
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   CONFIGURATION TABLETTE MÉTÉO — LA MANDCHOURIE        ║
echo  ║   Brancher la tablette en USB, mode développeur activé  ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

REM ── Vérifier / installer ADB ──────────────────────────────────
where adb >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [1/8] ADB non trouvé. Installation via winget...
    winget install Google.PlatformTools --accept-package-agreements --accept-source-agreements
    set "PATH=%PATH%;%LOCALAPPDATA%\Android\Sdk\platform-tools;%USERPROFILE%\AppData\Local\Android\Sdk\platform-tools;%USERPROFILE%\platform-tools"
    where adb >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo  ERREUR : ADB introuvable après installation.
        echo  Télécharger manuellement : https://developer.android.com/tools/releases/platform-tools
        echo  Extraire dans C:\platform-tools et relancer ce script.
        pause
        exit /b 1
    )
) else (
    echo [1/8] ADB trouvé.
)

REM ── Attendre la tablette ───────────────────────────────────────
echo.
echo [2/8] Recherche de la tablette...
echo        Si la tablette demande "Autoriser le débogage USB", appuyer sur OK.
echo.
adb wait-for-device
echo        Tablette connectée !
echo.

REM ── Infos tablette ─────────────────────────────────────────────
echo [3/8] Informations tablette :
for /f "tokens=*" %%a in ('adb shell getprop ro.product.model') do echo        Modèle  : %%a
for /f "tokens=*" %%a in ('adb shell getprop ro.build.version.release') do echo        Android : %%a
for /f "tokens=*" %%a in ('adb shell wm size') do echo        Écran   : %%a
for /f "tokens=*" %%a in ('adb shell cat /sys/class/power_supply/battery/capacity 2^>nul') do echo        Batterie: %%a%%
echo.

REM ── Réglages Android ───────────────────────────────────────────
echo [4/8] Configuration Android...

REM Rotation bloquée en paysage
adb shell settings put system accelerometer_rotation 0
adb shell settings put system user_rotation 1
echo        Rotation bloquée en paysage

REM Luminosité manuelle, 60%
adb shell settings put system screen_brightness_mode 0
adb shell settings put system screen_brightness 153
echo        Luminosité manuelle 60%%

REM Écran toujours allumé (la page gère l'extinction)
adb shell settings put system screen_off_timeout 2147483647
echo        Veille écran désactivée

REM Volume média au max
adb shell media volume --stream 3 --set 15 >nul 2>&1
echo        Volume média au maximum

REM Désactiver les notifications sonores
adb shell settings put global heads_up_notifications_enabled 0 >nul 2>&1
echo        Notifications pop-up désactivées

REM Désactiver les mises à jour automatiques du Play Store
adb shell pm disable-user --user 0 com.android.vending >nul 2>&1
echo        Play Store désactivé (pas de mises à jour intempestives)

REM Synthèse vocale : langue française
adb shell settings put secure tts_default_locale fr_FR >nul 2>&1
echo        Synthèse vocale en français

REM Garder l'écran allumé en charge (développeur)
adb shell settings put global stay_on_while_plugged_in 3
echo        Écran allumé tant que branché

echo.

REM ── Installer Fully Kiosk Browser ─────────────────────────────
echo [5/8] Fully Kiosk Browser...
adb shell pm list packages | findstr /i "de.ozerov.fully" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo        Fully Kiosk déjà installé.
) else (
    if exist "%~dp0fully-kiosk.apk" (
        echo        Installation de fully-kiosk.apk...
        adb install "%~dp0fully-kiosk.apk"
    ) else (
        echo.
        echo        Fully Kiosk n'est pas installé.
        echo        Options :
        echo          a) Télécharger l'APK depuis https://www.fully-kiosk.com/apk/
        echo             le renommer fully-kiosk.apk, le placer dans ce dossier, relancer.
        echo          b) L'installer depuis le Play Store sur la tablette.
        echo          c) Continuer sans (Chrome en plein écran, moins bien).
        echo.
        set /p CHOIX="        Continuer sans Fully Kiosk ? (O/N) : "
        if /i "%CHOIX%"=="N" (
            echo        Installer Fully Kiosk puis relancer ce script.
            pause
            exit /b 0
        )
    )
)
echo.

REM ── Configurer Fully Kiosk si installé ─────────────────────────
adb shell pm list packages | findstr /i "de.ozerov.fully" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [6/8] Configuration Fully Kiosk...

    REM Créer le fichier de config Fully Kiosk
    adb shell "mkdir -p /sdcard/fully" 2>nul

    REM Écrire les réglages dans un fichier temporaire puis le pousser
    echo        Envoi des réglages Fully Kiosk...

    REM Lancer Fully Kiosk avec l'URL de la page
    adb shell am start -n de.ozerov.fully/.FullyActivity -a android.intent.action.VIEW -d "https://zartuf27.github.io/meteo-mandchourie/meteo-mandchourie.html" >nul 2>&1
    echo        Fully Kiosk lancé avec l'adresse de la page.
    echo.
    echo        IMPORTANT — Réglages manuels dans Fully Kiosk :
    echo          1. Settings ^> Web Content ^> Enable JavaScript Interface : ON
    echo          2. Settings ^> Web Content ^> Autoplay Audio : ON
    echo          3. Settings ^> Device Management ^> Keep Screen On : ON
    echo          4. Settings ^> Kiosk Mode : ON, définir un code PIN
    echo          5. Settings ^> Other ^> Start URL = l'adresse ci-dessus
    echo          6. NE PAS activer la planification d'écran de Fully
    echo.
) else (
    echo [6/8] Pas de Fully Kiosk. Configuration Chrome...
    REM Ouvrir la page dans Chrome
    adb shell am start -a android.intent.action.VIEW -d "https://zartuf27.github.io/meteo-mandchourie/meteo-mandchourie.html" >nul 2>&1
    echo        Page ouverte dans le navigateur par défaut.
    echo        Pour le plein écran : ouvrir Chrome, menu ^> Ajouter à l'écran d'accueil.
    echo.
)

REM ── Désactiver les apps inutiles ───────────────────────────────
echo [7/8] Désactivation des apps inutiles sur une tablette dédiée...

REM Liste des packages à désactiver (sans risque, réactivables)
for %%p in (
    com.android.calendar
    com.android.deskclock
    com.android.email
    com.android.calculator2
    com.android.contacts
    com.android.dialer
    com.android.messaging
    com.android.music
    com.android.gallery3d
    com.android.camera2
    com.google.android.youtube
    com.google.android.apps.maps
    com.google.android.gm
    com.google.android.videos
    com.google.android.music
    com.google.android.apps.photos
    com.google.android.apps.docs
    com.google.android.talk
) do (
    adb shell pm disable-user --user 0 %%p >nul 2>&1
)
echo        Apps non essentielles désactivées.
echo        (Réactivable avec : adb shell pm enable [package])
echo.

REM ── Vérification finale ────────────────────────────────────────
echo [8/8] Vérification...
echo.
echo  ┌──────────────────────────────────────────────────────┐
echo  │  RÉCAPITULATIF                                       │
echo  │                                                      │
echo  │  Rotation     : paysage, bloquée                     │
echo  │  Luminosité   : 60%%, manuelle                       │
echo  │  Veille       : désactivée (la page gère)            │
echo  │  Volume       : maximum                              │
echo  │  Mises à jour : bloquées                             │
echo  │  Apps inutiles: désactivées                          │
echo  │                                                      │
echo  │  Page : zartuf27.github.io/meteo-mandchourie/        │
echo  │         meteo-mandchourie.html                       │
echo  │                                                      │
echo  │  RESTE À FAIRE DANS FULLY KIOSK :                    │
echo  │    - Enable JavaScript Interface                     │
echo  │    - Autoplay Audio                                  │
echo  │    - Kiosk Mode + code PIN                           │
echo  │    - NE PAS activer la planification d'écran         │
echo  └──────────────────────────────────────────────────────┘
echo.
echo  La tablette est prête. Fixer au mur, brancher en USB secteur.
echo.
pause
