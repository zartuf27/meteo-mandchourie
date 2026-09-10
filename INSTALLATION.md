# Installation — afficheur météo La Mandchourie

Ordre à suivre. Compter environ 1 h 30 en tout, dont 20 minutes sur la tablette.

## A. Avant la tablette (à faire ce soir, depuis un ordinateur)

### A1. Mettre la page en ligne sur GitHub Pages (15 min, gratuit, aucun outil à installer)
1. Créer un compte sur github.com si besoin.
2. « New repository » → nom : `meteo-mandchourie` → **Public** → « Create repository ».
3. « Add file » → « Upload files » → glisser dans la fenêtre :
   - `meteo-mandchourie.html`
   - le dossier `images` complet (glisser le dossier, pas seulement son contenu)
   - `CLAUDE.md`, `INSTALLATION.md`, `mode-d-emploi-equipe.html`
   - plus tard : le dossier `audio` s'il est généré
   → « Commit changes ».
4. Onglet « Settings » → menu « Pages » → Source : « Deploy from a branch » → Branch : `main`, dossier `/ (root)` → « Save ».
5. Attendre 1 à 2 minutes. L'adresse est : `https://<votre-nom>.github.io/meteo-mandchourie/meteo-mandchourie.html`
6. Ouvrir cette adresse sur le téléphone : la page doit montrer la météo de Delémont et « MétéoSuisse » en bas. Tester aussi `…/meteo-mandchourie.html?demo=neige`.

Pour modifier la page plus tard : ouvrir le fichier sur GitHub → icône crayon → modifier `REGLAGES` → « Commit ». La tablette prend la nouvelle version au rechargement de midi, ou en redémarrant Fully Kiosk.

### A2. Voix naturelle (10 min, facultatif mais recommandé)
Sur l'ordinateur : `pip install edge-tts` puis `python3 generer-audio-edge.py`. Ça crée un dossier `audio` avec 22 fichiers MP3 (voix Ariane, accent suisse romand ; `--voix fr-CH-FabriceNeural` pour une voix d'homme). Envoyer ce dossier sur GitHub comme en A1, puis dans la page mettre `audio_dossier: 'audio/'`.
Sans cette étape, la tablette utilise sa propre voix, qui marche aussi.

## B. La tablette (20 min)

### B1. Réglages Android
- Wi-Fi du foyer connecté ; vérifier que la page s'ouvre dans Chrome.
- Paramètres → Affichage : luminosité manuelle (désactiver « adaptative »), 60–70 % ; mise en veille : « jamais » ou le maximum.
- Rotation automatique : désactivée, tablette en paysage.
- Paramètres → Système → Mises à jour : désactiver les mises à jour automatiques si possible.
- Paramètres → Langues → Synthèse vocale : moteur Google, langue français, télécharger la voix française « haute qualité » si proposée. Tester avec « Écouter un exemple ».
- Retirer le compte Google du bureau s'il n'est pas nécessaire (Paramètres → Comptes).
- Vérifier au dos que la batterie n'a pas gonflé.

### B2. Fully Kiosk Browser (Play Store, gratuit)
1. Installer, ouvrir, entrer l'adresse de la page comme « Start URL ».
2. Settings → Web Content Settings → **Enable JavaScript Interface (PLUS)** : activé. Sans ça, la page ne peut pas éteindre l'écran ; elle affichera un écran noir à la place, ce qui fonctionne aussi.
3. Settings → Web Content Settings → **Autoplay Audio** : activé.
4. Settings → Device Management → **Keep Screen On** : activé. **Screen Off / On schedule** : laisser vide (la page gère).
5. Settings → Kiosk Mode : activer, définir un code PIN, le noter dans le classeur de l'équipe.
6. Settings → Other Settings → « Reload on … » : laisser par défaut.
7. Quitter les réglages : la page s'affiche plein écran. Toucher l'écran : la voix lit.

Note : certaines options marquées PLUS demandent la licence Fully Kiosk Plus (environ 7 CHF, une fois). Sans licence, tout fonctionne sauf l'extinction réelle de l'écran, remplacée par un écran noir.

### B3. Vérifications
- Le pied de page montre l'heure de mise à jour du jour.
- Toucher n'importe où : la voix parle. Toucher pendant qu'elle parle : elle recommence.
- Laisser tourner jusqu'à 11h30 un jour de semaine : l'écran s'éteint (ou devient noir). À 16h il se rallume.

## C. Le mur (15 min)
- Support mural à hauteur des yeux d'une personne assise ou debout, selon la salle.
- Câble d'alimentation en goulotte, chargeur hors de portée.
- Coller au dos du cadre ou dans le classeur : « Pictogrammes : Mulberry Symbols, Steve Lee, CC BY-SA 4.0 ».
- Imprimer `mode-d-emploi-equipe.html` (ouvrir dans un navigateur → Imprimer) et le mettre dans le classeur de l'équipe.

## D. Les jours suivants
- Vérifier au déjeuner de 7h que la météo affichée est celle du jour (heure de mise à jour du matin ou de la veille à 21h25).
- Faire le test avec deux ou trois résidents (`test-residents.md`).
- Ajuster les seuils dans `REGLAGES` d'après ce test.
