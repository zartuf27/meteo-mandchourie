#!/usr/bin/env python3
"""
Même chose que generer-audio.py, mais gratuit et sans clé : voix neuronale Microsoft Edge (edge-tts).
Voix par défaut : fr-CH-ArianeNeural, accent suisse romand (femme). Autre voix romande : fr-CH-FabriceNeural (homme).
Voix de France si besoin : fr-FR-RemyMultilingualNeural (celle de JARVIS), fr-FR-VivienneMultilingualNeural.

Installation :  pip install edge-tts
Usage :         python3 generer-audio-edge.py
                python3 generer-audio-edge.py --voix fr-CH-FabriceNeural
Résultat :      dossier « audio/ » à copier à côté de meteo-mandchourie.html, puis audio_dossier: 'audio/'
"""
import os, sys, asyncio, unicodedata, re

try:
    import edge_tts
except ImportError:
    sys.exit("Installer d'abord : pip install edge-tts")

VOIX = "fr-CH-ArianeNeural"   # voix suisse romande (femme) ; homme : fr-CH-FabriceNeural
if "--voix" in sys.argv:
    VOIX = sys.argv[sys.argv.index("--voix") + 1]
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

async def generer():
    os.makedirs(DOSSIER, exist_ok=True)
    for ph in phrases:
        chemin = os.path.join(DOSSIER, slug(ph) + ".mp3")
        if os.path.exists(chemin):
            continue
        # « k-way » se prononce mieux écrit « ka-ouais » pour la synthèse ; le nom de fichier reste basé sur la phrase d'origine
        texte = ph.replace("k-way", "ka-ouais")
        try:
            await edge_tts.Communicate(texte, VOIX, rate="-10%", volume="+30%").save(chemin)
            print("ok ", ph)
        except Exception as e:
            print("ÉCHEC", ph, e)

asyncio.run(generer())
print("Terminé. Copier le dossier « audio » à côté de meteo-mandchourie.html.")
