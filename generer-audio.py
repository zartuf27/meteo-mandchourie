#!/usr/bin/env python3
"""
Génère une fois pour toutes les phrases lues par l'écran météo, avec une voix
naturelle ElevenLabs, dans un dossier « audio/ » à mettre à côté de la page.

Usage :
    export ELEVENLABS_API_KEY="votre_clé"
    python3 generer-audio.py                 # voix par défaut
    python3 generer-audio.py --voix <id>     # autre voix (id trouvé sur elevenlabs.io/voices)

22 phrases courtes, ~500 caractères : le plan gratuit suffit largement.
Les fichiers déjà présents ne sont pas régénérés.
Ensuite, dans la page : audio_dossier: 'audio/'
"""
import os, sys, time, unicodedata, re, json, urllib.request

CLE = os.environ.get("ELEVENLABS_API_KEY")
if not CLE:
    sys.exit("Définir ELEVENLABS_API_KEY d'abord.")

VOIX = "XB0fDUnXU5powFXDhCwa"   # « Charlotte », voix française naturelle ; à remplacer si besoin
if "--voix" in sys.argv:
    VOIX = sys.argv[sys.argv.index("--voix") + 1]
MODELE = "eleven_multilingual_v2"
DOSSIER = "audio"

# ---- exactement les mêmes phrases que la page ----------------------------
phrases = ["Il va faire très froid.", "Il va faire froid.", "Il va faire doux.", "Il va faire chaud.",
           "Il va neiger.", "Il va y avoir de l’orage.", "Il va pleuvoir.", "Il va y avoir du soleil.", "Il va y avoir du brouillard.",
           "Il y a beaucoup de vent.", "Il fait très chaud.", "Il gèle. Attention, ça glisse.",
           "Mettez un manteau chaud.", "Mettez un bonnet.", "Mettez une veste.",
           "Mettez un pull à longues manches.", "Mettez un t-shirt.", "Mettez un k-way.",
           "Prenez un parapluie.", "Prenez une veste.", "Mettez une casquette.", "Buvez beaucoup d’eau."]

def slug(t):  # même règle que dans la page
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", t))

os.makedirs(DOSSIER, exist_ok=True)
for ph in phrases:
    chemin = os.path.join(DOSSIER, slug(ph) + ".mp3")
    if os.path.exists(chemin):
        continue
    corps = json.dumps({"text": ph, "model_id": MODELE,
                        "voice_settings": {"stability": 0.6, "similarity_boost": 0.8, "speed": 0.9}}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOIX}?output_format=mp3_44100_64",
        data=corps, headers={"xi-api-key": CLE, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r, open(chemin, "wb") as f:
            f.write(r.read())
        print("ok ", ph)
    except Exception as e:
        print("ÉCHEC", ph, e)
    time.sleep(0.4)  # respect des limites de l'API
print("Terminé. Copier le dossier « audio » à côté de meteo-mandchourie.html.")
