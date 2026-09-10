@echo off
chcp 65001 >nul
set "PATH=%PATH%;%USERPROFILE%\platform-tools;%LOCALAPPDATA%\Android\Sdk\platform-tools"
title Restauration tablette
color 0E

echo.
echo  Restauration des réglages par défaut de la tablette.
echo  Brancher la tablette en USB.
echo.

adb wait-for-device

REM Réactiver la rotation automatique
adb shell settings put system accelerometer_rotation 1

REM Luminosité adaptative
adb shell settings put system screen_brightness_mode 1

REM Veille 2 minutes
adb shell settings put system screen_off_timeout 120000

REM Ne plus rester allumé en charge
adb shell settings put global stay_on_while_plugged_in 0

REM Réactiver le Play Store
adb shell pm enable com.android.vending >nul 2>&1

REM Réactiver les notifications
adb shell settings put global heads_up_notifications_enabled 1 >nul 2>&1

REM Réactiver les apps
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
    adb shell pm enable %%p >nul 2>&1
)

echo.
echo  Tablette restaurée. Redémarrer pour appliquer.
echo.
pause
