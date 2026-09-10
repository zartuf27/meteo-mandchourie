#!/usr/bin/env bash
# Configuration complète de la tablette météo La Mandchourie via ADB.
# Lancé par Claude Code quand la tablette est branchée en USB (mode développeur).
set -e

ADB="${USERPROFILE}/platform-tools/adb.exe"
if ! command -v "$ADB" &>/dev/null; then
  ADB="adb"
fi
if ! command -v "$ADB" &>/dev/null; then
  echo "ERREUR : ADB introuvable. Installer avec : winget install Google.PlatformTools"
  exit 1
fi

PAGE="https://zartuf27.github.io/meteo-mandchourie/meteo-mandchourie.html"
FULLY_PKG="de.ozerov.fully"
FULLY_APK_URL="https://www.fully-kiosk.com/apk/fully-kiosk-browser-latest.apk"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "=== CONFIGURATION TABLETTE MÉTÉO — LA MANDCHOURIE ==="
echo ""

# ── 1. Connexion ─────────────────────────────────────────────
echo "[1/9] Attente de la tablette..."
"$ADB" wait-for-device
echo "       Connectée."

# ── 2. Infos ─────────────────────────────────────────────────
echo ""
echo "[2/9] Informations :"
MODEL=$("$ADB" shell getprop ro.product.model | tr -d '\r')
ANDROID=$("$ADB" shell getprop ro.build.version.release | tr -d '\r')
SCREEN=$("$ADB" shell wm size 2>/dev/null | tr -d '\r')
BATTERY=$("$ADB" shell cat /sys/class/power_supply/battery/capacity 2>/dev/null | tr -d '\r')
echo "       Modèle  : $MODEL"
echo "       Android : $ANDROID"
echo "       Écran   : $SCREEN"
echo "       Batterie: ${BATTERY}%"

# ── 3. Rotation paysage bloquée ──────────────────────────────
echo ""
echo "[3/9] Rotation paysage bloquée..."
"$ADB" shell settings put system accelerometer_rotation 0
"$ADB" shell settings put system user_rotation 1

# ── 4. Luminosité manuelle 60% ──────────────────────────────
echo "[4/9] Luminosité 60%, manuelle..."
"$ADB" shell settings put system screen_brightness_mode 0
"$ADB" shell settings put system screen_brightness 153

# ── 5. Veille + écran allumé en charge ──────────────────────
echo "[5/9] Veille désactivée, écran allumé tant que branché..."
"$ADB" shell settings put system screen_off_timeout 2147483647
"$ADB" shell settings put global stay_on_while_plugged_in 3

# ── 6. Volume max + notifications off ───────────────────────
echo "[6/9] Volume max, notifications pop-up désactivées..."
"$ADB" shell media volume --stream 3 --set 15 2>/dev/null || true
"$ADB" shell settings put global heads_up_notifications_enabled 0 2>/dev/null || true

# ── 7. Synthèse vocale FR + Play Store off ──────────────────
echo "[7/9] Synthèse vocale FR, Play Store désactivé..."
"$ADB" shell settings put secure tts_default_locale fr_FR 2>/dev/null || true
"$ADB" shell pm disable-user --user 0 com.android.vending 2>/dev/null || true

# ── 8. Désactiver les apps inutiles ─────────────────────────
echo "[8/9] Désactivation des apps inutiles..."
for pkg in \
  com.android.calendar com.android.deskclock com.android.email \
  com.android.calculator2 com.android.contacts com.android.dialer \
  com.android.messaging com.android.music com.android.gallery3d \
  com.android.camera2 com.google.android.youtube com.google.android.apps.maps \
  com.google.android.gm com.google.android.videos com.google.android.music \
  com.google.android.apps.photos com.google.android.apps.docs \
  com.google.android.talk; do
  "$ADB" shell pm disable-user --user 0 "$pkg" 2>/dev/null || true
done

# ── 9. Fully Kiosk Browser ──────────────────────────────────
echo "[9/9] Fully Kiosk Browser..."
if "$ADB" shell pm list packages 2>/dev/null | grep -qi "$FULLY_PKG"; then
  echo "       Déjà installé."
else
  APK_LOCAL="$SCRIPT_DIR/fully-kiosk.apk"
  if [ ! -f "$APK_LOCAL" ]; then
    echo "       Téléchargement de l'APK..."
    curl -L -o "$APK_LOCAL" "$FULLY_APK_URL" 2>/dev/null || true
  fi
  if [ -f "$APK_LOCAL" ]; then
    echo "       Installation..."
    "$ADB" install "$APK_LOCAL" 2>/dev/null || echo "       (échec install, continuer)"
  else
    echo "       APK non trouvé. Installer manuellement depuis le Play Store."
  fi
fi

# Lancer Fully Kiosk ou Chrome avec la page
if "$ADB" shell pm list packages 2>/dev/null | grep -qi "$FULLY_PKG"; then
  echo "       Lancement de Fully Kiosk..."
  "$ADB" shell am start -n "$FULLY_PKG/.FullyActivity" \
    -a android.intent.action.VIEW -d "$PAGE" 2>/dev/null || true
  FULLY_OK=true
else
  echo "       Lancement dans le navigateur..."
  "$ADB" shell am start -a android.intent.action.VIEW -d "$PAGE" 2>/dev/null || true
  FULLY_OK=false
fi

# ── Résumé ───────────────────────────────────────────────────
echo ""
echo "=== CONFIGURATION TERMINÉE ==="
echo ""
echo "  Modèle      : $MODEL (Android $ANDROID)"
echo "  Batterie    : ${BATTERY}%"
echo "  Rotation    : paysage, bloquée"
echo "  Luminosité  : 60%, manuelle"
echo "  Veille      : désactivée"
echo "  Volume      : maximum"
echo "  Play Store  : désactivé"
echo "  Apps inutiles: désactivées"
echo "  Page        : $PAGE"
echo ""

if [ "$FULLY_OK" = true ]; then
  echo "  RÉGLAGES MANUELS FULLY KIOSK (sur la tablette) :"
  echo "    1. Settings > Web Content > Enable JavaScript Interface : ON"
  echo "    2. Settings > Web Content > Autoplay Audio : ON"
  echo "    3. Settings > Device Management > Keep Screen On : ON"
  echo "    4. Settings > Kiosk Mode : ON + choisir un code PIN"
  echo "    5. NE PAS activer Screen Off/On Schedule"
  echo ""
fi

echo "  La page météo doit s'afficher avec 'MétéoSuisse' en bas."
echo "  Toucher l'écran : la voix lit la météo."
echo ""
echo "  Pour restaurer la tablette : bash restaurer-tablette.sh"
