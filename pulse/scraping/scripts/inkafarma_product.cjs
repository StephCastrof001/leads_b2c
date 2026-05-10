const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SKU = process.argv[2] || '068513';
const URL = `https://inkafarma.pe/producto/protector-solar-la-roche-posay-anthelios-uvmune400/${SKU}`;
const OUTPUT_DIR = path.join(__dirname, '../output');

async function scrapeProduct(sku, url) {
  console.log(`[SCRAPER] Iniciando para SKU: ${sku}`);
  console.log(`[SCRAPER] URL: ${url}`);

  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'es-PE',
    timezoneId: 'America/Lima',
  });

  const page = await context.newPage();

  // Bloquear assets innecesarios para ir mas rapido
  await page.route('**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf}', route => route.abort());

  await page.goto(url, { waitUntil: 'load', timeout: 30000 });

  // Esperar a que los precios carguen (auto-wait via locator)
  await page.waitForSelector('[class*=price], [class*=Price], [class*=precio]', {
    timeout: 10000
  }).catch(() => console.log('[WARN] Selector de precio no encontrado, continuando...'));

  // Screenshot para verificacion visual
  const screenshotPath = path.join(OUTPUT_DIR, `inkafarma_${sku}.png`);
  // Habilitar imagenes solo para screenshot
  await page.unroute('**/*.{png,jpg,jpeg,gif,webp}');
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.log(`[SCRAPER] Screenshot guardado: ${screenshotPath}`);

  // Extraer HTML completo del area de precio + producto
  const rawData = await page.evaluate(() => {
    const result = {
      title: document.title,
      url: window.location.href,
      // Buscar todos los textos que parecen precios (S/XX.XX)
      allPriceTexts: [],
      // Buscar elementos con oh, cupon, descuento en texto
      specialPriceElements: [],
      // HTML del contenedor principal del producto
      productHTML: '',
    };

    // Capturar todos los textos con patron de precio peruano
    const allElements = document.querySelectorAll('*');
    const pricePattern = /S\/\s*[\d,]+\.?\d*/gi;
    const pctPattern = /\d+%\s*(dscto|descuento|off)/gi;

    allElements.forEach(el => {
      if (el.children.length === 0) { // solo nodos hoja
        const text = el.textContent?.trim();
        if (text && (pricePattern.test(text) || pctPattern.test(text))) {
          pricePattern.lastIndex = 0;
          pctPattern.lastIndex = 0;
          result.allPriceTexts.push({
            text: text,
            tag: el.tagName,
            className: el.className?.toString().substring(0, 100),
            id: el.id,
          });
        }
      }
    });

    // Buscar elementos especiales: Oh!, cupon, descuento
    const keywords = ['oh!', 'ohpay', 'oh pay', 'cupon', 'cupÃ³n', 'oferta', 'precio especial'];
    allElements.forEach(el => {
      const text = el.textContent?.toLowerCase().trim();
      if (text && keywords.some(k => text.includes(k)) && text.length < 200) {
        result.specialPriceElements.push({
          text: el.textContent?.trim().substring(0, 150),
          tag: el.tagName,
          className: el.className?.toString().substring(0, 100),
        });
      }
    });

    // HTML del contenedor de producto (buscar por roles comunes)
    const productContainer = document.querySelector(
      '[class*=product-detail], [class*=product_detail], ' +
      '[class*=pdp], [class*=product-page], ' +
      'main article, [role=main]'
    );
    if (productContainer) {
      result.productHTML = productContainer.innerHTML.substring(0, 5000);
    }

    return result;
  });

  await browser.close();

  // Guardar resultado
  const output = {
    sku,
    url,
    scraped_at: new Date().toISOString(),
    screenshot: screenshotPath,
    ...rawData,
  };

  const outputPath = path.join(OUTPUT_DIR, `inkafarma_${sku}_raw.json`);
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`[SCRAPER] JSON guardado: ${outputPath}`);
  console.log(`\n=== PRECIOS ENCONTRADOS ===`);
  console.log(JSON.stringify(rawData.allPriceTexts, null, 2));
  console.log(`\n=== ELEMENTOS ESPECIALES (Oh!/Cupon) ===`);
  console.log(JSON.stringify(rawData.specialPriceElements.slice(0, 10), null, 2));

  return output;
}

scrapeProduct(SKU, URL).catch(err => {
  console.error('[ERROR]', err.message);
  process.exit(1);
});

