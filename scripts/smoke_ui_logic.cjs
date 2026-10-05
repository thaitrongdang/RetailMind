"use strict";

// DOM-light integration check: executes the real UI controller against the real local API.
// It verifies data binding and failure states; it does not replace visual browser testing.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

async function main() {
  const elements = new Map();
  for (const name of ["content", "page-title", "page-index", "navigation", "snapshot", "sidebar", "menu-toggle", "service-status", "customer-form", "new-customer-button", "model-select", "product-form", "product-query", "customer-id", "similar-result", "error-analysis", "reveal-outcomes", "replay-outcomes", "retry-button", "change-customer-button"]) {
    elements.set(name, {innerHTML: "", outerHTML: "", textContent: "", value: "", disabled: false, handlers: {}, addEventListener(type, handler) { this.handlers[type] = handler; }, setAttribute() {}, classList: {toggle() { return false; }, remove() {}}});
  }
  const document = {
    getElementById(name) { return elements.get(name) || null; },
    querySelectorAll() { return []; }
  };
  const base = process.env.RETAILMIND_API_URL || "http://127.0.0.1:8765";
  const requests = [];
  const context = vm.createContext({
    document,
    URLSearchParams,
    fetch: path => { requests.push(path); return globalThis.fetch(base + path); },
    console
  });
  vm.runInContext(fs.readFileSync("ui/app.js", "utf8"), context);
  for (let attempt = 0; attempt < 100 && !elements.get("content").innerHTML.includes("Positive sales over time"); attempt++) {
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  assert.ok(elements.get("content").innerHTML.includes("Positive sales over time"), "Initial API-backed overview did not load");
  const run = async (page, needle) => {
    vm.runInContext("state.page = " + JSON.stringify(page), context);
    await vm.runInContext("render()", context);
    const html = elements.get("content").innerHTML;
    assert.ok(html.includes(needle), page + " did not render expected content: " + html.slice(0, 180));
    console.log(page + ": OK");
  };
  await run("overview", "Positive sales over time");
  vm.runInContext('state.customerId = "12384"', context);
  await run("customers", "Top-ten recommendations");
  vm.runInContext('state.model = "als"', context);
  await run("customers", "Serving model: als");
  vm.runInContext('state.model = "selected"', context);
  await vm.runInContext("renderNewCustomer(state.generation)", context);
  assert.ok(elements.get("content").innerHTML.includes("explicit_new_customer"), "Missing explicit new-customer view");
  console.log("new customer: OK");
  const outcomeRequestsBeforeReplay = requests.filter(path => path.startsWith("/replay/outcomes")).length;
  await run("replay", "Reveal outcomes");
  assert.equal(requests.filter(path => path.startsWith("/replay/outcomes")).length, outcomeRequestsBeforeReplay, "Replay fetched outcomes before reveal");
  assert.ok(!elements.get("content").innerHTML.includes("Observed future products"), "Replay disclosed outcomes before reveal");
  const revealButton = elements.get("reveal-outcomes");
  await revealButton.handlers.click({currentTarget: revealButton});
  assert.ok(elements.get("replay-outcomes").innerHTML.includes("Observed future products"), "Reveal did not display outcomes");
  assert.equal(requests.filter(path => path.startsWith("/replay/outcomes")).length, outcomeRequestsBeforeReplay + 1, "Reveal did not fetch outcomes exactly once");
  await run("products", "Product search");
  await run("evaluation", "Model comparison");
  assert.ok(elements.get("error-analysis").outerHTML.includes("no-hit customers"), "Missing test error analysis");
  await run("quality", "Classification reasons");
  vm.runInContext('state.snapshot = "validation"', context);
  await run("overview", "validation-20110901");
  vm.runInContext('state.page = "customers"; state.customerId = "unknown-id"', context);
  await vm.runInContext("render()", context);
  assert.ok(elements.get("content").innerHTML.includes("customer_not_found"), "Missing unknown-customer error state");
  assert.ok(elements.get("content").innerHTML.includes("Change customer ID"), "Unknown-customer error has no recovery action");
  console.log("validation snapshot and customer error: OK");
}

main().catch(error => {console.error(error); process.exitCode = 1;});
