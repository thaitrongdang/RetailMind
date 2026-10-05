"use strict";

const state = {page: "overview", snapshot: "test", generation: 0, customerId: "", model: "selected", productQuery: "", selectedProduct: ""};
const content = document.getElementById("content");
const titles = {overview: "Overview", customers: "Customers", replay: "Historical Replay", products: "Products", evaluation: "Model Evaluation", quality: "Data Quality"};
const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const num = value => Number(value ?? 0).toLocaleString("en-GB");
const money = value => "£" + Number(value ?? 0).toLocaleString("en-GB", {minimumFractionDigits: 2, maximumFractionDigits: 2});
const pct = value => (Number(value ?? 0) * 100).toFixed(2) + "%";
const query = values => new URLSearchParams(values).toString();
const context = () => '<span class="context">' + (state.snapshot === "test" ? "Test · 01 Nov 2011" : "Validation · 01 Sep 2011") + '</span>';
const panel = (title, body) => '<section class="panel"><h2>' + esc(title) + '</h2>' + body + '</section>';
const lightPanel = (title, body) => '<section class="panel light"><h2>' + esc(title) + '</h2>' + body + '</section>';
const metricCard = (label, value, definition, light = false) => '<div class="card' + (light ? ' spotlight' : '') + '"><span class="label">' + esc(label) + '</span><strong>' + esc(value) + '</strong><small>' + esc(definition) + '</small></div>';
const note = text => '<div class="inline-note">' + esc(text) + '</div>';
const empty = text => '<div class="state empty">' + esc(text) + '</div>';
const table = (headers, rows) => '<div class="table-wrap"><table><thead><tr>' + headers.map(h => '<th>' + esc(h) + '</th>').join("") + '</tr></thead><tbody>' + rows.map(row => '<tr>' + row.map(cell => '<td>' + cell + '</td>').join("") + '</tr>').join("") + '</tbody></table></div>';
const intro = text => '<div class="page-intro"><p>' + esc(text) + '</p>' + context() + '</div>';
const requestNote = data => '<p class="meta">Snapshot <span class="mono">' + esc(data.snapshot_id) + '</span> · Request <span class="mono">' + esc(data.request_id) + '</span></p>';

