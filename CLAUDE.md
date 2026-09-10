# CLAUDE.md — Afficheur météo FALC, Résidence La Mandchourie

Documentation complète du projet. À lire en entier avant toute modification.
Ce fichier sert de mémoire du projet : contexte, décisions, fonctionnement, réglages, tests, et ce qu'il ne faut pas faire.

---

## 1. Le projet en une phrase

Une tablette murale, dans la salle commune de la Résidence La Mandchourie (Delémont), affiche chaque jour la météo et un conseil d'habillement en Facile à Lire et à Comprendre (FALC), pour que les résidents adultes en situation de handicap intellectuel choisissent eux-mêmes leur tenue avant de partir en atelier.

---

## 2. Contexte

- **Lieu** : Résidence La Mandchourie, Rue du Pont-Neuf 4, 2800 Delémont (Fondation Les Castors, Foyer de Porrentruy).
- **Public** : adultes avec handicap intellectuel, hébergés en résidence. La grande majorité part au travail (ateliers) à 7h30 et rentre vers 16h.
- **Porteur** : Ludovic Vitelli, éducateur social (60 %), membre de l'équipe éducative.
- **Matériel** : une tablette Android inutilisée du bureau. Aucun achat. Alimentée en USB, fixée au mur.
- **Réseau** : Wi-Fi du foyer, coupé toute la nuit. La tablette se met en veille de 21h30 à 6h30 (géré par la page elle-même, voir §7).
- **Objectif éducatif** : autodétermination. L'écran informe, le résident décide. L'écran n'est jamais une autorité (« c'est écrit »), et l'accompagnement reste humain.

---

## 3. Historique des décisions (pourquoi c'est comme ça)

| Question | Décision | Raison |
|---|---|---|
| Écran e-ink sur ESP32 ? | Abandonné | Prix (55–70 CHF), noir/blanc seulement, aucun collègue ne sait reflasher un ESP32 |
| Tablette LCD | Retenu | Zéro coût (tablette existante), couleur, remplaçable, un collègue sait débrancher/rebrancher, mise à jour à distance |
| Batterie ou secteur ? | Secteur | Une batterie qu'on oublie de charger donne une météo périmée, trompeuse pour les résidents |
| Détection de présence par caméra ? | Non | Caméra dans un foyer = question de protection des données ; économie de quelques francs par an ; écran qui s'allume à l'approche = surprise pour certains résidents |
| Défilement météo → habillement (carrousel) ? | Non | Inclusion Europe : pas de pages qui changent seules, tout doit tenir sur un écran ; WCAG 2.2.2 |
| Animations ? | Désactivées par défaut | Inclusion Europe, règle écran n° 22 : « Ne placez pas d'animations sur l'écran ». Réactivables si le test avec les résidents le justifie |
| Pictos dessinés ou photos ? | Mulberry Symbols livrés et actifs ; dessins intégrés en secours ; photos possibles | Pour la météo (phénomène), un symbole est plus clair qu'une photo ; pour les vêtements (objets), des photos des vraies affaires du foyer peuvent être meilleures. À trancher avec les résidents |
| Voix : ElevenLabs en direct ? | Non, phrases pré-enregistrées | Clé d'API exposée, coût par lecture, dépendance réseau. Les 22 phrases sont enregistrées une fois et jouées hors ligne |
| Déclenchement de la voix | Toute la page | Un seul geste possible, pas de cible à viser. Événement `click` (relâchement), pas `pointerdown` : Android n'autorise le son que sur le relâchement |
| Température lue à voix haute ? | Non | Remplacée par des phrases simples : « Il va faire froid. Il va pleuvoir. » Le chiffre reste à l'écran |
| Modèle météo | MétéoSuisse ICON-CH via Open-Meteo, repli automatique sur le modèle mondial | Résolution 1–2 km, adaptée au relief jurassien |
| Fériés | Liste du foyer (pas seulement cantonale) + ponts | Tirée des documents « jours fériés Mandchourie » 2024, 2025, 2026 |
| Permanences | Calculées par une règle, plus liste d'exceptions | Neuf années de plannings (2018–2026) suivent la même règle : samedi 13–19 juillet pour 23 jours, samedi 19–25 décembre pour 16 jours |
| Hébergement | GitHub Pages recommandé (pas le homelab) | Gratuit, jamais en panne, modifiable par un collègue sans dépendre du matériel personnel de Ludovic |

