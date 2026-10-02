const scanForm = document.querySelector("#scan-form");
const urlInput = document.querySelector("#url");
const maxPagesInput = document.querySelector("#max-pages");
const checkLinksInput = document.querySelector("#check-links");
const maxLinksInput = document.querySelector("#max-links");
const scanButton = document.querySelector("#scan-button");
const scanStatus = document.querySelector("#scan-status");
const resultSection = document.querySelector("#result-section");
const historyList = document.querySelector("#history-list");
const historyEmpty = document.querySelector("#history-empty");
const refreshHistoryButton = document.querySelector("#refresh-history");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function displayUrl(value) {
  try {
    const url = new URL(value);
    return url.hostname + (url.pathname === "/" ? "" : url.pathname);
  } catch {
    return value;
  }
}

function healthLabel(score) {
  if (score >= 95) return "Excellent";
  if (score >= 85) return "Good";
  if (score >= 70) return "Needs attention";
  return "Needs work";
}

function setLoading(isLoading) {
  scanButton.disabled = isLoading;
  scanButton.classList.toggle("loading", isLoading);
  scanStatus.classList.remove("error");
  scanStatus.textContent = isLoading
    ? "Scanning pages and analyzing site quality…"
    : "";
}

function renderScan(scan) {
  resultSection.classList.remove("hidden");

  document.querySelector("#result-domain").textContent = displayUrl(scan.start_url);
  document.querySelector("#result-time").textContent =
    "Saved " + formatDate(scan.created_at);
  document.querySelector("#health-score").textContent = scan.site_health;
  document.querySelector("#health-label").textContent = healthLabel(scan.site_health);
  document.querySelector("#pages-scanned").textContent = scan.pages_scanned;
  document.querySelector("#total-issues").textContent = scan.total_issues;
  document.querySelector("#broken-links").textContent =
    scan.link_check?.broken_count ?? 0;
  document.querySelector("#high-count").textContent = scan.severity.high;
  document.querySelector("#medium-count").textContent = scan.severity.medium;
  document.querySelector("#low-count").textContent = scan.severity.low;
  document.querySelector("#page-count-badge").textContent =
    `${scan.pages.length} page${scan.pages.length === 1 ? "" : "s"}`;

  const scoreRing = document.querySelector("#score-ring");
  const percentage = Math.max(0, Math.min(100, scan.site_health));
  scoreRing.style.background =
    `radial-gradient(circle closest-side, #0d1a2b 78%, transparent 80% 100%), ` +
    `conic-gradient(var(--accent) ${percentage}%, rgba(148, 163, 184, 0.12) 0)`;

  const pagesList = document.querySelector("#pages-list");
  pagesList.innerHTML = scan.pages.map((page) => {
    const issues = page.issues.length
      ? page.issues.map((issue) => `
          <div class="issue">
            <span class="issue-tag ${escapeHtml(issue.severity)}">${escapeHtml(issue.severity)}</span>
            <p><strong>${escapeHtml(issue.category)}:</strong> ${escapeHtml(issue.message)}</p>
          </div>
        `).join("")
      : `<div class="issue"><p>No issues detected on this page.</p></div>`;

    return `
      <article class="page-item">
        <div class="page-summary" role="button" tabindex="0" aria-expanded="false">
          <div class="page-url">
            <strong>${escapeHtml(displayUrl(page.url))}</strong>
            <span>HTTP ${page.status_code} · ${page.response_time_ms} ms</span>
          </div>
          <div class="page-score">${page.score}/100</div>
          <div class="issue-count">${page.issues.length} issue${page.issues.length === 1 ? "" : "s"}</div>
        </div>
        <div class="page-details">
          <div class="detail-grid">
            <div class="detail-stat"><span>H1 headings</span><strong>${page.h1_count}</strong></div>
            <div class="detail-stat"><span>Images</span><strong>${page.image_count}</strong></div>
            <div class="detail-stat"><span>Internal links</span><strong>${page.internal_link_count}</strong></div>
            <div class="detail-stat"><span>External links</span><strong>${page.external_link_count}</strong></div>
          </div>
          <div class="issue-list">${issues}</div>
        </div>
      </article>
    `;
  }).join("");

  pagesList.querySelectorAll(".page-summary").forEach((summary) => {
    const toggle = () => {
      const item = summary.closest(".page-item");
      const isOpen = item.classList.toggle("open");
      summary.setAttribute("aria-expanded", String(isOpen));
    };

    summary.addEventListener("click", toggle);
    summary.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    });
  });

  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function runScan(event) {
  event.preventDefault();
  setLoading(true);

  try {
    const response = await fetch("/api/scans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: urlInput.value.trim(),
        max_pages: Number(maxPagesInput.value),
        check_links: checkLinksInput.checked,
        max_links: Number(maxLinksInput.value),
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      const detail = typeof data.detail === "string"
        ? data.detail
        : "The scan could not be completed.";
      throw new Error(detail);
    }

    renderScan(data);
    await loadHistory();
    scanStatus.textContent = `Scan #${data.id} completed and saved.`;
  } catch (error) {
    scanStatus.classList.add("error");
    scanStatus.textContent = error.message || "Something went wrong.";
  } finally {
    scanButton.disabled = false;
    scanButton.classList.remove("loading");
  }
}

async function loadHistory() {
  try {
    const response = await fetch("/api/scans?limit=10");
    const data = await response.json();

    if (!response.ok) throw new Error("Could not load scan history.");

    const scans = data.scans ?? [];
    historyEmpty.classList.toggle("hidden", scans.length !== 0);

    historyList.innerHTML = scans.map((scan) => `
      <article class="history-item" data-scan-id="${scan.id}" tabindex="0" role="button">
        <div class="history-domain">
          <strong>${escapeHtml(displayUrl(scan.start_url))}</strong>
          <span>${escapeHtml(formatDate(scan.created_at))} · Scan #${scan.id}</span>
        </div>
        <div class="history-stat">
          <strong>${scan.site_health}/100</strong>
          <span>Health</span>
        </div>
        <div class="history-stat">
          <strong>${scan.pages_scanned}</strong>
          <span>Pages</span>
        </div>
        <div class="history-stat">
          <strong>${scan.total_issues}</strong>
          <span>Issues</span>
        </div>
        <div class="history-stat">
          <strong>${scan.broken_links_count}</strong>
          <span>Broken links</span>
        </div>
      </article>
    `).join("");

    historyList.querySelectorAll(".history-item").forEach((item) => {
      const openSavedScan = () => loadSavedScan(item.dataset.scanId);

      item.addEventListener("click", openSavedScan);
      item.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openSavedScan();
        }
      });
    });
  } catch (error) {
    historyList.innerHTML = `
      <div class="empty-state">
        <strong>History unavailable</strong>
        <span>${escapeHtml(error.message)}</span>
      </div>
    `;
  }
}

async function loadSavedScan(scanId) {
  try {
    scanStatus.classList.remove("error");
    scanStatus.textContent = `Loading saved scan #${scanId}…`;

    const response = await fetch(`/api/scans/${scanId}`);
    const data = await response.json();

    if (!response.ok) throw new Error("Could not load that saved scan.");

    renderScan(data);
    scanStatus.textContent = `Loaded saved scan #${scanId}.`;
  } catch (error) {
    scanStatus.classList.add("error");
    scanStatus.textContent = error.message;
  }
}

checkLinksInput.addEventListener("change", () => {
  maxLinksInput.disabled = !checkLinksInput.checked;
});

scanForm.addEventListener("submit", runScan);
refreshHistoryButton.addEventListener("click", loadHistory);
loadHistory();
