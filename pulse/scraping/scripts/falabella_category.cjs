/**
 * Falabella Category Scraper
 * Estrategia: Network interception (primaria) + DOM fallback
 * Anti-deteccion: webdriver patch, chrome runtime inject, es-PE locale
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CATEGORY_URL = process.argv[2] || 'https://www.falabella.com.pe/falabella-pe/category/CATG11985/Cuidado-de-la-piel';
const OUTPUT_DIR = path.join(__dirname, '../output');

const API_PATTERNS = ['/api/', '/search', '/category', '/product', 'catalog', 'listing'];
const PRODUCT_SIGNALS = ['sku', 'brand', 'price', 'displayname', 'product'];

async function scrapeCategory(url) {
  console.log(`[FALABELLA] URL: ${url}`);
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-web-security',
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'es-PE',
    timezoneId: 'America/Lima',
  });

  // Patch anti-deteccion
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.chrome = { runtime: {} };
  });

  const page = await context.newPage();

  // Bloquear assets para velocidad
  await page.route('**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,otf}', r => r.abort());

  // === PRIMARIO: Network interception ===
  const capturedAPIs = [];
  page.on('response', async (response) => {
    try {
      const resUrl = response.url();
      const ct = response.headers()['content-type'] || '';
      if (!ct.includes('application/json')) return;
      if (!API_PATTERNS.some(p => resUrl.includes(p))) return;

      const text = await response.text().catch(() => '');
      if (!text || text.length < 100) return;

      const lower = text.toLowerCase();
      const score = PRODUCT_SIGNALS.filter(s => lower.includes(s)).length;
      if (score < 3) return;

      const apiFile = path.join(OUTPUT_DIR, `falabella_api_${capturedAPIs.length + 1}_raw.json`);
      let parsed;
      try { parsed = JSON.parse(text); } catch { return; }

      fs.writeFileSync(apiFile, JSON.stringify({ url: resUrl, body: parsed }, null, 2));
      capturedAPIs.push({ url: resUrl, file: apiFile, score });
      console.log(`[API] Capturado (score ${score}): ${resUrl.substring(0, 80)}`);
    } catch {}
  });

  await page.goto(url, { waitUntil: 'load', timeout: 30000 });

  // Scroll para activar lazy-load
  await page.evaluate(() => window.scrollBy(0, 600));
  await page.waitForTimeout(1500);

  // Screenshot
  await page.unroute('**/*.{png,jpg,jpeg,gif,webp}');
  const ssPath = path.join(OUTPUT_DIR, 'falabella_category.png');
  await page.screenshot({ path: ssPath });
  console.log(`[SCREENSHOT] ${ssPath}`);

  // === FALLBACK: DOM extraction ===
  const domProducts = await page.evaluate(() => {
    const results = [];
    const cardSelectors = [
      '[data-pod]', '[class*=pod-]',
      '[class*=ProductCard]', '[class*=product-card]',
      '[class*=product_card]'
    ];

    let cards = [];
    for (const sel of cardSelectors) {
      cards = Array.from(document.querySelectorAll(sel));
      if (cards.length > 0) { console.log('Selector:', sel); break; }
    }

    cards.slice(0, 6).forEach(card => {
      const getText = (...sels) => {
        for (const s of sels) {
          const el = card.querySelector(s);
          if (el?.textContent?.trim()) return el.textContent.trim();
        }
        return null;
      };

      // Precios â€” Falabella usa clases como price-internet, price-cmr
      const priceNormal = getText(
        '[class*=price-internet]', '[class*=price-normal]',
        '[class*=original]', '[class*=regular]'
      );
      const priceCMR = getText('[class*=price-cmr]', '[class*=cmr]', '[class*=promo]');
      const priceInstall = getText('[class*=installment]', '[class*=cuota]');

      const sku = card.dataset?.sku || card.dataset?.productId ||
        card.querySelector('[data-sku]')?.dataset?.sku || null;

      const imgEl = card.querySelector('img');
      const linkEl = card.querySelector('a[href*=/product/]');

      // Extraer product_id de la URL
      const href = linkEl?.href || '';
      const idMatch = href.match(/\/product\/(\d+)\//);

      results.push({
        sku: sku || idMatch?.[1] || null,
        product_id: idMatch?.[1] || null,
        nombre: getText('[class*=title]', '[class*=name]', 'b', 'h2', 'h3'),
        marca: getText('[class*=brand]', '[class*=Brand]'),
        precio_normal: priceNormal,
        precio_cmr: priceCMR,
        precio_cuotas: priceInstall,
        imagen_url: imgEl?.src || imgEl?.dataset?.src || null,
        url_producto: href || null,
      });
    });

    // Raw fallback: todos los precios S/XX.XX visibles
    const allPrices = [];
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length === 0) {
        const t = el.textContent?.trim();
        if (t && /^S\/\s*[\d,]+\.?\d*$/.test(t)) allPrices.push(t);
      }
    });

    return { cards_found: cards.length, products: results, all_prices_raw: [...new Set(allPrices)] };
  });

  await browser.close();

  const summary = {
    scraped_at: new Date().toISOString(),
    url,
    screenshot: ssPath,
    api_responses_captured: capturedAPIs.length,
    api_files: capturedAPIs.map(a => a.file),
    dom_cards_found: domProducts.cards_found,
    dom_products: domProducts.products,
    all_prices_raw: domProducts.all_prices_raw,
  };

  const summaryPath = path.join(OUTPUT_DIR, 'falabella_category_summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

  console.log('\n=== RESUMEN ===');
  console.log(`API responses capturados: ${capturedAPIs.length}`);
  console.log(`Cards DOM encontrados: ${domProducts.cards_found}`);
  console.log(`Precios raw: ${domProducts.all_prices_raw.join(', ')}`);
  console.log(`Summary: ${summaryPath}`);

  return summary;
}

scrapeCategory(CATEGORY_URL).catch(err => {
  console.error('[ERROR]', err.message);
  process.exit(1);
});

