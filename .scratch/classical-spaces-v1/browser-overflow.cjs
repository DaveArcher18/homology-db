const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
    await page.goto("file:///tmp/homology-classical-candidate.html#spectrum=ceta");
    await page.locator(".spectrum-view").waitFor();
    console.log(JSON.stringify(await page.evaluate(() => ({
      viewport: innerWidth, document: document.documentElement.scrollWidth,
      elements: [...document.querySelectorAll("body *")].map((node) => ({
        tag: node.tagName, id: node.id, class: node.className,
        left: node.getBoundingClientRect().left, right: node.getBoundingClientRect().right,
        width: node.getBoundingClientRect().width, overflow: getComputedStyle(node).overflowX,
      })).filter((node) => node.right > innerWidth + 1 || node.left < -1).slice(0, 35),
    })), null, 2));
    await page.screenshot({ path: "/tmp/homology-classical-ceta-overflow.png", fullPage: true, animations: "disabled" });
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
