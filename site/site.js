// The website lives on stat.cmu.edu. If this copy was opened on GitHub Pages, go there.
if (window.location.hostname.endsWith("github.io")) {
  const page = window.location.pathname.split("/site/")[1] || "";
  window.location.replace(courseLinks.siteHome + page + window.location.hash);
}

function setRepoLinks() {
  document.querySelectorAll("[data-public-repo]").forEach((element) => {
    element.href = courseLinks.publicRepo;
  });
}

function isReleased(item, today = new Date()) {
  if (!item.slides) return false;
  const mode = siteSettings.moduleReleaseMode;
  if (mode === "all") return true;
  if (mode === "beta") return item.week <= siteSettings.betaThroughWeek;
  if (mode === "preview") return item.week === siteSettings.previewWeek;
  return new Date(`${item.publishDate}T00:00:00`) <= today;
}

// "2027-02-14" means midnight in Pittsburgh; "2027-02-14T13:00" means 1 pm there.
// The offset is found from the time zone, so dates after daylight saving starts are right too.
function easternTime(dateString) {
  const [day, time = "00:00"] = dateString.split("T");
  const standard = new Date(`${day}T${time}:00-05:00`);
  const hourThere = Number(new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    hourCycle: "h23",
    timeZone: "America/New_York"
  }).format(standard));
  const hourWanted = Number(time.split(":")[0]);
  return hourThere === hourWanted ? standard : new Date(standard.getTime() - 60 * 60 * 1000);
}

// "Sun Feb 14" for a date, "Sun Feb 14, 1 pm" for a date with a time.
function formatDate(dateString) {
  const hasTime = dateString.includes("T");
  const instant = hasTime ? easternTime(dateString) : new Date(`${dateString}T12:00:00-05:00`);
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hourCycle: "h12",
    timeZone: "America/New_York"
  }).formatToParts(instant).map((part) => [part.type, part.value]));
  const date = `${parts.weekday} ${parts.month} ${parts.day}`;
  if (!hasTime) return date;
  const minutes = parts.minute === "00" ? "" : `:${parts.minute}`;
  return `${date}, ${parts.hour}${minutes} ${parts.dayPeriod.toLowerCase()}`;
}

function isOpen(openDate, today = new Date()) {
  if (!openDate || siteSettings.moduleReleaseMode === "beta") return true;
  return easternTime(openDate) <= today;
}

function link(item) {
  if (!item.href) return `<span class="locked">${item.label}</span>`;
  if (!isOpen(item.openDate)) {
    return `<span class="locked" title="Opens ${formatDate(item.openDate)}">${item.label}</span>`;
  }
  return `<a href="${item.href}">${item.label}</a>`;
}

function linkList(items) {
  if (!items) return "";
  return items.map(link).join(" · ");
}

function homeworkCell(hw) {
  if (!hw) return "";
  if (!isOpen(hw.openDate)) {
    return `<span class="locked">${hw.label}</span><span class="small">opens ${formatDate(hw.openDate)}</span>`;
  }
  return `${hw.label} · <a href="${hw.pdf}">PDF</a><br>${linkList(hw.links)}<span class="small">due ${hw.due}</span>`;
}

function currentWeek() {
  const released = weeklyMaterials.filter((item) => isReleased(item));
  return released.length ? released[released.length - 1] : null;
}

function renderSchedule() {
  const body = document.querySelector("[data-schedule]");
  if (!body) return;
  const current = currentWeek();

  body.innerHTML = weeklyMaterials.map((item) => {
    const released = isReleased(item);
    const classes = [item.isBreak ? "break" : "", current && item.week === current.week ? "current" : ""].join(" ").trim();
    const data = released && item.data
      ? `<span class="small">${item.data.map(link).join(" · ")}</span>`
      : "";
    const note = item.note ? `<span class="small">${item.note}</span>` : "";
    return `
      <tr class="${classes}">
        <td class="week">${item.week}</td>
        <td class="dates">${item.dates}</td>
        <td class="topic">${item.topic}${note}${data}</td>
        <td class="links" data-label="Slides">${released ? linkList(item.slides) : ""}</td>
        <td class="links" data-label="Lab">${released ? linkList(item.lab) : ""}</td>
        <td class="links" data-label="Homework">${released ? homeworkCell(item.homework) : ""}</td>
      </tr>`;
  }).join("");

  const mode = document.querySelector("[data-release-mode]");
  if (mode && siteSettings.moduleReleaseMode === "beta") {
    mode.textContent = `Beta preview: Weeks 1–${siteSettings.betaThroughWeek} are open for testing.`;
  }
}

function renderThisWeek() {
  const box = document.querySelector("[data-this-week]");
  if (!box) return;
  const item = currentWeek();
  if (!item) {
    box.innerHTML = `<p>Materials for each week appear here the Sunday before class.</p>`;
    return;
  }
  box.innerHTML = `
    <p class="this-week-title">Week ${item.week} · ${item.dates}</p>
    <p class="this-week-topic">${item.topic}</p>
    <dl>
      <dt>Slides</dt><dd>${linkList(item.slides)}</dd>
      <dt>Lab</dt><dd>${linkList(item.lab)}</dd>
      <dt>Homework</dt><dd>${homeworkCell(item.homework)}</dd>
    </dl>`;
}

function renderProjectDocs() {
  const list = document.querySelector("[data-project-docs]");
  if (!list) return;
  list.innerHTML = projectDocs.map((doc) => {
    const action = doc.links
      ? linkList(doc.links)
      : doc.href
        ? link({ label: doc.actionLabel || "Open", href: doc.href, openDate: doc.openDate })
        : `<span class="locked">Coming later</span>`;
    return `<li><strong>${doc.label}.</strong> ${doc.status} ${action}</li>`;
  }).join("");
}

setRepoLinks();
renderSchedule();
renderThisWeek();
renderProjectDocs();
