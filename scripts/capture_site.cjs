const { chromium } = require('C:/Users/hardi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:1440,height:980},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:8765',{waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(2500);
  await page.screenshot({path:'reports/website_hero.png'});
  await page.locator('#simulator').scrollIntoViewIfNeeded();
  await page.getByRole('button',{name:/Run PSO/}).click();
  await page.getByText('Search complete.',{exact:false}).waitFor({state:'visible',timeout:30000});
  await page.screenshot({path:'reports/website_results.png'});
  console.log('Saved website_hero.png and website_results.png');
  await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