---

## 4. Fichiers livrés

```
meteo-mandchourie.html   la page complète (HTML + CSS + JS, aucun fichier externe obligatoire)
generer-audio.py         script Python pour enregistrer les 22 phrases avec ElevenLabs (payant/plan gratuit)
generer-audio-edge.py    même chose, gratuit et sans clé, voix Microsoft Edge, accent suisse romand (fr-CH-Ariane ; Fabrice pour une voix d'homme) — à préférer
INSTALLATION.md          pas à pas : GitHub Pages, réglages Android, Fully Kiosk, fixation
mode-d-emploi-equipe.html  fiche imprimable d'une page pour le classeur de l'équipe
test-residents.md        protocole et feuille de relevé du test FALC avec les résidents
note-colloque.md         texte court pour présenter le projet au colloque
CLAUDE.md                ce document
images/                  19 pictogrammes Mulberry Symbols (SVG) + ATTRIBUTION.txt, voir §9
audio/                   (facultatif) phrases enregistrées, voir §10
```

La page est **autonome** : un seul fichier, pas de bibliothèque, pas de police à télécharger (police système : Atkinson Hyperlegible si installée, sinon Verdana). Elle fonctionne ouverte directement depuis un fichier, mais le rechargement quotidien (§7) demande qu'elle soit servie par un serveur web.

---

## 5. Ce que l'écran affiche

De haut en bas, tout sur un seul écran, sans défilement :

1. **« Aujourd'hui »** puis la date en entier : « Mercredi 9 septembre 2026 » (règle FALC : dates en toutes lettres, chiffres en chiffres).
2. **Bloc central** : à gauche un grand pictogramme météo avec un mot (Soleil / Soleil et nuages / Nuages / Brouillard / Pluie / Neige / Orage) ; à droite « Ce matin » ou « Cet après-midi » et la température en très grand (« 8° »).
3. **Ligne d'information**, seulement si nécessaire (jamais plus de deux) : vent fort, canicule, gel. Les alertes sont en rouge.
4. **Bloc habillement** : pictos des vêtements + une phrase par ligne, alignée à gauche : « Mettez un k-way. / Prenez un parapluie. » ; bouton rond « écouter » à droite (repère visuel, toute la page déclenche la voix).
5. **Pied de page** en petit gris, pour l'équipe : « Mis à jour le 9 septembre à 06h12 — MétéoSuisse », avec « — pas de Wi-Fi depuis un moment » si les données ont plus de 14 h.

Le fond de page prend une teinte très pâle selon le temps (jaune soleil, bleu pluie, gris nuages…) : deuxième indice, en plus du picto et du mot.

Cas sans données : picto « ? » et « Aucune donnée reçue pour le moment — vérifier le Wi-Fi ».

---

## 6. Logique météo

### Source
Open-Meteo, `https://api.open-meteo.com/v1/forecast`, sans clé ni compte.
Paramètres : `hourly=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation_probability`, `daily=temperature_2m_max,apparent_temperature_max`, `timezone=Europe/Zurich`, `forecast_days=3`, `models=meteoswiss_icon_seamless`.
Si l'appel avec le modèle MétéoSuisse échoue ou renvoie des données vides, la page refait l'appel sans `models` (modèle mondial). Le pied de page indique « MétéoSuisse » quand c'est ce modèle qui a servi.

