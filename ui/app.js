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
function showError(error) { content.innerHTML = '<div class="state error" role="alert">' + esc(error.message || error) + '</div>'; }
function loading() { content.innerHTML = '<div class="state" role="status">Loading snapshot data…</div>'; }
function current(generation) { return generation === state.generation; }
async function render() {
  const generation = ++state.generation;
  document.getElementById("page-title").textContent = titles[state.page];
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
async function overview(generation) {
  const data = await getJson("/overview?" + query({snapshot: state.snapshot}));
  if (!current(generation)) return;
  const s = data.summary;
  const cards = [["Positive sales", money(s.gross_sales_gbp), "GBP, excludes returns"],["Sales invoices", num(s.invoices), "Distinct invoice IDs"],["Known customers", num(s.identified_customers), "Pre-cutoff only"],["Product codes", num(s.products), "Includes anonymous-only sales"]];
  content.innerHTML = intro("Sales activity strictly before this training cutoff. Positive valid merchandise sales include anonymous transactions; recommendation candidates require identified history.") +
    '<div class="grid cards">' + cards.map(card => '<div class="card"><span class="label">' + esc(card[0]) + '</span><strong>' + esc(card[1]) + '</strong><small>' + esc(card[2]) + '</small></div>').join("") + '</div>' +
    '<div class="grid two-col">' +
    panel("Monthly positive sales", bars(data.monthly.slice(-12), "month", "gross_sales_gbp", money) + table(["Month","Invoices","Sale lines","Gross positive sales (GBP)"], data.monthly.map(row => [esc(row.month),num(row.invoices),num(row.sale_lines),money(row.gross_sales_gbp)]))) +
    panel("Countries", table(["Country","Invoices","Gross positive sales (GBP)"], data.countries.map(row => [esc(row.country),num(row.invoices),money(row.gross_sales_gbp)]))) +
    '</div>' + panel("Most frequent product codes", table(["Stock code","Invoices","Units"], data.top_products.map(row => [esc(row.stock_code),num(row.invoices),num(row.units)]))) +
    note("Positive sales are not net revenue or profit. Unknown-customer sales are present in overview but do not enter personalized model training.") + requestNote(data);
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
    esc(item.source_model), '<span class="evidence">' + evidence(item.evidence) + '</span>'
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
}async function customers(generation) {
  const heading = intro("Inspect a pre-cutoff customer profile, recent sale lines and personalized product rankings.") + panel("Find a customer", customerForm());
  content.innerHTML = heading + (state.customerId ? '<div class="state">Loading customer…</div>' : empty("Enter a historical customer ID to inspect its profile and top-ten recommendations."));
  bindCustomerForm();
  if (!state.customerId) return;
  const [profile, rec] = await Promise.all([
    getJson("/customers/" + encodeURIComponent(state.customerId) + "?" + query({snapshot: state.snapshot})),
    getJson("/recommendations?" + query({snapshot: state.snapshot, customer_id: state.customerId, k: 10, model: state.model}))
  ]);
  if (!current(generation)) return;
  const p = profile.profile;
  const cards = [["RFM segment",p.rfm_segment,"Cutoff-fitted"],["Recency",num(p.recency_days) + " days","At cutoff"],["Frequency",num(p.frequency_invoices),"Distinct invoices"],["Monetary",money(p.monetary_gbp),"Positive GBP sales"]];
  const csv = "/recommendations?" + query({snapshot: state.snapshot, customer_id: state.customerId, k: 10, model: state.model, format: "csv"});
  content.innerHTML = heading + '<div class="grid cards">' + cards.map(card => '<div class="card"><span class="label">' + esc(card[0]) + '</span><strong>' + esc(card[1]) + '</strong><small>' + esc(card[2]) + '</small></div>').join("") + '</div>' +
    panel("Top-ten recommendations", '<div class="actions"><a class="link-button" href="' + esc(csv) + '">Download CSV</a></div><p class="meta">Actual model: ' + esc(rec.model_name) + ' · Version ' + esc(rec.model_version) + ' · Mode ' + esc(rec.mode) + ' · ' + esc(rec.reason_code) + '</p>' + recommendationTable(rec)) +
    panel("Recent historical sale lines", profile.recent_lines.length ? table(["Date","Invoice","Product","Quantity","Unit price (GBP)"], profile.recent_lines.map(row => [esc(row.invoice_date),esc(row.invoice_no),esc(row.stock_code),num(row.quantity),money(row.unit_price)])) : empty("No historical sale lines.")) +
    note("Ranking scores are model-specific signals, not purchase probabilities. Per-item serving model reveals any Popularity backfill.") + requestNote(rec);
  bindCustomerForm();
}
async function replay(generation) {
  const heading = intro("Compare a recommendation list made at the selected cutoff with purchases observed in the following 30 days. Outcomes are loaded through a separate route.") + panel("Replay a historical customer", customerForm());
  content.innerHTML = heading + (state.customerId ? '<div class="state">Loading historical replay…</div>' : empty("Enter a historical customer ID to replay."));
  bindCustomerForm();
  if (!state.customerId) return;
  const [rec, outcomes] = await Promise.all([
    getJson("/recommendations?" + query({snapshot: state.snapshot, customer_id: state.customerId, k: 10, model: state.model})),
    getJson("/replay/outcomes?" + query({snapshot: state.snapshot, customer_id: state.customerId}))
  ]);
  if (!current(generation)) return;
  const labels = new Set(outcomes.labels.map(row => String(row.stock_code)));
  const hits = rec.items.filter(item => labels.has(item.stock_code)).length;
  content.innerHTML = heading +
    '<div class="grid cards"><div class="card"><span class="label">Observed future products</span><strong>' + num(labels.size) + '</strong><small>Distinct valid products</small></div><div class="card"><span class="label">Top-ten overlap</span><strong>' + num(hits) + '</strong><small>Observed matching products</small></div><div class="card"><span class="label">Window starts</span><strong style="font-size:16px">' + esc(outcomes.outcome_start.slice(0,10)) + '</strong><small>Inclusive</small></div><div class="card"><span class="label">Window ends</span><strong style="font-size:16px">' + esc(outcomes.outcome_end_exclusive.slice(0,10)) + '</strong><small>Exclusive</small></div></div>' +
    panel("Ranking at cutoff", table(["Rank","Product","Description at cutoff","Observed future purchase","Serving model"], rec.items.map(item => [num(item.rank),esc(item.stock_code),esc(item.description_as_of_cutoff),labels.has(item.stock_code) ? '<span class="pill">Observed match</span>' : '<span class="pill muted">No match</span>',esc(item.source_model)]))) +
    panel("Observed future product labels", outcomes.labels.length ? table(["Stock code","First observed purchase","Future invoices"], outcomes.labels.map(row => [esc(row.stock_code),esc(row.first_outcome_time),num(row.future_invoices)])) : empty("No valid identified purchase was observed in this 30-day window.")) +
    note("A no-match result does not mean this customer saw or rejected a product. The source has purchases but no recommendation impression logs.") + requestNote(rec);
  bindCustomerForm();
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
  document.querySelectorAll(".similar-button").forEach(button => button.addEventListener("click", () => {state.selectedProduct = button.dataset.code; renderSimilar(generation);}));
  if (state.selectedProduct) await renderSimilar(generation);
}
async function renderSimilar(generation) {
  const target = document.getElementById("similar-result");
  if (!target) return;
  target.innerHTML = '<div class="state">Loading similar products…</div>';
  try {
    const data = await getJson("/products/" + encodeURIComponent(state.selectedProduct) + "/similar?" + query({snapshot: state.snapshot, k: 10}));
    if (!current(generation)) return;
    target.innerHTML = panel("Similar to " + data.stock_code, data.items.length ? table(["Rank","Product","Description at cutoff","ItemCF similarity"], data.items.map(row => [num(row.rank),esc(row.stock_code),esc(row.description_as_of_cutoff),Number(row.score).toFixed(4)])) : empty("This product has no retained ItemCF neighbors.")) + requestNote(data);
  } catch (error) { if (current(generation)) target.innerHTML = '<div class="state error">' + esc(error.message) + '</div>'; }
}
async function evaluation(generation) {
  const data = await getJson("/evaluations?" + query({snapshot: state.snapshot}));
  if (!current(generation)) return;
  const models = Object.entries(data.model_metrics);
  const contract = data.evaluation_contract || {};
  const csv = "/evaluations?" + query({snapshot: state.snapshot, format: "csv"});
  const cohorts = data.selected_routed_metrics.by_history_cohort || {};
  content.innerHTML = intro("Offline purchase-overlap metrics on a common historical-customer cohort. Validation selected the configuration; test reports the frozen selection.") +
    panel("Model comparison", '<div class="actions"><a class="link-button" href="' + esc(csv) + '">Download metrics CSV</a></div>' +
      table(["Model","Customers","Recall@10","NDCG@10","HitRate@10","Catalog coverage"], models.map(([name,m]) => [
        esc(name) + (name === data.selected_model ? ' <span class="pill">Selected</span>' : ''), num(m.evaluated_customers),pct(m.recall_at_10),pct(m.ndcg_at_10),pct(m.hit_rate_at_10),pct(m.catalog_coverage)
      ])) + '<p class="meta">Chosen by validation NDCG@10 · Test does not reselect. Scores use full candidate ranking and allow repeat purchases.</p>') +
    panel("Selected model by history", table(["Historical invoices","Evaluated customers","Recall@10","NDCG@10"], Object.entries(cohorts).map(([name,m]) => [esc(name.replaceAll("_"," ")),num(m.evaluated_customers),pct(m.recall_at_10),pct(m.ndcg_at_10)]))) +
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
  content.innerHTML = intro("Full-source lineage and classification across both workbook sheets. This report covers all dates, including dates after either training cutoff.") +
    '<div class="grid cards"><div class="card"><span class="label">Source rows</span><strong>' + num(q.total_rows) + '</strong><small>Two sheets</small></div><div class="card"><span class="label">Unique row IDs</span><strong>' + num(q.unique_raw_row_ids) + '</strong><small>Lineage check</small></div><div class="card"><span class="label">Duplicate-like extra rows</span><strong>' + num(q.suspicious_duplicate_extra_rows) + '</strong><small>Flagged, retained</small></div><div class="card"><span class="label">Reconciliation</span><strong>' + (q.reconciled ? "Passed" : "Failed") + '</strong><small>One reason per row</small></div></div>' +
    panel("Classification reasons", table(["Reason","Rows","Share of source"],rows)) +
    panel("Source manifest", table(["Sheet","Data rows"],data.sheets.map(sheet => [esc(sheet.name),num(sheet.rows)])) + '<p class="meta">Workbook SHA-256: <span class="mono">' + esc(data.source_hash) + '</span><br>License: ' + esc(data.license) + '<br>Excluded non-merchandise codes: ' + esc(data.excluded_stock_codes.join(", ")) + '</p>') +
    note("Data-quality counts describe the entire source, whereas overview and customer figures are cut off at the selected snapshot. Duplicate-like rows were retained pending sensitivity analysis.") + '<p class="meta">Request <span class="mono">' + esc(data.request_id) + '</span></p>';
}
document.getElementById("navigation").addEventListener("click", event => {
  const button = event.target.closest("button[data-page]");
  if (!button) return;
  state.page = button.dataset.page;
  render();
});
document.getElementById("snapshot").addEventListener("change", event => {state.snapshot = event.target.value; state.selectedProduct = ""; render();});
render();