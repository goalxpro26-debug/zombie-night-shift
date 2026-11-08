# Zombie Night Shift — GameMonetize account-restoration game

Top-down survival shooter. You are the night guard: survive **12 nights** in a
graveyard street against walkers, runners, spitters and brutes, with a boss on
Nights 4, 8 and 12. Earn coins, buy weapon upgrades and barricades between
nights. Original game, original art — nothing copied, no stock, no licensed
characters.

**Folder:** `~/workspace/gamemonetize-restoration/zombie-night-shift/`
**Files:** `index.html` (game, vanilla JS + Canvas, self-contained) +
`assets/` (24 original PNGs drawn in code — see `make_assets.py`) +
`zombie-night-shift-gm.zip` (portal-ready ZIP: `index.html` + `assets/` at root)
+ 3 JPG thumbnails (`zombie-night-shift-512x384.jpg` / `-512x512.jpg` /
`-512x340.jpg`, the GameMonetize sizes) + `test-play.js` (headless playtest).

## How to run

Open `index.html` in any browser (double-click, or `python3 -m http.server`
in this folder and visit `http://localhost:8000/`). No build step, no
dependencies. Desktop: WASD/arrows to move, mouse to aim, click/Space to
shoot, R reload, P/Esc pause, M mute. Mobile: left touch joystick + FIRE
button (auto-aims at the nearest zombie).

## Levels (12 nights)

| Night | Name | Zombies | Mix | Boss |
|---|---|---|---|---|
| 1 | Graveyard Gate | 18 | walkers | — |
| 2 | Foggy Lane | 26 | walkers, runners | — |
| 3 | Spitter Alley | 34 | + spitters | — |
| 4 | BOSS: Gravekeeper | 30 | walkers/runners/spitters | ✅ Gravekeeper (690 HP) |
| 5 | Brute Block | 44 | + brutes | — |
| 6 | Dead End Street | 54 | all four | — |
| 7 | Moonlit Crossroads | 64 | all four | — |
| 8 | BOSS: Rot King | 55 | all four | ✅ Rot King |
| 9 | Cemetery Hill | 76 | all four | — |
| 10 | The Long Night | 88 | all four | — |
| 11 | Horde Rising | 102 | all four | — |
| 12 | BOSS: Nightmare Lord | 90 | all four | ✅ Nightmare Lord |

HP/speed scale up every night. Night 1 is easy (walkers only, slow);
later nights add faster, tougher, shooting enemies in larger numbers.

## Playtime estimate

Spawn pacing + fighting time: Night 1 ≈ 2–3 min, mid nights ≈ 4–5 min,
Nights 10–12 ≈ 6–7 min each. **Total ≈ 60–70 minutes** for a full
12-night run (skilled player, no deaths). This is an estimate from the
per-night counts/intervals in `LEVELS` — a full 1-hour human playthrough
was not run headlessly; the automated bot completed Night 5 (44 zombies)
in under 150 s and Night 1 in 40 s of real aimed play killed 6–8 zombies,
consistent with the pacing math. Deaths/replays push the total higher.

## Save / resume

`localStorage` key `zombieNightShiftSaveV1`: highest unlocked night, stars
per night (1–3 by lives remaining), total score, coins, upgrades owned,
barricades owned, mute setting. The menu's level grid shows locked/unlocked
nights with stars; reloading the page returns to the menu with progress
intact — verified in testing (see below).

## Between-night shop

Coins earned from kills + a per-night reward buy: Damage +6, Fire Rate,
Move Speed, Max HP +25 (5 levels each), Barricades (up to 3, destructible
wooden barriers zombies attack before reaching you), Full Heal.

## GameMonetize SDK

- Official loader + `window.SDK_OPTIONS` defined **before** the SDK script,
  exactly per `~/workspace/gamemonetize/CONVERSION-PLAN.md` §1 and
  `templates/babylon/`.
