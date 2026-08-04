function setRepoLinks() {
  document.querySelectorAll("[data-public-repo]").forEach((element) => {
    element.href = courseLinks.publicRepo;
  });

  document.querySelectorAll("[data-instructor-repo]").forEach((element) => {
    element.href = courseLinks.instructorRepo;
  });
}

function isReleased(item, today = new Date()) {
  if (siteSettings.moduleReleaseMode === "all") return true;
  if (siteSettings.moduleReleaseMode === "preview") {
    return item.week === siteSettings.previewWeek;
  }
  const publishDate = new Date(`${item.publishDate}T00:00:00`);
  return publishDate <= today;
}

function formatOpenDate(dateString) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "America/New_York"
  }).format(new Date(`${dateString}T12:00:00-05:00`));
}

function materialLink(link, today = new Date()) {
  if (!link.openDate) {
    return `<a class="pill" href="${link.href}">${link.label}</a>`;
  }

  const openDate = new Date(`${link.openDate}T00:00:00-05:00`);
  if (openDate <= today) {
    return `<a class="pill" href="${link.href}">${link.label}</a>`;
  }

  const label = `${link.label} · opens ${formatOpenDate(link.openDate)}`;
  return `<span class="pill pill-locked" aria-disabled="true" title="${label}">${label}</span>`;
}

function sortedModules() {
  return weeklyMaterials
    .filter((item) => isReleased(item))
    .sort((a, b) => b.week - a.week);
}

function moduleCard(item) {
  const releaseText = item.publishDate
    ? `<p class="module-date">Publishes Sunday, ${item.publishDate}</p>`
    : "";

  return `
    <article class="card module-card">
      <div class="module-kicker">${item.label}</div>
      <h3>${item.title}</h3>
      <p>${item.description}</p>
      ${releaseText}
      <div class="pill-row">
        ${item.links.map((link) => materialLink(link)).join("")}
      </div>
    </article>
  `;
}

function renderMaterials() {
  const container = document.querySelector("[data-weekly-materials]");
  if (!container) return;

  const latest = sortedModules().slice(0, 2);
  container.innerHTML = latest.length
    ? latest.map(moduleCard).join("")
    : `<article class="card"><h3>Modules coming soon</h3><p>Weekly materials will appear here on Sundays during the semester.</p></article>`;
}

function renderModulesPage() {
  const container = document.querySelector("[data-modules-list]");
  if (!container) return;

  const modules = sortedModules();
  container.innerHTML = modules.length
    ? modules.map(moduleCard).join("")
    : `<article class="card"><h3>No released modules yet</h3><p>Weekly materials will appear here on Sundays during the semester.</p></article>`;

  const modeLabel = document.querySelector("[data-release-mode]");
  if (modeLabel) {
    if (siteSettings.moduleReleaseMode === "preview") {
      modeLabel.textContent = `Preview mode: showing Week ${siteSettings.previewWeek}. Lab and homework links remain gated by their opening dates.`;
    } else if (siteSettings.moduleReleaseMode === "all") {
      modeLabel.textContent = "Preview mode: showing all scheduled modules.";
    } else {
      modeLabel.textContent = "Live mode: modules appear after their Sunday publish date.";
    }
  }
}

function renderProjectDocs() {
  const container = document.querySelector("[data-project-docs]");
  if (!container) return;

  container.innerHTML = projectDocs.map((doc) => `
    <article class="card">
      <h3>${doc.label}</h3>
      <p>${doc.status}</p>
      <div class="pill-row">
        <a class="pill" href="${doc.href}">Open in GitHub</a>
      </div>
    </article>
  `).join("");
}

setRepoLinks();
renderMaterials();
renderModulesPage();
renderProjectDocs();
