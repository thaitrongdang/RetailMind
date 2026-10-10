"use strict";

const {chromium} = require("playwright");
const fs = require("node:fs");
const path = require("node:path");

const base = (process.env.RETAILMIND_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "") + "/ui/";
const output = path.resolve(process.env.RETAILMIND_BROWSER_OUTPUT || ".uv-cache/browser-verification");
fs.mkdirSync(output, {recursive: true});

async function waitForText(page, text) {
  await page.getByText(text, {exact: false}).first().waitFor({timeout: 20000});
}

async function assertNoOverflow(page, label) {
  const size = await page.evaluate(() => ({page: document.documentElement.scrollWidth, viewport: window.innerWidth}));
  if (size.page > size.viewport + 1) throw new Error(`${label}: horizontal overflow ${size.page} > ${size.viewport}`);
}

async function main() {
  const browser = await chromium.launch({headless: true, ...(process.env.RETAILMIND_BROWSER_EXECUTABLE ? {executablePath: process.env.RETAILMIND_BROWSER_EXECUTABLE} : {})});
  const errors = [];
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 900}, deviceScaleFactor: 1});
    page.on("pageerror", error => errors.push(error.message));
    page.on("console", message => { if (message.type() === "error" && !message.location().url.includes("unknown-id")) errors.push(message.text() + " @ " + message.location().url); });
    await page.goto(base);
    await waitForText(page, "Positive sales over time");
    await assertNoOverflow(page, "Overview desktop");
    await page.screenshot({path: path.join(output, "overview-desktop.png"), fullPage: true});

    await page.locator('nav button[data-page="customers"]').click();
    await page.locator("#customer-id").fill("12384");
    await page.getByRole("button", {name: "Load customer"}).click();
    await waitForText(page, "Top-ten recommendations");
    await assertNoOverflow(page, "Customers desktop");
    await page.screenshot({path: path.join(output, "customers-desktop.png"), fullPage: true});
    const csvDownload = page.waitForEvent("download");
    await page.getByRole("link", {name: /Download CSV/}).first().click();
    const download = await csvDownload;
    if (!download.suggestedFilename().endsWith(".csv")) throw new Error("Recommendation export was not CSV");
    await page.getByRole("button", {name: "New-customer recommendations"}).click();
    await waitForText(page, "Popularity recommendations");
    if (!(await page.locator("#content").innerText()).includes("explicit_new_customer")) throw new Error("New-customer reason code missing");
    await page.locator("#customer-id").fill("unknown-id");
    await page.getByRole("button", {name: "Load customer"}).click();
    await waitForText(page, "Unable to load this view");
    if (!(await page.locator("#content").innerText()).includes("customer_not_found")) throw new Error("Unknown customer error missing");
    await page.getByRole("button", {name: "Change customer ID"}).click();
    await page.locator("#customer-id").fill("12384");
    await page.getByRole("button", {name: "Load customer"}).click();
    await waitForText(page, "Top-ten recommendations");

    let outcomeCalls = 0;
    page.on("request", request => { if (request.url().includes("/replay/outcomes")) outcomeCalls++; });
    await page.locator('nav button[data-page="replay"]').click();
    await page.getByRole("button", {name: "Reveal outcomes"}).waitFor();
    if (outcomeCalls !== 0) throw new Error("Replay requested outcomes before reveal");
    await page.screenshot({path: path.join(output, "replay-before-reveal-desktop.png"), fullPage: true});
    await page.getByRole("button", {name: "Reveal outcomes"}).click();
    await waitForText(page, "Observed future products");
    if (outcomeCalls !== 1) throw new Error(`Replay requested outcomes ${outcomeCalls} times`);
    await assertNoOverflow(page, "Replay desktop");
    await page.screenshot({path: path.join(output, "replay-desktop.png"), fullPage: true});

    await page.locator('nav button[data-page="products"]').click();
    await page.locator("#product-query").fill("22423");
    await page.getByRole("button", {name: "Search", exact: true}).click();
    await page.locator(".similar-button").first().click();
    await waitForText(page, "Similarities come from the cutoff-specific ItemCF bundle");
    await assertNoOverflow(page, "Products desktop");
    await page.screenshot({path: path.join(output, "products-desktop.png"), fullPage: true});

    await page.locator('nav button[data-page="evaluation"]').click();
    await waitForText(page, "Selected model by RFM segment");
    await assertNoOverflow(page, "Evaluation desktop");
    await page.screenshot({path: path.join(output, "evaluation-desktop.png"), fullPage: true});

    await page.locator('nav button[data-page="quality"]').click();
    await waitForText(page, "Traceable example rows");
    await assertNoOverflow(page, "Data Quality desktop");
    await page.screenshot({path: path.join(output, "quality-desktop.png"), fullPage: true});

    await page.locator("#snapshot").selectOption("validation");
    await page.locator('nav button[data-page="overview"]').click();
    await waitForText(page, "validation-20110901");
    const switchedContext = await page.locator(".context").innerText();
    if (!switchedContext.toLowerCase().includes("validation")) throw new Error("Snapshot context did not switch: " + switchedContext + " / " + await page.locator("#snapshot").inputValue());
    await assertNoOverflow(page, "Validation overview desktop");

    const mobile = await browser.newPage({viewport: {width: 390, height: 844}, deviceScaleFactor: 1});
    mobile.on("pageerror", error => errors.push(error.message));
    mobile.on("console", message => { if (message.type() === "error") errors.push(message.text() + " @ " + message.location().url); });
    await mobile.goto(base);
    await waitForText(mobile, "Positive sales over time");
    if (!(await mobile.locator("#sidebar").evaluate(element => element.inert))) throw new Error("Closed mobile navigation remains keyboard focusable");
    await assertNoOverflow(mobile, "Overview mobile");
    await mobile.screenshot({path: path.join(output, "overview-mobile.png"), fullPage: true});
    await mobile.locator("#menu-toggle").click();
    if (await mobile.locator("#sidebar").evaluate(element => element.inert)) throw new Error("Opened mobile navigation is inert");
    await mobile.keyboard.press("Escape");
    if (!(await mobile.locator("#sidebar").evaluate(element => element.inert))) throw new Error("Escape did not close mobile navigation");
    await mobile.locator("#menu-toggle").click();
    await mobile.locator('nav button[data-page="customers"]').click();
    await mobile.locator("#customer-id").fill("12384");
    await mobile.getByRole("button", {name: "Load customer"}).click();
    await waitForText(mobile, "Top-ten recommendations");
    await assertNoOverflow(mobile, "Customers mobile");
    await mobile.screenshot({path: path.join(output, "customers-mobile.png"), fullPage: true});
    for (const name of ["replay", "products", "evaluation", "quality"]) {
      await mobile.locator("#menu-toggle").click();
      await mobile.locator(`nav button[data-page="${name}"]`).click();
      await mobile.locator(".page-intro").waitFor();
      await waitForText(mobile, ({replay: "Reveal outcomes", products: "Code or description", evaluation: "Selected model by RFM segment", quality: "Traceable example rows"})[name]);
      await mobile.waitForFunction(() => document.querySelector("#sidebar").getBoundingClientRect().right <= 1);
      const sidebarRight = await mobile.locator("#sidebar").evaluate(element => element.getBoundingClientRect().right);
      if (sidebarRight > 1) throw new Error(`${name}: mobile navigation did not close (${sidebarRight}px)`);
      await assertNoOverflow(mobile, `${name} mobile`);
      await mobile.screenshot({path: path.join(output, `${name}-mobile.png`), fullPage: true});
    }
    if (errors.length) throw new Error("Browser errors: " + errors.join(" | "));
    const evidence = {status: "passed", scope: "browser_flow", base, checkedAt: new Date().toISOString(), pages: 6, desktop: "1440x900", mobile: "390x844", outcomeCalls, snapshotSwitch: "test→validation", screenshots: fs.readdirSync(output).filter(name => name.endsWith(".png")).sort(), errors};
    fs.writeFileSync(path.join(output, "browser_verification.json"), JSON.stringify(evidence, null, 2) + "\n");
    console.log(JSON.stringify(evidence, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });


