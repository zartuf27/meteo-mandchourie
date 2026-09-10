#!/usr/bin/env bash
# Restaure la tablette à ses réglages par défaut.
set -e

ADB="${USERPROFILE}/platform-tools/adb.exe"
if ! command -v "$ADB" &>/dev/null; then ADB="adb"; fi

echo "Attente de la tablette..."
"$ADB" wait-for-device

"$ADB" shell settings put system accelerometer_rotation 1
"$ADB" shell settings put system screen_brightness_mode 1
"$ADB" shell settings put system screen_off_timeout 120000
"$ADB" shell settings put global stay_on_while_plugged_in 0
"$ADB" shell settings put global heads_up_notifications_enabled 1 2>/dev/null || true
"$ADB" shell pm enable com.android.vending 2>/dev/null || true

for pkg in \
  com.android.calendar com.android.deskclock com.android.email \
  com.android.calculator2 com.android.contacts com.android.dialer \
  com.android.messaging com.android.music com.android.gallery3d \
  com.android.camera2 com.google.android.youtube com.google.android.apps.maps \
  com.google.android.gm com.google.android.videos com.google.android.music \
  com.google.android.apps.photos com.google.android.apps.docs \
  com.google.android.talk; do
  "$ADB" shell pm enable "$pkg" 2>/dev/null || true
done

echo ""
echo "Tablette restaurée. Redémarrer la tablette."
