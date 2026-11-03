const { chromium } = require('C:/Users/hardi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:980},deviceScaleFactor:1});
 await page.goto('http://127.0.0.1:8765',{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForSelector('#route-scene'); await page.waitForTimeout(1200);
 await page.screenshot({path:'reports/website_hero.png'});
 await page.locator('#simulator').scrollIntoViewIfNeeded(); await page.locator('#run-button').click();
 await page.waitForFunction(()=>document.querySelector('#run-status')?.textContent.includes('Search complete.'),null,{timeout:30000});
 await page.waitForTimeout(350);
 await page.screenshot({path:'reports/website_results.png'});
 console.log('Captured ACO website hero and results'); await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
