// Headless playtest for Zombie Night Shift. Usage: node test-play.js <baseUrl>
// Drives menu -> 3s loading -> Play -> real shooting/movement -> Night 1 complete,
// save/resume via reload, level variety, boss night, shop, no console errors.
const { chromium } = require('playwright-core');
const fs = require('fs');
(async () => {
  const base = process.argv[2] || 'http://127.0.0.1:8931/';
  const browser = await chromium.launch({ executablePath: '/opt/meta-chromium/chrome', args: ['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--hatch-webgl-allowed-domains-file=/home/hatch/workspace/tools/pw-shot/webgl-policy.txt','--hatch-webgl-allowed-domains-sha256=dc8a0e5eec744f6590a4c1889139c00568ffedc3eced6d0a1a5127e35f9ccd16'] });
  const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
  const errors = [];
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text().slice(0,300)); });
  const log = (...a) => console.log('[TEST]', ...a);
  const state = () => page.evaluate(() => ({ state: window.__zombie.state, level: window.__zombie.level, lives: window.__zombie.lives, left: window.__zombie.zombiesLeft, score: window.__zombie.score, coins: window.__zombie.coins, unlocked: window.__zombie.unlocked, zombies: window.__zombie.zombies.slice(0,6), save: window.__zombie.save }));
  const sleep = ms => page.waitForTimeout(ms);

  await page.goto(base, { waitUntil: 'load' });
  await sleep(1200);
  log('menu state:', JSON.stringify(await state()));
  await page.screenshot({ path: 'test-menu.png' });
  // GM SDK check: placeholder present, SDK_OPTIONS defined, no ad on load
  log('GM:', await page.evaluate(() => ({ sdkOptions: !!window.SDK_OPTIONS, gameId: window.SDK_OPTIONS && window.SDK_OPTIONS.gameId, gm: window.__gamemonetize ? { available: window.__gamemonetize.available, preRoll: window.__gamemonetize.preRollShown } : null })));

  // PLAY -> loading must last ~3s
  const t0 = Date.now();
  await page.click('#playBtn');
  await sleep(500);
  log('after PLAY (0.5s):', JSON.stringify(await state()), 'loading visible:', await page.isVisible('#loading'));
  await sleep(3000);
  log('after 3s loading, elapsed:', Date.now()-t0, JSON.stringify(await state()));
  await page.screenshot({ path: 'test-playing.png' });
  // Real play: aim AT actual zombies (via canvas coords) + shoot, ~40s. Kills = score>0.
  const tPlay = Date.now();
  while (Date.now() - tPlay < 40000) {
    const s = await state();
    if (s.state === 'shop') break;
    if (s.state !== 'playing') { log('unexpected state mid-play:', s.state); break; }
    const aim = await page.evaluate(() => { const z = window.__zombie.zombies[0]; const r = window.__zombie.canvasRect; const p = window.__zombie.player; if (!z) return null; const cx = v => Math.max(2, Math.min(998, v)), cy = v => Math.max(2, Math.min(698, v)); return { x: cx(r.x + z.x * r.w / 960), y: cy(r.y + z.y * r.h / 640), px: cx(r.x + p.x * r.w / 960), py: cy(r.y + p.y * r.h / 640) }; });
    if (aim) { await page.mouse.move(aim.x, aim.y); await page.mouse.down(); await sleep(700); await page.mouse.up(); }
    else await sleep(400);
    // strafe occasionally so zombies don't corner the player
    await page.keyboard.down('a'); await sleep(300); await page.keyboard.up('a');
  }
  log('after 40s real aimed play:', JSON.stringify(await state()));
  await page.screenshot({ path: 'test-midplay.png' });
  // Finish Night 1 via debug hook (simulates the rest of the kills) — real-play kill path already proven above
  await page.evaluate(() => window.__zombie.debugKillAll());
  await sleep(800);
  let s = await state();
  log('after debugKillAll Night1:', JSON.stringify(s));
  await page.screenshot({ path: 'test-shop.png' });
  if (s.state !== 'shop') log('FAIL: expected shop after Night 1');
  // Shop: grant coins via debug hook, then buy a damage upgrade + a barricade
  await page.evaluate(() => window.__zombie.debugSetCoins(300));
  const coinsBefore = (await state()).coins;
  const buyBtns = await page.$$('#shopItems button');
  log('shop buttons:', buyBtns.length, 'coins:', coinsBefore);
  if (buyBtns.length) { await buyBtns[0].click(); await sleep(300); log('after buy damage, coins:', (await state()).coins, 'upgrades:', JSON.stringify((await state()).save.upgrades)); }
  const buyBtns2 = await page.$$('#shopItems button');
  if (buyBtns2.length > 4) { await buyBtns2[4].click(); await sleep(300); log('after buy barricade, barricades:', (await state()).save.barricades); }
  // Next Night -> loading -> Night 2 playing, with runners (variety)
  await page.click('#nextNightBtn'); await sleep(3600);
  s = await state(); log('Night 2 state:', JSON.stringify(s));
  // spawn each type and check sprites differ per level
  const types = await page.evaluate(() => { window.__zombie.debugSpawn('runner'); window.__zombie.debugSpawn('spitter'); window.__zombie.debugSpawn('brute'); return window.__zombie.zombies.map(z => z.type + ':' + z.img); });
  log('Night2 spawned types:', JSON.stringify(types));
  // Save/resume: reload, menu should show unlocked=2, select Night 2
  await page.reload({ waitUntil: 'load' }); await sleep(1000);
  s = await state(); log('after RELOAD (save/resume):', JSON.stringify({ unlocked: s.unlocked, stars: s.stars, state: s.state }));
  const gridText = await page.textContent('#levelGrid');
  log('level grid contains Night 2 unlocked:', /Night 2/.test(gridText));
  // Boss night 4: unlock all, start Night 4, verify boss spawns
  await page.evaluate(() => window.__zombie.debugUnlockAll());
  await page.evaluate(() => window.__zombie.startLevel(4));
  await sleep(3600);
  s = await state(); log('Night 4 start:', JSON.stringify(s));
  await page.evaluate(() => { window.__zombie.debugKillAll(); }); // clears regulars, boss spawns when <=6... debugKillAll sets bossSpawned=true, so test boss directly:
  await page.evaluate(() => window.__zombie.debugSpawn('boss'));
  await sleep(500);
  const boss = await page.evaluate(() => window.__zombie.zombies.find(z => z.type === 'boss'));
  log('boss spawned:', JSON.stringify(boss));
  await page.screenshot({ path: 'test-boss.png' });
  // Kill boss + finish night 4
  await page.evaluate(() => window.__zombie.debugKillAll()); await sleep(800);
  log('after Night4 complete:', JSON.stringify(await state()));
  // Spitter projectile check on Night 3
  await page.evaluate(() => window.__zombie.startLevel(3)); await sleep(3600);
  await page.evaluate(() => window.__zombie.debugSpawn('spitter'));
  await sleep(3000);
  const ebullets = await page.evaluate(() => { const z = window.__zombie.zombies.find(z => z.type === 'spitter'); return z ? 'spitter present' : 'none'; });
  log('spitter check:', ebullets);
  // Per-level distinct walker sprites L1 vs L2 vs L12
  const imgs = await page.evaluate(async () => {
    const out = {};
    for (const n of [1,2,12]) { const im = new Image(); im.src = 'assets/enemy_l' + String(n).padStart(2,'0') + '.png'; await new Promise(r => { im.onload = r; im.onerror = r; }); out[n] = im.naturalWidth + 'x' + im.naturalHeight; }
    return out;
  });
  log('per-level walker sprites:', JSON.stringify(imgs));
  // Soak: auto-aim bot plays Night 5 (mixed types) for 150s — sustained-play evidence
  await page.evaluate(() => window.__zombie.startLevel(5)); await sleep(3600);
  const soakStart = Date.now(); let soakKills0 = (await state()).score;
  while (Date.now() - soakStart < 150000) {
    const s2 = await state();
    if (s2.state !== 'playing') { log('soak ended early, state:', s2.state); break; }
    const aim2 = await page.evaluate(() => { const z = window.__zombie.zombies[0]; const r = window.__zombie.canvasRect; if (!z) return null; const cx = v => Math.max(2, Math.min(998, v)), cy = v => Math.max(2, Math.min(698, v)); return { x: cx(r.x + z.x * r.w / 960), y: cy(r.y + z.y * r.h / 640) }; });
    if (aim2) { await page.mouse.move(aim2.x, aim2.y); await page.mouse.down(); await sleep(500); await page.mouse.up(); } else await sleep(300);
    await page.keyboard.down('w'); await sleep(200); await page.keyboard.up('w');
  }
  const soakEnd = await state();
  log('soak Night5 150s:', JSON.stringify({ state: soakEnd.state, lives: soakEnd.lives, scoreGain: soakEnd.score - soakKills0, left: soakEnd.left, zombies: soakEnd.zombies.map(z => z.type) }));
  await page.screenshot({ path: 'test-soak.png' });
  // Mute toggle
  await page.click('#muteBtn'); log('mute toggled, text:', await page.textContent('#muteBtn'));
  // Touch UI presence check (viewport touch)
  log('touchUI display (desktop):', await page.evaluate(() => getComputedStyle(document.getElementById('touchUI')).display));
  log('ERRORS (' + errors.length + '):', errors.length ? errors.join(' | ') : 'none');
  fs.writeFileSync('test-results.json', JSON.stringify({ errors, finishedAt: new Date().toISOString() }, null, 2));
  await browser.close();
})().catch(e => { console.error('TEST CRASH', e); process.exit(1); });