async function getJson(path) {
  const response = await fetch(path, {headers: {"Accept": "application/json"}});
  let data;
  try { data = await response.json(); } catch (_) { throw new Error("The API returned an unreadable response (" + response.status + ")."); }
  if (!response.ok) throw new Error((data.error || "API error") + " · HTTP " + response.status + " · request " + (data.request_id || "unavailable"));
  return data;
}
function showError(error) {
  const canChangeCustomer = (state.page === "customers" || state.page === "replay") && state.customerId;
  content.innerHTML = '<div class="state error" role="alert"><span class="state-title">Unable to load this view</span><p>' + esc(error.message || error) + '</p><div class="actions"><button class="retry-button" id="retry-button" type="button">Retry</button>' + (canChangeCustomer ? '<button class="secondary" id="change-customer-button" type="button">Change customer ID</button>' : '') + '</div></div>';
  document.getElementById('retry-button').addEventListener('click', render);
  if (canChangeCustomer) document.getElementById('change-customer-button').addEventListener('click', () => {state.customerId = ""; render();});
}
function loading() { content.innerHTML = '<div class="state" role="status">Loading snapshot data…</div>'; }
function current(generation) { return generation === state.generation; }
async function render() {
  const generation = ++state.generation;
  document.getElementById("page-title").textContent = titles[state.page];
  document.getElementById("page-index").textContent = String(Object.keys(titles).indexOf(state.page) + 1).padStart(2, '0');
  document.querySelectorAll("#navigation button").forEach(button => {button.classList.toggle("active", button.dataset.page === state.page); button.setAttribute("aria-current", button.dataset.page === state.page ? "page" : "false");});
  loading();
  try {
    if (state.page === "overview") await overview(generation);
    if (state.page === "customers") await customers(generation);
    if (state.page === "replay") await replay(generation);
    if (state.page === "products") await products(generation);
    if (state.page === "evaluation") await evaluation(generation);
    if (state.page === "quality") await quality(generation);
  } catch (error) { if (current(generation)) showError(error); }
}
function bars(rows, label, value, formatter) {
  const largest = Math.max(...rows.map(row => Number(row[value] || 0)), 1);
  return '<div class="bar-chart" role="img" aria-label="' + esc(label + " bar chart") + '">' + rows.map(row => '<div class="bar-row"><span>' + esc(row[label]) + '</span><div class="bar-track"><div class="bar-fill" style="width:' + Math.max(2, Number(row[value] || 0) / largest * 100).toFixed(2) + '%"></div></div><span class="value">' + esc(formatter(row[value])) + '</span></div>').join("") + '</div><div class="axis-label">' + esc(value + " · " + (value.includes("gbp") ? "GBP" : "count")) + '</div>';
}
function monthlyChart(rows) {
  if (!rows.length) return empty("No monthly sales are available for this snapshot.");
  const values = rows.map(row => Number(row.gross_sales_gbp || 0));
  const ceiling = Math.max(...values, 1) * 1.12;
  const x0 = 54, y0 = 18, width = 720, height = 222;
  const points = rows.map((row, index) => [x0 + (rows.length === 1 ? width / 2 : index * width / (rows.length - 1)), y0 + height - values[index] / ceiling * height]);
  const line = points.map((point, index) => (index ? "L" : "M") + point[0].toFixed(1) + " " + point[1].toFixed(1)).join(" ");
  const area = line + " L " + (x0 + width) + " " + (y0 + height) + " L " + x0 + " " + (y0 + height) + " Z";
  const grid = [0, .5, 1].map(fraction => {
    const y = y0 + height * (1 - fraction);
    return '<line class="chart-grid" x1="' + x0 + '" y1="' + y + '" x2="' + (x0 + width) + '" y2="' + y + '"/><text class="chart-label" x="0" y="' + (y + 4) + '">£' + esc((ceiling * fraction / 1000000).toFixed(1)) + 'm</text>';
  }).join("");
  const ticks = rows.map((row, index) => index % Math.max(1, Math.ceil(rows.length / 6)) === 0 || index === rows.length - 1 ? '<text class="chart-label" x="' + points[index][0] + '" y="266" text-anchor="middle">' + esc(row.month) + '</text>' : '').join("");
  const last = points[points.length - 1];
  return '<div class="chart-frame"><svg viewBox="0 0 790 278" role="img" aria-label="Monthly positive merchandise sales in GBP, from ' + esc(rows[0].month) + ' through ' + esc(rows[rows.length - 1].month) + '"><title>Monthly positive sales in GBP</title>' + grid + '<path class="chart-area" d="' + area + '"/><path class="chart-line" d="' + line + '"/><circle class="chart-point" cx="' + last[0] + '" cy="' + last[1] + '" r="4"/>' + ticks + '</svg><div class="chart-legend">Positive merchandise sales · GBP</div></div>';
}
async function overview(generation) {
  const data = await getJson("/overview?" + query({snapshot: state.snapshot}));
  if (!current(generation)) return;
  const s = data.summary;
  const cards = [["Positive sales",money(s.gross_sales_gbp),"GBP · excludes returns and adjustments"],["Sales invoices",num(s.invoices),"Distinct sale invoice IDs"],["Known customers",num(s.identified_customers),"Identified before this cutoff"],["Product codes",num(s.products),"Valid merchandise codes"]];
  content.innerHTML = intro("Historical merchandise activity before " + data.train_cutoff.slice(0, 10) + ". Figures include anonymous positive sales where applicable; recommendations use identified history.") +
    '<div class="grid cards">' + cards.map((card,index) => metricCard(...card,index === 0)).join("") + '</div>' +
    panel("Positive sales over time", '<p class="panel-subtitle">Last 12 observed months · positive merchandise sales, not net revenue</p>' + monthlyChart(data.monthly.slice(-12)) + '<details><summary>View monthly values</summary>' + table(["Month","Invoices","Sale lines","Positive sales (GBP)"],data.monthly.map(row => [esc(row.month),num(row.invoices),num(row.sale_lines),money(row.gross_sales_gbp)])) + '</details>') +
    '<div class="grid two-col">' +
    panel("Popular products",data.top_products.length ? table(["Stock code","Invoices","Units"],data.top_products.map(row => [esc(row.stock_code),num(row.invoices),num(row.units)])) : empty("No eligible products.")) +
    panel("Countries by positive sales",data.countries.length ? bars(data.countries.slice(0,6),"country","gross_sales_gbp",money) + '<details><summary>View all countries</summary>' + table(["Country","Invoices","Positive sales (GBP)"],data.countries.map(row => [esc(row.country),num(row.invoices),money(row.gross_sales_gbp)])) + '</details>' : empty("No country data.")) +
    '</div>' + note("Positive sales exclude returns and adjustments. Anonymous sales appear in these totals but do not train personalized recommendations.") + requestNote(data);
}
function customerForm() {
  return '<form id="customer-form" class="form-row"><div class="field"><label for="customer-id">Historical customer ID</label><input id="customer-id" name="customer_id" value="' + esc(state.customerId) + '" placeholder="e.g. 12384" required></div><div class="field"><label for="model-select">Ranking model</label><select id="model-select"><option value="selected"' + (state.model === 'selected' ? ' selected' : '') + '>Selected</option><option value="itemcf"' + (state.model === 'itemcf' ? ' selected' : '') + '>ItemCF</option><option value="als"' + (state.model === 'als' ? ' selected' : '') + '>ALS</option><option value="popularity"' + (state.model === 'popularity' ? ' selected' : '') + '>Popularity</option></select></div><button class="primary" type="submit">Load customer</button><button id="new-customer-button" class="secondary" type="button">New-customer recommendations</button></form><p class="meta">Example from the verified local UCI workbook: 12384. An unknown ID returns 404; use explicit new-customer recommendations when there is no history.</p>';
}
function bindCustomerForm() {
  document.getElementById("customer-form").addEventListener("submit", event => {event.preventDefault(); state.customerId = document.getElementById("customer-id").value.trim(); state.model = document.getElementById("model-select").value; render();});
  document.getElementById("new-customer-button").addEventListener("click", () => renderNewCustomer(state.generation));
}
function recommendationTable(data) {
  return table(["Rank","Product","Ranking score","History","Serving model","Historical evidence"], data.items.map(item => [
    num(item.rank), '<strong>' + esc(item.stock_code) + '</strong><br><span class="comparison">' + esc(item.description_as_of_cutoff) + '</span>',
    Number(item.score).toFixed(4), item.repeat_item ? '<span class="pill">Repeat</span>' : '<span class="pill muted">New to customer</span>',
    esc(item.source_model), '<details class="evidence-disclosure"><summary>View evidence</summary><span class="evidence">' + evidence(item.evidence) + '</span></details>'
  ]));
}
function evidence(value) {
  if (!value) return "No evidence available";
  if (value.kind === "distinct_customers_90d") return esc(num(value.count) + " distinct customers in prior 90 days");
  if (Array.isArray(value.top)) return value.top.length ? value.top.map(part => esc(part.historical_stock_code) + " · " + Number(part.contribution).toFixed(3)).join("<br>") : "No contributing history";
  return esc(value.kind);
}
async function renderNewCustomer(generation) {
  content.innerHTML = intro("Explicit new-customer mode uses the pre-cutoff Popularity bundle. No customer ID or fabricated shared history is used.") + panel("New customer", customerForm()) + '<div class="state">Loading new-customer recommendations…</div>';
  bindCustomerForm();
  try {
    const rec = await getJson("/recommendations/new?" + query({snapshot: state.snapshot, k: 10}));
    if (!current(generation)) return;
    const csv = "/recommendations/new?" + query({snapshot: state.snapshot, k: 10, format: "csv"});
    content.innerHTML = intro("Explicit new-customer mode uses the pre-cutoff Popularity bundle. No customer ID or fabricated shared history is used.") +
      panel("New customer", customerForm()) +
      panel("Popularity recommendations", '<div class="actions"><a class="link-button" href="' + esc(csv) + '">Download CSV</a></div><p class="meta">Mode ' + esc(rec.mode) + ' · ' + esc(rec.reason_code) + ' · Bundle ' + esc(rec.model_version) + '</p>' + recommendationTable(rec)) + requestNote(rec);
    bindCustomerForm();
  } catch (error) { if (current(generation)) showError(error); }
}
async function customers(generation) {
  const heading = intro("Inspect one customer's pre-cutoff history and a ranking from the selected snapshot. Search IDs represent historical customers, not live accounts.") + panel("Find a customer", customerForm());
  content.innerHTML = heading + (state.customerId ? '<div class="state" role="status">Loading customer profile and recommendations…</div>' : empty("Enter a historical customer ID to inspect RFM, purchase history and a top-ten ranking."));
  bindCustomerForm();
  if (!state.customerId) return;
  const [profile, rec] = await Promise.all([
    getJson("/customers/" + encodeURIComponent(state.customerId) + "?" + query({snapshot: state.snapshot})),
    getJson("/recommendations?" + query({snapshot: state.snapshot, customer_id: state.customerId, k: 10, model: state.model}))
  ]);
  if (!current(generation)) return;
  const p = profile.profile;
  const cards = [["RFM segment",p.rfm_segment,"Cutoff-fitted segment"],["Recency",num(p.recency_days) + " days","Since last purchase at cutoff"],["Frequency",num(p.frequency_invoices),"Distinct historical invoices"],["Monetary",money(p.monetary_gbp),"Positive historical sales"]];
  const csv = "/recommendations?" + query({snapshot: state.snapshot, customer_id: state.customerId, k: 10, model: state.model, format: "csv"});
  content.innerHTML = heading +
    panel("Customer " + p.customer_id, '<p class="meta">Country: ' + esc(p.country) + ' · First purchase: ' + esc(p.first_purchase.slice(0,10)) + ' · Last purchase: ' + esc(p.last_purchase.slice(0,10)) + ' · Distinct products: ' + num(p.distinct_products) + '</p><div class="grid cards">' + cards.map((card,index) => metricCard(...card,index === 0)).join("") + '</div>') +
    panel("Recent historical sale lines",profile.recent_lines.length ? table(["Date","Invoice","Product","Description","Quantity","Unit price (GBP)"],profile.recent_lines.map(row => [esc(row.invoice_date.slice(0,10)),esc(row.invoice_no),esc(row.stock_code),esc(row.description),num(row.quantity),money(row.unit_price)])) : empty("No historical sale lines.")) +
    panel("Top-ten recommendations",'<div class="actions"><a class="link-button" href="' + esc(csv) + '">Download CSV ↗</a></div><p class="meta">Serving model: ' + esc(rec.model_name) + ' · Version ' + esc(rec.model_version) + ' · Mode ' + esc(rec.mode) + ' · Reason ' + esc(rec.reason_code) + '</p>' + (rec.items.length ? recommendationTable(rec) : empty("No eligible recommendations were returned."))) +
    note("Scores are model-specific ranking signals, not purchase probabilities. Each row identifies any Popularity backfill.") + requestNote(rec);
  bindCustomerForm();
}
async function replay(generation) {
  const heading = intro("Review the history and ranking at this cutoff, then reveal purchases observed over the next 30 days. Future outcomes come from a separate route.") + panel("Replay a historical customer", customerForm());
  content.innerHTML = heading + (state.customerId ? '<div class="state">Loading historical replay…</div>' : empty("Enter a historical customer ID to replay."));
  bindCustomerForm();
  if (!state.customerId) return;
  const [profile, rec] = await Promise.all([
    getJson("/customers/" + encodeURIComponent(state.customerId) + "?" + query({snapshot: state.snapshot})),
    getJson("/recommendations?" + query({snapshot: state.snapshot, customer_id: state.customerId, k: 10, model: state.model})),
  ]);
  if (!current(generation)) return;
  content.innerHTML = heading +
    '<div class="grid cards">' + metricCard("Training cutoff",rec.train_cutoff.slice(0,10),"History is strictly before this date",true) + metricCard("Prediction horizon","30 days","Starting at the cutoff") + metricCard("Serving model",rec.model_name,"Reason: " + rec.reason_code) + metricCard("Ranked products",num(rec.items.length),"Repeat purchases allowed") + '</div>' +
    panel("Recent history before cutoff",profile.recent_lines.length ? table(["Date","Invoice","Product","Description","Quantity"],profile.recent_lines.map(row => [esc(row.invoice_date.slice(0,10)),esc(row.invoice_no),esc(row.stock_code),esc(row.description),num(row.quantity)])) : empty("No recent history was returned.")) +
    panel("Ranking at cutoff",rec.items.length ? table(["Rank","Product","Description at cutoff","History","Serving model"],rec.items.map(item => [num(item.rank),esc(item.stock_code),esc(item.description_as_of_cutoff),item.repeat_item ? '<span class="pill">Repeat</span>' : '<span class="pill muted">New to customer</span>',esc(item.source_model)])) : empty("No eligible recommendations were returned.")) +
    '<div class="actions"><button class="primary" id="reveal-outcomes" type="button">Reveal outcomes</button></div><div id="replay-outcomes" aria-live="polite"></div>' +
    note("The ranking above is fixed before outcomes are requested. Purchase overlap is an offline observation, not evidence of product exposure or preference.") + requestNote(rec);
  bindCustomerForm();
  document.getElementById("reveal-outcomes").addEventListener("click", async event => {
    const button = event.currentTarget;
    button.disabled = true;
    const target = document.getElementById("replay-outcomes");
    target.innerHTML = '<div class="state" role="status">Loading observed future purchases…</div>';
    try {
      const outcomes = await getJson("/replay/outcomes?" + query({snapshot: state.snapshot, customer_id: state.customerId}));
      if (!current(generation)) return;
      const labels = new Set(outcomes.labels.map(row => String(row.stock_code)));
      const hits = rec.items.filter(item => labels.has(item.stock_code)).length;
      target.innerHTML = '<div class="grid cards">' + metricCard("Observed products",num(labels.size),"Distinct valid future products",true) + metricCard("Top-ten overlap",num(hits),"Observed matching products") + metricCard("Window starts",outcomes.outcome_start.slice(0,10),"Inclusive") + metricCard("Window ends",outcomes.outcome_end_exclusive.slice(0,10),"Exclusive") + '</div>' +
        panel("Ranking compared with outcomes",table(["Rank","Product","Observed future purchase"],rec.items.map(item => [num(item.rank),esc(item.stock_code),labels.has(item.stock_code) ? '<span class="pill">✓ Observed match</span>' : '<span class="pill muted">No match</span>']))) +
        panel("Observed future products",outcomes.labels.length ? table(["Stock code","First observed purchase","Future invoices"],outcomes.labels.map(row => [esc(row.stock_code),esc(row.first_outcome_time),num(row.future_invoices)])) : empty("No valid identified purchase was observed in this 30-day window."));
    } catch (error) {
      if (!current(generation)) return;
      target.innerHTML = '<div class="state error" role="alert">' + esc(error.message || error) + '</div>';
      button.disabled = false;
    }
  });
}
function productsForm() {
  return '<form id="product-form" class="form-row"><div class="field"><label for="product-query">Code or description</label><input id="product-query" value="' + esc(state.productQuery) + '" placeholder="Search products"></div><button class="primary" type="submit">Search</button></form>';
}
async function products(generation) {
  const url = "/products?" + query({snapshot: state.snapshot, q: state.productQuery, limit: 25});
  const data = await getJson(url);
  if (!current(generation)) return;
  content.innerHTML = intro("Search merchandise seen before the selected cutoff. Similar products come from the ItemCF bundle for that same snapshot.") +
    panel("Product search", productsForm() + '<p class="meta">' + num(data.total_matches) + ' matching product codes · Showing at most 25 by 90-day customer popularity.</p>' +
      (data.items.length ? table(["Stock code","Description","90-day customers","Historical sale lines","Explore"], data.items.map(row => [
        esc(row.stock_code),esc(row.description),num(row.popularity_90d),num(row.sale_lines),
        '<button class="secondary similar-button" type="button" data-code="' + esc(row.stock_code) + '">Similar</button>'
      ])) : empty("No products matched this search."))) +
    '<div id="similar-result"></div>' + requestNote(data);
  document.getElementById("product-form").addEventListener("submit", event => {event.preventDefault(); state.productQuery = document.getElementById("product-query").value.trim(); state.selectedProduct = ""; render();});
  document.querySelectorAll(".similar-button").forEach(button => button.addEventListener("click", () => {state.selectedProduct = button.dataset.code; renderSimilar(generation, data.items.find(item => item.stock_code === state.selectedProduct));}));
  if (state.selectedProduct) await renderSimilar(generation, data.items.find(item => item.stock_code === state.selectedProduct));
}
async function renderSimilar(generation, product) {
  const target = document.getElementById("similar-result");
  if (!target) return;
  target.innerHTML = '<div class="state">Loading similar products…</div>';
  try {
    const data = await getJson("/products/" + encodeURIComponent(state.selectedProduct) + "/similar?" + query({snapshot: state.snapshot, k: 10}));
    if (!current(generation)) return;
    target.innerHTML = panel("Product " + data.stock_code, (product ? '<p class="meta">' + esc(product.description) + ' · ' + num(product.popularity_90d) + ' distinct customers in the prior 90 days · ' + num(product.sale_lines) + ' historical sale lines</p>' : '') + '<p class="meta">Similarities come from the cutoff-specific ItemCF bundle; they do not imply stock availability.</p>' + (data.items.length ? table(["Rank","Product","Description at cutoff","ItemCF similarity"], data.items.map(row => [num(row.rank),esc(row.stock_code),esc(row.description_as_of_cutoff),Number(row.score).toFixed(4)])) : empty("This product has no retained ItemCF neighbors."))) + requestNote(data);
  } catch (error) { if (current(generation)) target.innerHTML = '<div class="state error">' + esc(error.message) + '</div>'; }
}
async function evaluation(generation) {
  const data = await getJson("/evaluations?" + query({snapshot: state.snapshot}));
  if (!current(generation)) return;
  const models = Object.entries(data.model_metrics);
  const contract = data.evaluation_contract || {};
  const csv = "/evaluations?" + query({snapshot: state.snapshot, format: "csv"});
  const cohorts = data.selected_routed_metrics.by_history_cohort || {};
  const rfm = data.selected_routed_metrics.by_rfm_segment || {};
  const selected = data.model_metrics[data.selected_model];
  content.innerHTML = intro("Offline purchase-overlap metrics on a common historical-customer cohort. Validation selected the configuration; test reports the frozen selection.") +
    lightPanel("Validation-selected model", '<p class="selection-model">' + esc(({itemcf: "ItemCF", als: "ALS", popularity: "Popularity"})[data.selected_model] || data.selected_model) + '</p><p class="panel-subtitle">Selected on validation NDCG@10. The test split reports this frozen choice without reselection.</p><div class="selection-stats"><span>Recall@10 <strong>' + pct(selected.recall_at_10) + '</strong></span><span>NDCG@10 <strong>' + pct(selected.ndcg_at_10) + '</strong></span><span>Evaluated customers <strong>' + num(selected.evaluated_customers) + '</strong></span></div>') +
    panel("Model comparison", '<div class="actions"><a class="link-button" href="' + esc(csv) + '">Download metrics CSV</a></div>' +
      table(["Model","Customers","Recall@10","NDCG@10","HitRate@10","Catalog coverage","Offline p95 (ms)"], models.map(([name,m]) => [
        esc(name) + (name === data.selected_model ? ' <span class="pill">Selected</span>' : ''), num(m.evaluated_customers),pct(m.recall_at_10),pct(m.ndcg_at_10),pct(m.hit_rate_at_10),pct(m.catalog_coverage),Number(m.offline_inference_p95_ms).toFixed(2)
      ])) + '<p class="meta">Full candidate ranking · common labels and cohort · repeat purchases allowed. Offline p95 is evaluator inference time, separate from HTTP latency.</p>') +
    panel("Selected model by history", table(["Historical invoices","Evaluated customers","Recall@10","NDCG@10"], Object.entries(cohorts).map(([name,m]) => [esc(name.replaceAll("_"," ")),num(m.evaluated_customers),pct(m.recall_at_10),pct(m.ndcg_at_10)]))) +
    panel("Selected model by RFM segment", table(["Cutoff-fitted segment","Evaluated customers","Recall@10","NDCG@10"], Object.entries(rfm).map(([name,m]) => [esc(name.replaceAll("_"," ")),num(m.customers),pct(m.recall_at_10),pct(m.ndcg_at_10)]))) +
    panel("Cohort and protocol", table(["Measure","Value"], [
      ["Historical customers",num(data.selected_routed_metrics.historical_customers)],
      ["Evaluated customers",num(data.selected_routed_metrics.evaluated_customers)],
      ["Historical customers without future labels",num(data.selected_routed_metrics.empty_label_historical_customers)],
      ["New future customers",num(data.selected_routed_metrics.new_future_customers)],
      ["Candidate products",num(data.selected_routed_metrics.candidate_products)],
      ["Label availability",pct(data.selected_routed_metrics.label_availability_micro)],
      ["Horizon",esc(contract.horizon_days || 30) + " days"]
    ]) + (state.snapshot === "test" ? '<div id="error-analysis" class="state">Loading test error analysis…</div>' : note("Error analysis is reported for the frozen test split only."))) +
    requestNote(data);
  if (state.snapshot === "test") {
    const errors = await getJson("/evaluations/errors");
    if (!current(generation)) return;
    const a = errors.analysis;
    document.getElementById("error-analysis").outerHTML = '<div class="inline-note">Selected model no-hit customers: ' + num(a.zero_hit_customers) + ' / ' + num(a.evaluated_customers) + ' (' + pct(a.zero_hit_rate) + '). Future-only label pairs: ' + num(a.future_only_label_pairs) + '. This measures overlap, not exposure or preference.</div>';
  }
}
async function quality(generation) {
  const data = await getJson("/data-quality");
  if (!current(generation)) return;
  const q = data.quality;
  const rows = Object.entries(q.reason_counts).map(([name,count]) => [esc(name.replaceAll("_"," ")),num(count),pct(count / q.total_rows)]);
  const missing = Object.entries(q.missing_raw_values || {});
  const examples = Object.entries(q.reason_samples || {}).flatMap(([reason,items]) => items.map(item => [esc(reason.replaceAll("_"," ")),esc(item.raw_row_id),esc(item.source_sheet) + ' / ' + num(item.source_row),esc(item.invoice_raw),esc(item.stock_code_raw),esc(item.customer_id_raw || "Missing")]));
  content.innerHTML = intro("Full-source lineage and classification across both workbook sheets. This report covers all dates, including dates after either training cutoff.") +
    '<div class="grid cards">' + metricCard("Source rows",num(q.total_rows),"Across both workbook sheets",true) + metricCard("Unique row IDs",num(q.unique_raw_row_ids),"Source lineage") + metricCard("Duplicate-like extra rows",num(q.suspicious_duplicate_extra_rows),"Flagged and retained") + metricCard("Reconciliation",q.reconciled ? "Passed" : "Failed","One reason per raw row") + '</div>' +
    panel("Classification reasons", table(["Reason","Rows","Share of source"],rows) + '<p class="meta">Each row receives exactly one primary reason. Cancellations, invalid values and non-merchandise rows remain in processed lineage but do not train recommendations. Anonymous valid sales support analytics only.</p>') +
    panel("Missing values in raw fields",missing.length ? table(["Raw field","Missing rows","Share of source"],missing.map(([field,count]) => [esc(field.replaceAll("_raw","")),num(count),pct(count / q.total_rows)])) : empty("Field-level missingness has not been generated. Run the current prepare command to refresh this report.")) +
    panel("Traceable example rows",examples.length ? table(["Reason","Raw row ID","Sheet / Excel row","Invoice","Stock code","Customer ID"],examples) : empty("Reason examples are unavailable. Run the current prepare command to refresh this report.")) +
    panel("Source manifest", table(["Sheet","Data rows"],data.sheets.map(sheet => [esc(sheet.name),num(sheet.rows)])) + '<p class="meta">Workbook SHA-256: <span class="mono">' + esc(data.source_hash) + '</span><br>License: ' + esc(data.license) + '<br>Excluded non-merchandise codes: ' + esc(data.excluded_stock_codes.join(", ")) + '</p>') +
    note("Data-quality counts describe the entire source, whereas overview and customer figures are cut off at the selected snapshot. Duplicate-like rows were retained pending sensitivity analysis.") + '<p class="meta">Request <span class="mono">' + esc(data.request_id) + '</span></p>';
}
document.getElementById("navigation").addEventListener("click", event => {
  const button = event.target.closest("button[data-page]");
  if (!button) return;
  state.page = button.dataset.page;
  setNavigationOpen(false);
  render();
});
document.getElementById("snapshot").addEventListener("change", event => {state.snapshot = event.target.value; state.selectedProduct = ""; render();});
function setNavigationOpen(open) {
  const sidebar = document.getElementById("sidebar");
  const isMobile = window.matchMedia("(max-width: 920px)").matches;
  sidebar.classList.toggle("open", isMobile && open);
  sidebar.inert = isMobile && !open;
  sidebar.setAttribute("aria-hidden", String(isMobile && !open));
  const toggle = document.getElementById("menu-toggle");
  toggle.setAttribute("aria-expanded", String(isMobile && open));
  toggle.setAttribute("aria-label", isMobile && open ? "Close navigation" : "Open navigation");
}
document.getElementById("menu-toggle").addEventListener("click", () => {
  setNavigationOpen(!document.getElementById("sidebar").classList.contains("open"));
});
window.addEventListener("resize", () => setNavigationOpen(false));
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && document.getElementById("sidebar").classList.contains("open")) {
    setNavigationOpen(false);
    document.getElementById("menu-toggle").focus();
  }
});
setNavigationOpen(false);
async function bootstrap() {
  try {
    const [health, snapshots] = await Promise.all([getJson("/health"), getJson("/snapshots")]);
    const status = document.getElementById("service-status");
    status.className = "service-status " + (health.status === "ready" ? "ready" : "degraded");
    status.innerHTML = '<span class="status-dot"></span>' + (health.status === "ready" ? "API ready" : "API degraded");
    const select = document.getElementById("snapshot");
    if (snapshots.snapshots.length) {
      select.innerHTML = snapshots.snapshots.slice().reverse().map(item => '<option value="' + esc(item.name) + '">' + esc(item.name === "test" ? "Test" : "Validation") + ' · ' + esc(item.train_cutoff.slice(0,10)) + '</option>').join("");
      select.value = state.snapshot;
    }
  } catch (_) {
    const status = document.getElementById("service-status");
    status.className = "service-status degraded";
    status.innerHTML = '<span class="status-dot"></span>API unavailable';
  }
  render();
}
bootstrap();