### Fiche par jour (fonction `condenser`)
Pour chacun des 3 jours reçus :
- **matin** : température de 8h (`heure_matin`), ressenti de 8h, code météo de 9h, vent max et probabilité de pluie max sur 7h–12h.
- **après-midi** : maximum du jour, ressenti max, code météo de 14h (`heure_apres_midi`), vent max et probabilité de pluie max sur 12h–21h.

### Affichage matin / après-midi
Avant 11h30 (`bascule`) : « Ce matin » et la fiche matin. Après : « Cet après-midi » et la fiche après-midi.

### Codes météo (WMO) → picto
- 0 → soleil · 1–2 → éclaircies · 3 → nuages · 45, 48 → brouillard
- 51–67, 80–82 → pluie · 71–77, 85, 86 → neige · 95+ → orage

### Cache
Chaque réception est stockée dans `localStorage` (clé `meteo-mandchourie-v2`). Au démarrage, la page affiche le cache avant même de demander le réseau. Sans réseau, elle affiche la fiche du jour issue de la dernière réception (jusqu'à 3 jours de réserve).

---

## 7. Rythme des mises à jour et horaires d'écran

### Cycle quotidien (jour de semaine)
| Heure | Ce qui se passe |
|---|---|
| 06:00 | Écran allumé (commande Fully Kiosk ou écran noir retiré). Demande météo immédiate. |
| 06:00–07:30 | **Créneau critique** : tant qu'aucune météo du jour même n'a été reçue, nouvel essai toutes les 5 min. Dès le retour du Wi-Fi, mise à jour dans la minute (événement `online`). |
| journée | Demande toutes les 30 min. |
| 11:30 | Écran éteint (résidents en atelier). |
| 12:00 | Rechargement complet de la page, seulement si le serveur répond (`HEAD` sur l'adresse de la page). Évite qu'une page figée depuis des semaines reste en place. |
| 16:00 | Écran allumé, demande immédiate. |
| 21:25 | **Précharge du soir** : dernière demande fixe. La fiche du lendemain est en réserve. |
| 21:30 | Écran éteint. Le Wi-Fi du foyer se coupe pour la nuit. |

Au réveil de la tablette (`visibilitychange`), demande immédiate.

### Plages d'allumage
```
semaine    : 06:00–11:30 et 16:00–21:30
weekend    : 07:00–21:30        (aussi fériés et ponts)
permanence : 07:00–21:30
```
Tirées des plannings 2025 de la Mandchourie : codes horaires de semaine 6h30–8h30 / 8h30–11h30 / 10h30–11h30 le matin, 16h–19h / 16h–21h30 / 16h–22h le soir ; week-end W1 9h–18h, W2 14h–22h ; permanence M1 8h–15h, M3 8h–17h, M2 14h–22h.

### Type de jour (`typeDeJour`)
1. Si la date est dans une période de `permanences` → `permanence`.
2. Sinon, samedi, dimanche ou férié du foyer → `weekend`.
3. Sinon → `semaine`.

### Fériés du foyer (`ferieFoyer`)
Tout est calculé pour l'année en cours, rien n'est figé.
Fixes : 1er janvier, 2 janvier, 1er mai, 23 juin (Plébiscite), 1er août, 15 août, 1er novembre (si `toussaint: true` ; confirmé par Ludovic et par le document 2024), 25 décembre.
Mobiles, calculés depuis Pâques (algorithme de Meeus) : Vendredi saint, Lundi de Pâques, Ascension (J+39), Lundi de Pentecôte (J+50), Fête-Dieu (J+60).
Ponts (si `ponts: true`) :
- le vendredi qui suit un jeudi férié (2 mai 2025, lendemains de l'Ascension et de la Fête-Dieu, 16 août 2024) ;
- le lundi qui précède un mardi férié (22 juin 2026).
Vérifié contre les documents « jours fériés » du foyer 2024, 2025 et 2026 : tous les jours ressortent, aucun manquant, aucun en trop (hors jours déjà couverts par une permanence).

### Permanences (`permanencesAnnee`)
Calculées automatiquement (`permanences_automatiques: true`) d'après les plannings 2018–2026 de la Mandchourie, qui suivent tous la même règle :
- **été** : commence le samedi compris entre le 13 et le 19 juillet, dure 23 jours (trois semaines pleines, jusqu'au dimanche) ;
- **hiver** : commence le samedi compris entre le 19 et le 25 décembre, dure 16 jours (jusqu'au dimanche qui suit le 3 janvier).

Vérification sur 9 étés (2018–2026) et 7 hivers (2018–2025) : toutes les dates correspondent. Seule exception trouvée : l'hiver 2021-2022 a commencé le vendredi 24 décembre au lieu du samedi 25 (Noël tombait un samedi). Pour ce genre de cas, la liste `permanences` accepte des périodes supplémentaires ou décalées, sous la forme `['2027-12-24','2028-01-09']`.

Résultats pour les prochaines années : été 2026 18 juillet – 9 août ; hiver 2026-27 19 décembre – 3 janvier ; été 2027 17 juillet – 8 août.

### Commande de l'écran
Si `window.fully` existe (Fully Kiosk avec « Enable JavaScript Interface » activé) : `fully.turnScreenOn()` / `fully.turnScreenOff()`, extinction réelle du rétroéclairage.
Sinon : un calque noir couvre la page (`body.nuit-active`).
Au rallumage, demande météo immédiate.

---

## 8. Conseils d'habillement (`conseiller`)

Température de référence : le **ressenti** (`apparent_temperature`) si `ressenti_pour_les_habits: true`, sinon la température réelle. Le chiffre affiché à l'écran est toujours la température réelle.

| Condition | Pictos | Phrases |
|---|---|---|
| ressenti < 8 (`seuil_manteau`) ou neige | manteau, bonnet | Mettez un manteau chaud. / Mettez un bonnet. |
| < 15 (`seuil_veste`) | veste | Mettez une veste. |
| < 21 (`seuil_pull`) | pull | Mettez un pull à longues manches. |
| ≥ 21 | t-shirt | Mettez un t-shirt. |
| pluie probable* | k-way remplace la veste ; + parapluie | Mettez un k-way. / Prenez un parapluie. |
| vent ≥ 40 km/h (`seuil_vent`) | info vent ; si t-shirt ou pull et pas de pluie : + veste | Il y a beaucoup de vent. / Prenez une veste. |
| ≥ 28 (`seuil_chaleur`), sans pluie | + casquette, eau | Mettez une casquette. / Buvez beaucoup d'eau. |
| ≥ 32 (`seuil_canicule`) | alerte rouge | Il fait très chaud. |
| matin et température ≤ 0 (`seuil_gel`) | alerte rouge | Il gèle. Attention, ça glisse. |

\* pluie probable = picto pluie/orage **ou** probabilité de précipitation ≥ 50 % (`seuil_pluie_pourcent`) sur la demi-journée. C'est le cas d'erreur le plus fréquent en pratique (matin sec, averse à 10h) ; la probabilité le couvre.

Les seuils sont des points de départ : à ajuster après le test avec les résidents et après le premier hiver.

Le mot « k‑way » est écrit avec un tiret insécable (U+2011) pour ne jamais être coupé sur deux lignes (règle FALC). La voix le reçoit avec un tiret normal.

---

## 9. Pictogrammes et images

### Pictogrammes livrés : Mulberry Symbols (actifs par défaut)
Le dossier `images/` contient 19 fichiers SVG et la page est réglée dessus (`images_dossier: 'images/'`, `images_extension: '.svg'`). Source : Mulberry Symbols (mulberrysymbols.org), banque de symboles de communication alternative, licence **CC BY-SA 4.0**, téléchargée depuis le dépôt GitHub officiel. Choix motivé : style unique et cohérent, dessins d'adultes, contour noir net, couleurs franches, licence qui permet même un usage commercial avec attribution ; et surtout accessible depuis l'environnement de développement (ARASAAC ne l'était pas ; ses pictos restent une alternative à tester, voir plus bas).

Correspondances : soleil ← sun · nuages ← cloudy · pluie ← rain · neige ← snow · orage ← thunder_storm · chaud ← hot_person · gel ← slippery · manteau ← coat · bonnet ← bobble_hat · veste ← jacket_2 · pull ← jumper · tshirt ← t-shirt · kway ← raincoat · parapluie ← umbrella · casquette ← cap · eau ← water.
Composés à partir de Mulberry (même licence) : eclaircies (sun + cloudy), brouillard (cloudy + lignes). Dessiné pour le projet dans le même style : vent.

**Attribution obligatoire** (fichier `images/ATTRIBUTION.txt`) : « Pictogrammes : Mulberry Symbols, Steve Lee, CC BY-SA 4.0 ». À mettre dans le dossier du projet ou au dos du cadre, pas sur l'écran des résidents.

### Pictos dessinés (secours)
Tous en SVG dans le fichier, aucun téléchargement. Couleurs codées : soleil jaune, pluie bleue, orage violet, manteau/veste bleu foncé, pull rouge, t-shirt vert, bonnet rose, k-way jaune. Adultes, sans style enfantin, un seul objet par picto.

Noms : `soleil, eclaircies, nuages, brouillard, pluie, neige, orage` (météo) · `vent, chaud, gel` (informations) · `manteau, bonnet, veste, pull, tshirt, kway, parapluie, casquette, eau` (vêtements).

### Remplacement par des fichiers
Régler `images_dossier: 'images/'` et déposer des fichiers `nom.png` (ou `.jpg` avec `images_extension`) dans ce dossier. Chaque picto est remplacé individuellement ; si le fichier manque ou ne charge pas, le dessin revient automatiquement (fonction `image()`, gestionnaire `onerror`).

### Banques recommandées (gratuites, reconnues en accessibilité cognitive)
- **ARASAAC** (arasaac.org) — la référence, gouvernement d'Aragon, licence CC BY-NC-SA. Utilisable par un foyer ; attribution obligatoire (une ligne au dos du cadre ou dans le dossier projet : « Pictogrammes : ARASAAC, Gouvernement d'Aragon, CC BY-NC-SA »). Mots à chercher : soleil, nuage, pluie, neige, orage, brouillard, vent, manteau, bonnet, veste, pull, t-shirt, imperméable, parapluie, casquette, boire.
- **Sclera** (sclera.be) — pictos noir/blanc épurés, gratuit.
- **Mulberry Symbols** — CC BY-SA.
- **Global Symbols / OpenSymbols** — moteur de recherche multi-banques.

Règle FALC : un seul style d'image dans tout le document. Ne pas mélanger un picto ARASAAC et un dessin maison sur le même écran si on peut l'éviter.

### Photos
Pour les vêtements, des photos des vraies affaires du foyer peuvent être plus reconnaissables : un objet par photo, fond blanc ou uni, cadrage carré, lumière du jour, même angle pour toutes. Pas d'images prises au hasard sur le web (droits).

---

## 10. Voix

### Ce qui est dit
Aucun chiffre. Phrases simples, dans l'ordre : temps qu'il va faire, informations, vêtements.
- Température : « Il va faire très froid. » / « Il va faire froid. » / « Il va faire doux. » / « Il va faire chaud. » (mêmes seuils que les vêtements ; ≥ canicule, c'est l'alerte « Il fait très chaud. » qui parle)
- Temps : « Il va neiger. » / « Il va y avoir de l'orage. » / « Il va pleuvoir. » / « Il va y avoir du soleil. » / « Il va y avoir du brouillard. » (nuages sans pluie : rien, pour rester court)
- Puis les informations et les phrases d'habillement telles qu'affichées.

Exemple : « Il va faire froid. Il va pleuvoir. Mettez un k-way. Prenez un parapluie. »

### Déclenchement
N'importe quel toucher sur la page (`click` sur `body`), plus Espace/Entrée au clavier. Un nouveau toucher pendant la lecture relance depuis le début (pas de superposition). Le bouton rond en bas à droite est un repère visuel ; il s'assombrit pendant la lecture.

### Deux modes
1. **Voix intégrée** (`audio_dossier: ''`) : `speechSynthesis` du navigateur, `fr-FR`, débit 0,85. Sur Android, installer/choisir la voix française Google (Paramètres → Synthèse vocale) : nettement meilleure que la voix par défaut.
2. **Phrases enregistrées** (`audio_dossier: 'audio/'`) : un fichier MP3 par phrase, nommé par le slug de la phrase (minuscules, sans accents, tirets ; ex. `il-va-pleuvoir.mp3`, `mettez-un-k-way.mp3`). Les morceaux sont enchaînés avec 350 ms de pause. Si un fichier manque ou ne peut pas être lu, la voix intégrée prend le relais pour toute la phrase.

### `generer-audio.py`
Génère les 22 fichiers avec ElevenLabs (modèle `eleven_multilingual_v2`, voix « Charlotte » par défaut, changeable avec `--voix <id>`). Environ 500 caractères : le plan gratuit suffit. Clé dans la variable d'environnement `ELEVENLABS_API_KEY`. Les fichiers existants ne sont pas régénérés. La liste des phrases du script doit rester identique à celle de la page.

### Contrainte Android
Le son n'est autorisé qu'après une action de l'utilisateur au relâchement (`click`), jamais au simple `pointerdown`. Dans Fully Kiosk, activer « Autoplay Audio » supprime aussi le blocage du tout premier appui après redémarrage.

---

## 11. Mode démonstration

Ajouter `?demo=<situation>` à l'adresse. Le réseau et la commande d'écran sont désactivés, le pied de page affiche « Mode démonstration ».

| Situation | Code | Temp | Vent | Pluie % |
|---|---|---|---|---|
| soleil | 0 | 24 | 10 | – |
| eclaircies | 2 | 18 | 15 | 70 (déclenche le k-way malgré le picto) |
| nuages | 3 | 12 | 12 | – |
| brouillard | 45 | 6 | 5 | – |
| pluie | 63 | 9 | 20 | – |
| neige | 73 | −1 | 15 | – |
| orage | 95 | 22 | 35 | – |
| vent | 2 | 16 | 55 | – |
| canicule | 0 | 34 | 8 | – |
| gel | 1 | −4 | 10 | – |

Usage prévu : le test FALC avec les résidents (§14), sans attendre qu'il neige.

---

## 12. Réglages (`REGLAGES`, en haut du script)

C'est la seule partie du fichier qu'un collègue doit modifier.

| Clé | Valeur actuelle | Rôle |
|---|---|---|
| `latitude`, `longitude` | 47.3639, 7.3448 | Rue du Pont-Neuf 4, Delémont |
| `rafraichir_minutes` | 30 | cadence normale |
| `creneau_critique` | 06:00–07:30, 5 min | insistance avant le déjeuner |
| `precharge_soir` | 21:25 | dernière demande avant la veille |
| `modele` | `meteoswiss_icon_seamless` | modèle MétéoSuisse ; `''` = mondial |
| `ressenti_pour_les_habits` | true | conseils sur le ressenti |
| `seuil_pluie_pourcent` | 50 | probabilité qui sort le k-way |
| `heure_matin` / `heure_apres_midi` | 8 / 14 | heures de référence |
| `bascule` | 11:30 | passage matin → après-midi |
| `horaires` | voir §7 | plages d'allumage par type de jour |
| `permanences_automatiques` | true | été et hiver calculés par la règle du foyer |
| `permanences` | `[]` | exceptions décidées par la direction |
| `ponts` | true | vendredi après un jeudi férié, lundi avant un mardi férié |
| `toussaint` | true | 1er novembre férié (confirmé par Ludovic) |
| `gerer_l_ecran` | true | la page commande l'écran |
| `recharger_a` | 12:00 | rechargement quotidien |
| `animations` | false | FALC |
| `voix` | true | lecture à voix haute |
| `audio_dossier` | `''` | phrases enregistrées |
| `images_dossier` / `images_extension` | `''` / `.png` | pictos de remplacement |
| `seuil_manteau` … `seuil_vent` | 8 / 15 / 21 / 28 / 32 / 0 / 40 | seuils d'habillement et d'alerte |

---

## 13. Installation sur la tablette

1. **Héberger la page** : GitHub Pages (dépôt public, fichier à la racine) ou tout serveur web. Le rechargement quotidien s'appuie sur cette adresse.
2. **Tablette** : Android 5 minimum. Vérifier l'état de la batterie (gonflement) avant fixation. Rotation bloquée en paysage, luminosité adaptative désactivée, mises à jour automatiques coupées, compte Google retiré si inutile.
3. **Fully Kiosk Browser** (gratuit) :
   - adresse de démarrage = l'adresse de la page ;
   - **Enable JavaScript Interface** (Advanced Web Settings) : indispensable pour l'extinction réelle de l'écran ;
   - **Autoplay Audio** : recommandé pour la voix ;
   - **désactiver** la planification d'écran de Fully : la page s'en charge ;
   - garder la page chargée en veille (par défaut).
4. **Wi-Fi du foyer** : réseau invité si possible ; la page n'envoie aucune donnée, ne demande aucun compte. Le retour du Wi-Fi le matin idéalement avant 6h.
5. **Fixation** : support mural à hauteur des yeux, câble en goulotte, alimentation hors de portée.
6. **Vérification** : le pied de page affiche une heure de mise à jour du jour et « MétéoSuisse ».

---

## 14. Règles FALC appliquées (Inclusion Europe, « L'information pour tous »)

- Police sans empattement, grande, pas d'italique, pas de majuscules entières, pas d'ombre ni de contour, pas de texte en couleur.
- Une idée par phrase, une phrase par ligne, texte aligné à gauche, jamais un mot coupé sur deux lignes.
- Vouvoiement (« Mettez… »), phrases positives, verbes d'action.
- Dates en entier, nombres en chiffres.
- Chaque information a un picto **et** un mot ; le même picto pour la même chose partout ; images d'adultes.
- Tout tient sur un écran, rien ne défile, rien ne bouge, rien n'apparaît tout seul.
- Seulement l'information nécessaire : la ligne vent n'existe que s'il y a du vent, l'alerte que s'il y a une alerte.
- Pas de graphique, pas d'heure par heure, pas de plusieurs jours.
- Lecture à voix haute disponible (recommandation « lecteur d'écran »).
- **Règle d'or non déléguable au code** : impliquer les personnes concernées. Le test avec les résidents (ci-dessous) est la validation FALC, pas ce document.

### Protocole de test avec les résidents
Deux ou trois résidents, un par un, tablette en mode `?demo=`. Deux questions seulement : « Qu'est-ce que tu vois ? » puis « Qu'est-ce que tu mets aujourd'hui ? ». Noter ce qui est nommé spontanément, sans aider. Ce qui n'est pas nommé est à changer (picto, mot, seuil). Comparer pictos dessinés et photos réelles. Une demi-heure suffit.

---

## 15. Cadre éducatif (à garder en tête lors de toute évolution)

- **Information, pas injonction.** L'équipe ne renvoie jamais à l'écran comme argument. Un résident qui regarde l'écran et sort quand même en t-shirt a fait un choix éclairé.
- **Un rôle plutôt qu'un affichage** : un résident « responsable météo » du jour, qui écoute et annonce aux autres au petit-déjeuner ; tournus.
- **Le corps avant l'écran** : lier le picto à la sensation (fenêtre ouverte le matin), sinon l'outil devient une béquille.
- **Générique vs individuel** : l'écran donne une règle pour tous ; les adaptations personnelles (« moi j'ai toujours froid ») se travaillent dans le projet individuel, éventuellement avec une carte perso au vestiaire.
- **Résidents anxieux** : l'annonce d'orage peut inquiéter dès le matin ; adoucir ou retirer selon le groupe.
- **PdV** : objectif observable « choisit une tenue adaptée à la météo sans sollicitation », relevé avant/après sur un mois.
- **Oser enlever** : si un résident n'a plus besoin de l'écran, l'objectif est atteint.
- **Ne pas surcharger** : pas de menu, d'activités ni d'anniversaires sur cet écran. Si besoin, un deuxième écran.

---

## 16. Ce qui reste à faire (état au 9 septembre 2026)

1. Tester la page sur un téléphone avec Internet ; vérifier « MétéoSuisse » dans le pied de page (non testable depuis l'environnement de développement, réseau restreint).
2. Test FALC avec les résidents (§14), puis ajustement des seuils, des mots, et choix pictos/photos.
3. Information au colloque ; accord pour la fixation et l'accès Wi-Fi.
4. Hébergement, installation Fully Kiosk, réglages Android.
5. Chaque décembre, vérifier que les dates de permanence publiées par la direction correspondent au calcul ; sinon saisir l'exception dans `permanences`.
6. Facultatif : enregistrer les 22 phrases avec `generer-audio-edge.py` (gratuit) ou ElevenLabs, ou installer la voix française Google.
7. Facultatif : comparer avec les pictos ARASAAC (à télécharger à la main depuis arasaac.org, mêmes noms de fichiers) si les résidents connaissent déjà cette banque.
8. Revoir les seuils après le premier hiver.
9. ~~Fiche « mode d'emploi »~~ faite : `mode-d-emploi-equipe.html`.

---

## 17. Tests effectués

- Syntaxe JavaScript validée à chaque modification.
- Rendu dans Chromium headless (Playwright), paysage 1280×800 et portrait 800×1280, pour les 10 situations de démonstration et le cas sans données : aucune erreur console, aucun débordement.
- Fériés 2025 calculés = liste du foyer (15 jours), aucun manquant ; fériés 2026 = document du foyer (13 jours), aucun manquant, aucun en trop ; 16 août 2024 et 1er novembre 2024 reconnus.
- Permanences calculées = plannings du foyer pour les étés 2018 à 2026 et les hivers 2018 à 2025, sans écart (une seule exception historique, hiver 2021-22, documentée).
- Type de jour vérifié : 2 mai 2025 → weekend (pont), 25 juillet 2025 → permanence, 24 décembre 2025 → permanence, 10 septembre 2025 → semaine, 3 avril 2026 (Vendredi saint) → weekend.
- Repli des images : dossier configuré sans fichiers → tous les pictos dessinés réapparaissent, aucune image cassée.
- Déclenchement de la voix : deux touchers tactiles simulés sur la page → deux lectures ; aucun appel sur `pointerdown` seul.
- Non testé ici : appel réel à Open-Meteo/MétéoSuisse, voix Android, commande d'écran Fully Kiosk. À valider sur la tablette.

---

## 18. Pièges connus et choses à ne pas faire

- Ne pas réactiver `pointerdown` pour la voix : Android bloque le son.
- Ne pas mettre la clé ElevenLabs dans la page : la page est publique.
- Ne pas ajouter d'informations à l'écran (menu, activités…) : chaque ajout dégrade la lisibilité de la météo.
- Ne pas remettre les animations sans test avec les résidents.
- Ne pas changer la liste des phrases dans la page sans mettre à jour `generer-audio.py` et régénérer les MP3 (les noms de fichiers dérivent des phrases).
- Ne pas remplacer `localStorage` : c'est ce qui permet l'affichage du matin sans Wi-Fi.
- Ne pas laisser Fully Kiosk et la page gérer tous les deux les horaires d'écran.
- Les données du personnel et des résidents lues dans les plannings 2014–2026 n'ont servi qu'à déduire les horaires ; aucune n'est dans la page et aucune ne doit y entrer.