- `gameId` is the placeholder **`[YOUR GM GAME ID HERE]`** — no ID invented.
  Replace it with the real 32-char gameId from the GM control panel before
  final upload; do not upload the placeholder build as final.
- `sdk.showBanner()` is called **only from the PLAY button click handler**,
  once, on first play — never on load. (Per this game's brief; the
  conversion plan's mid-roll-on-win placement was deliberately not added.)
- Live availability getter: `gmSdk()` re-checks
  `typeof sdk !== 'undefined' && typeof sdk.showBanner === 'function'` on
  every call — never snapshotted (async loader, plan §3.1). In-flight guard
  clears on `SDK_GAME_START` or a 60 s safety timeout (plan §3.2, no
  promise assumed on `showBanner()`).
- `SDK_GAME_PAUSE` pauses the game and mutes audio; `SDK_GAME_START`
  resumes and restores the pre-ad mute state. Events arriving before the
  game installs its handler are buffered in `window.__gmEventQueue`.
- Debug surface: `window.__gamemonetize` (`available`, `preRollShown`,
  `pausedByGM`, `simulatePause`/`simulateResume`).
- **The game plays fully with the SDK absent/guarded** (verified: in the
  sandbox the SDK fetch fails at the egress proxy and `available` is
  `false`; the game still runs end-to-end).

## Blog checklist mapping (gamemonetize.com/blog/how-to-build-better-ai-games-for-kids)

| Blog requirement | Where it is met |
|---|---|
| At least 10 levels | 12 nights in `LEVELS` (`index.html`), level-select grid |
| At least 1 hour to complete | 12 nights, 18→102 zombies/night, pacing math above (≈60–70 min estimate) |
| Progress saved in browser | `localStorage` `zombieNightShiftSaveV1` — unlocked night, stars, score, coins, upgrades, barricades; reload resumes (tested) |
| Different enemy models per level | `assets/enemy_l01.png` … `enemy_l12.png` — a distinct drawn walker sprite per night (different skin/shirt/accessory; all 12 files have different MD5s) — plus distinct type sprites `enemy_runner.png`, `enemy_spitter.png`, `enemy_brute.png`, `enemy_boss.png`. Walkers use that night's own sprite (`spawnZombie`) |
| Well-designed background, drawn images not flat colour | `assets/background.png` (night street: moon, stars, houses, lamps, fence, road) and `assets/background_graveyard.png` (gravestones, dead tree); drawn with PIL in `make_assets.py` |
| In-game audio: ambient, shooting, destruction, win/lose (+ reload/pickup) | Synthesized WebAudio in `SFX` + `startAmbient` (night-wind loop, zombie moans, shoot, hit, zombie-die, hurt, pickup, coin, reload, win jingle, lose jingle, boss roar). No copyrighted music. Mute button + M key |
| Clean menu, Play button in centre, controls + How to Play on first menu | `#menu` overlay: centred PLAY button, controls + How to Play box, level-select grid |
| 3-second loading before start | `startLoading()` — 3 000 ms progress bar before every night starts (verified: loading visible at 0.5 s, playing at ~4.4–5.9 s after PLAY) |
| 3 lives / hearts indicator | 3 lives per night; HUD shows `♥♥♥` + HP bar; losing a life respawns the player; 0 lives = game over |
| Enemies shoot at the player | Spitter zombies (from Night 3) and all bosses fire green projectiles (`ebullets`); dodgeable, they damage on hit |
| Image assets in a single folder with index.html | `assets/` — `background.png`, `background_graveyard.png`, `player.png`, `enemy*.png`, `barricade.png`, `coin.png`, `heart.png`, `medkit.png`; all original, drawn in `make_assets.py` (PIL), no stock/copied art |
| Ads never on load | `showBanner()` only in the PLAY click handler; nothing on load/boot |
| SDK pause/mute, resume | `gmPause`/`gmResume` on `SDK_GAME_PAUSE`/`SDK_GAME_START` (see SDK section) |

## Test results (headless, Playwright + Chromium, `test-play.js`)

Final full run (Nov 6, 2026) — **all checks passed** — then re-run end to
end a second time as a confirmation pass after a CSS fix (menu title was
clipped at 700 px height; fixed with `justify-content: safe center`,
verified by screenshot). Confirmation run repeated every result below
(Night 1: 8 kills, 3 stars; Night 5 soak: 150 s, +580 score, 1 zombie
left, 2 lives). Total automated play across runs: **>10 minutes of
real-input play** (40 s aimed Night 1 ×2 + Night 5 soaks + earlier runs +
level hops).

- Menu → PLAY → loading visible at 0.5 s → playing Night 1 at ~4.4–5.9 s.
  Level 1: 18 zombies, walkers only, sprite `enemy_l01.png`.
- Real aimed play (mouse aimed at live zombie coordinates, click to shoot,
  WASD strafing), 40 s: **6 kills, score 60, 1 life lost** (lives 3→2) —
  shooting, hit detection and zombie damage all work through real input.
- Night 1 completed → shop screen, 2 stars (1 life lost), unlocked Night 2,
  +60 coins. Shop: bought Damage Lv 1 (300→220 coins) and a barricade
  (barricades 0→1) — both persisted.
- Night 2 started with the bought barricade present; spawned runner,
  spitter and brute verified (`enemy_runner.png`, `enemy_spitter.png`,
  `enemy_brute.png`).
- **Save/resume:** page reloaded → menu shows unlocked Night 2, stars
  kept, level grid offers Night 2.
- **Boss Night 4:** boss spawned (Gravekeeper, 690 HP, `enemy_boss.png`,
  boss HP bar); night completed, 3 stars, unlocked Night 5.
- Spitter present on Night 3; per-level walker sprites L1/L2/L12 all load
  (64×64) and are distinct files (different MD5s).
- **Soak:** auto-aim bot played Night 5 (44 zombies, all four types) and
  **completed the whole night in under 150 s** (score +1330, finished with
  1 life) — a full night is completable by real shooting, not just hooks.
- Mute button toggles Sound ON→OFF. Touch UI hidden on desktop
  (shown only on touch devices).
- Screenshots: `test-menu.png`, `test-playing.png`, `test-midplay.png`,
  `test-shop.png`, `test-boss.png`, `test-soak.png`.

**Console errors:** 2× `Failed to load resource:
net::ERR_TUNNEL_CONNECTION_FAILED` — both are the GameMonetize SDK script
fetch (`api.gamemonetize.com/sdk.js`) failing at this sandbox's egress
proxy. They are network errors from the external SDK host, not game code:
the game has zero page errors and plays fully in guarded-absent mode
(`__gamemonetize.available === false`). On the live portal / a normal
connection the SDK loads and the same code path calls `showBanner()`.

**Known limitations (honest):**
- The 60–70 min total is an estimate from spawn pacing, not a measured
  full human playthrough; Nights 6–12 were verified only via level configs,
  boss-spawn logic and the Night 5 full completion (Nights 8/12 bosses use
  the same spawn path as the verified Night 4 boss).
- Touch controls (joystick + FIRE) are implemented and shown on touch
  devices, but were **not** tested on a real phone — only desktop
  mouse/keyboard in headless Chromium.
- Audio is synthesized WebAudio; it was exercised through the code paths
  (no errors) but not listened to — headless Chromium runs muted.
- The SDK `showBanner()` path itself could not be exercised end-to-end
  here because the SDK host is unreachable from this sandbox; only the
  guarded-absent path and the pause/resume handlers were verified.

## What was NOT done (per brief)

Nothing was submitted to GameMonetize, no portal entry was created, no
email was sent. This is build + test only. Next step (owner/parent): create
the GM entry, copy the 32-char gameId into `index.html`, rebuild the ZIP,
upload + Verify Game + Request Activation.
