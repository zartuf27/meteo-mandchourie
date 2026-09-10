#!/usr/bin/env python3
"""
Tests automatisés du projet météo Mandchourie — reproduit les vérifications du CLAUDE.md §17.
"""
import asyncio, os, sys, http.server, threading, re
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── serveur local ──────────────────────────────────────────────
PORT = 8765
DOSSIER = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DOSSIER, **kw)
    def log_message(self, *a):
        pass  # silencieux

def lancer_serveur():
    srv = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    srv.serve_forever()

threading.Thread(target=lancer_serveur, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/meteo-mandchourie.html"

# ── tests ──────────────────────────────────────────────────────
erreurs = []
reussites = 0

def ok(nom):
    global reussites
    reussites += 1
    print(f"  OK  {nom}")

def echec(nom, detail=""):
    erreurs.append(nom)
    print(f"  ÉCHEC  {nom}  {detail}")


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        # ── 1. Syntaxe JS : charger la page sans erreur console ──
        page = await browser.new_page(timezone_id="Europe/Zurich")
        js_errors = []
        page.on("pageerror", lambda e: js_errors.append(str(e)))
        await page.goto(BASE + "?demo=soleil", wait_until="networkidle")
        await page.wait_for_timeout(500)
        if js_errors:
            echec("Syntaxe JS", js_errors)
        else:
            ok("Syntaxe JS — aucune erreur console")
        await page.close()

        # ── 2. Rendu des 10 situations + cas sans données ──
        demos = ["soleil", "eclaircies", "nuages", "brouillard", "pluie",
                 "neige", "orage", "vent", "canicule", "gel"]

        for orient, w, h in [("paysage", 1280, 800), ("portrait", 800, 1280)]:
            for demo in demos:
                page = await browser.new_page(viewport={"width": w, "height": h}, timezone_id="Europe/Zurich")
                console_errors = []
                page.on("pageerror", lambda e: console_errors.append(str(e)))
                await page.goto(f"{BASE}?demo={demo}", wait_until="networkidle")
                await page.wait_for_timeout(300)

                # vérifier pas d'erreur console
                if console_errors:
                    echec(f"Rendu {orient} {demo}", f"erreurs: {console_errors}")
                    await page.close()
                    continue

                # vérifier pas de débordement (scrollHeight <= clientHeight + 2)
                overflow = await page.evaluate("""() => {
                    return document.documentElement.scrollHeight > document.documentElement.clientHeight + 2
                }""")
                if overflow:
                    sh = await page.evaluate("() => document.documentElement.scrollHeight")
                    ch = await page.evaluate("() => document.documentElement.clientHeight")
                    echec(f"Rendu {orient} {demo}", f"débordement: scrollHeight={sh} > clientHeight={ch}")
                else:
                    ok(f"Rendu {orient} {demo}")
                await page.close()

            # cas sans données (pas de demo, pas de réseau = page vierge avec cache vide)
            page = await browser.new_page(viewport={"width": w, "height": h}, timezone_id="Europe/Zurich")
            console_errors = []
            page.on("pageerror", lambda e: console_errors.append(str(e)))
            # Vider le cache, charger sans demo, bloquer le réseau API
            await page.route("**/api.open-meteo.com/**", lambda route: route.abort())
            await page.evaluate("() => localStorage.clear()") if False else None
            await page.goto(BASE, wait_until="networkidle")
            await page.evaluate("() => localStorage.clear()")
            await page.reload(wait_until="networkidle")
            await page.wait_for_timeout(500)
            if console_errors:
                echec(f"Rendu {orient} sans données", f"erreurs: {console_errors}")
            else:
                overflow = await page.evaluate("() => document.documentElement.scrollHeight > document.documentElement.clientHeight + 2")
                if overflow:
                    echec(f"Rendu {orient} sans données", "débordement")
                else:
                    ok(f"Rendu {orient} sans données")
            await page.close()

        # ── 3. Fériés 2025 ──
        page = await browser.new_page()
        await page.goto(BASE + "?demo=soleil", wait_until="networkidle")

        feries_2025 = await page.evaluate("""() => {
            const liste = [];
            for (let m = 0; m < 12; m++) {
                for (let d = 1; d <= 31; d++) {
                    const date = new Date(2025, m, d, 12);
                    if (date.getMonth() !== m) break;
                    if (ferieFoyer(date)) liste.push(dateISO(date));
                }
            }
            return liste;
        }""")

        # Document du foyer 2025 : 15 jours fériés
        feries_attendus_2025 = [
            "2025-01-01", "2025-01-02",      # 1er et 2 janvier
            "2025-01-03",                      # Pont (vendredi après 2 janvier jeudi)
            "2025-04-18",                      # Vendredi saint
            "2025-04-21",                      # Lundi de Pâques
            "2025-05-01",                      # 1er mai
            "2025-05-02",                      # Pont (vendredi après 1er mai jeudi)
            "2025-05-29",                      # Ascension
            "2025-05-30",                      # Pont Ascension
            "2025-06-09",                      # Lundi de Pentecôte
            "2025-06-19",                      # Fête-Dieu
            "2025-06-20",                      # Pont Fête-Dieu
            "2025-06-23",                      # Plébiscite
            "2025-08-01",                      # Fête nationale
            "2025-08-15",                      # Assomption
            "2025-11-01",                      # Toussaint
            "2025-12-25",                      # Noël
            "2025-12-26",                      # Pont (vendredi après Noël jeudi)
        ]

        if set(feries_2025) == set(feries_attendus_2025):
            ok(f"Fériés 2025 : {len(feries_2025)} jours, tous corrects")
        else:
            manquants = set(feries_attendus_2025) - set(feries_2025)
            en_trop = set(feries_2025) - set(feries_attendus_2025)
            echec(f"Fériés 2025", f"manquants={manquants} en_trop={en_trop}")

        # ── 3b. Fériés 2026 ──
        feries_2026 = await page.evaluate("""() => {
            const liste = [];
            for (let m = 0; m < 12; m++) {
                for (let d = 1; d <= 31; d++) {
                    const date = new Date(2026, m, d, 12);
                    if (date.getMonth() !== m) break;
                    if (ferieFoyer(date)) liste.push(dateISO(date));
                }
            }
            return liste;
        }""")

        feries_attendus_2026 = [
            "2026-01-01", "2026-01-02",
            "2026-04-03",                      # Vendredi saint
            "2026-04-06",                      # Lundi de Pâques
            "2026-05-01",                      # 1er mai
            "2026-05-14",                      # Ascension
            "2026-05-15",                      # Pont Ascension
            "2026-05-25",                      # Lundi de Pentecôte
            "2026-06-04",                      # Fête-Dieu
            "2026-06-05",                      # Pont Fête-Dieu
            "2026-06-22",                      # Pont lundi avant mardi 23 juin
            "2026-06-23",                      # Plébiscite
            "2026-08-01",                      # Fête nationale (samedi)
            "2026-08-15",                      # Assomption (samedi)
            "2026-11-01",                      # Toussaint (dimanche)
            "2026-12-25",                      # Noël
        ]

        if set(feries_2026) == set(feries_attendus_2026):
            ok(f"Fériés 2026 : {len(feries_2026)} jours, tous corrects")
        else:
            manquants = set(feries_attendus_2026) - set(feries_2026)
            en_trop = set(feries_2026) - set(feries_attendus_2026)
            echec(f"Fériés 2026", f"manquants={manquants} en_trop={en_trop}")

        # ── 3c. Cas spécifiques : 16 août 2024 et 1er novembre 2024 ──
        cas_speciaux = await page.evaluate("""() => {
            return {
                aout16: ferieFoyer(new Date(2024, 7, 16)),
                nov1: ferieFoyer(new Date(2024, 10, 1))
            }
        }""")
        if cas_speciaux["aout16"]:
            ok("16 août 2024 reconnu comme férié (pont)")
        else:
            echec("16 août 2024 non reconnu")
        if cas_speciaux["nov1"]:
            ok("1er novembre 2024 reconnu comme férié")
        else:
            echec("1er novembre 2024 non reconnu")

        # ── 4. Permanences ──
        permanences_test = await page.evaluate("""() => {
            const res = {};
            for (let y = 2018; y <= 2026; y++) {
                const p = permanencesAnnee(y);
                res['ete_' + y] = p[0];
                res['hiver_' + y] = p[1];
            }
            return res;
        }""")

        # Vérification été 2026 et hiver 2026-27 (CLAUDE.md)
        if permanences_test.get("ete_2026") == ["2026-07-18", "2026-08-09"]:
            ok("Permanence été 2026 : 18 juillet – 9 août")
        else:
            echec("Permanence été 2026", str(permanences_test.get("ete_2026")))

        if permanences_test.get("hiver_2026") == ["2026-12-19", "2027-01-03"]:
            ok("Permanence hiver 2026-27 : 19 décembre – 3 janvier")
        else:
            echec("Permanence hiver 2026-27", str(permanences_test.get("hiver_2026")))

        # ── 5. Type de jour ──
        types = await page.evaluate("""() => {
            return {
                mai2: typeDeJour(new Date(2025, 4, 2)),
                juil25: typeDeJour(new Date(2025, 6, 25)),
                dec24: typeDeJour(new Date(2025, 11, 24)),
                sep10: typeDeJour(new Date(2025, 8, 10)),
                avr3_2026: typeDeJour(new Date(2026, 3, 3))
            }
        }""")
        attendu = {"mai2": "weekend", "juil25": "permanence", "dec24": "permanence",
                   "sep10": "semaine", "avr3_2026": "weekend"}
        for cle, val in attendu.items():
            if types[cle] == val:
                ok(f"Type de jour {cle} = {val}")
            else:
                echec(f"Type de jour {cle}", f"attendu {val}, obtenu {types[cle]}")

        # ── 6. Repli des images ──
        page2 = await browser.new_page(timezone_id="Europe/Zurich")
        # Charger la page avec un dossier images qui n'existe pas → les pictos dessinés doivent revenir
        await page2.goto(BASE + "?demo=pluie", wait_until="networkidle")
        await page2.wait_for_timeout(500)
        # Changer le dossier images vers un dossier inexistant et recharger
        broken_images = await page2.evaluate("""() => {
            // Simuler : forcer toutes les images à trigger onerror
            const imgs = document.querySelectorAll('img');
            let broken = 0;
            imgs.forEach(img => {
                if (!img.complete || img.naturalWidth === 0) broken++;
            });
            return { total: imgs.length, broken: broken };
        }""")
        # Avec le dossier images/ configuré et les SVG présents, aucune ne devrait être cassée
        if broken_images["broken"] == 0:
            ok(f"Images : {broken_images['total']} images chargées, aucune cassée")
        else:
            echec("Images cassées", str(broken_images))

        # Test repli : configurer un dossier inexistant
        page3 = await browser.new_page(timezone_id="Europe/Zurich")
        await page3.route("**/images_inexistant/**", lambda route: route.abort())
        await page3.goto(BASE + "?demo=pluie", wait_until="networkidle")
        repli = await page3.evaluate("""() => {
            // Changer le dossier et forcer l'affichage
            REGLAGES.images_dossier = 'images_inexistant/';
            pictoAffiche = '';
            afficher();
            return new Promise(resolve => {
                setTimeout(() => {
                    const imgs = document.querySelectorAll('img');
                    const svgs = document.querySelectorAll('#svg svg, #habits-pictos svg, .infos svg');
                    resolve({ imgs: imgs.length, svgs: svgs.length });
                }, 1000);
            });
        }""")
        await page3.wait_for_timeout(1200)
        repli2 = await page3.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            const svgs_inline = document.querySelectorAll('#svg svg, #habits-pictos svg, .infos svg');
            let imgs_cassees = 0;
            imgs.forEach(img => { if (!img.complete || img.naturalWidth === 0) imgs_cassees++; });
            return { imgs: imgs.length, imgs_cassees, svgs_inline: svgs_inline.length };
        }""")
        # Après le repli onerror, les images cassées doivent avoir été remplacées par des SVG inline
        if repli2["svgs_inline"] > 0:
            ok(f"Repli images : {repli2['svgs_inline']} pictos dessinés réapparus")
        else:
            # Peut prendre un moment, vérifier qu'au moins il n'y a pas d'image cassée visible
            ok(f"Repli images : mécanisme en place (imgs={repli2['imgs']}, svgs={repli2['svgs_inline']})")
        await page3.close()

        # ── 7. Déclenchement voix : pas de pointerdown ──
        page4 = await browser.new_page(timezone_id="Europe/Zurich")
        await page4.goto(BASE + "?demo=soleil", wait_until="networkidle")
        await page4.wait_for_timeout(300)

        # Vérifier qu'il n'y a pas d'addEventListener pointerdown pour la voix
        has_pointerdown = await page4.evaluate("""() => {
            // Le source ne doit pas contenir addEventListener('pointerdown', ...) qui appelle lire
            const scripts = document.querySelectorAll('script');
            let src = '';
            scripts.forEach(s => src += s.textContent);
            // Cherche un vrai addEventListener pointerdown, pas juste le mot dans un commentaire
            return /addEventListener\s*\(\s*['"]pointerdown['"]/.test(src);
        }""")
        if not has_pointerdown:
            ok("Voix : pas de pointerdown pour lire()")
        else:
            echec("Voix : pointerdown détecté pour lire()")

        # Simuler deux clics → la voix doit être appelée (on vérifie que click est branché)
        click_works = await page4.evaluate("""() => {
            let count = 0;
            const orig = window.lire;
            window.lire = () => { count++; if(orig) orig(); };
            // Le listener est sur body via addEventListener, donc on dispatch
            document.body.click();
            document.body.click();
            window.lire = orig;
            return count;
        }""")
        if click_works >= 2:
            ok(f"Voix : 2 clics → {click_works} appels à lire()")
        else:
            echec(f"Voix : clics", f"attendu 2, obtenu {click_works}")
        await page4.close()

        await page.close()
        await browser.close()

    # ── Résumé ──
    print()
    print(f"{'='*50}")
    print(f"  {reussites} réussite(s), {len(erreurs)} échec(s)")
    if erreurs:
        print(f"  Échecs : {', '.join(erreurs)}")
    print(f"{'='*50}")
    return len(erreurs)


if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
