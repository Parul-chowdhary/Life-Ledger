/**
 * LifeLedger Client Application Controller.
 * Handles theme switching, interactive calendar navigation,
 * OCR preview canvas bounding boxes, warranty claim letters, and search.
 */

document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();
  initCalendar();
  initSearch();
  initClaimLetterModal();
});

/* 1. Dark / Light Theme Toggle */
function initThemeToggle() {
  const toggleBtn = document.getElementById("theme-toggle-btn");
  if (!toggleBtn) return;

  const savedTheme = localStorage.getItem("lifeledger-theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(toggleBtn, savedTheme);

  toggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("lifeledger-theme", next);
    updateThemeIcon(toggleBtn, next);
  });
}

function updateThemeIcon(btn, theme) {
  btn.innerHTML = theme === "dark" ? "☀️ Light" : "🌙 Dark";
}

/* 2. Interactive Calendar View */
function initCalendar() {
  const calendarGrid = document.getElementById("calendar-days-grid");
  if (!calendarGrid) return;

  const monthYearLabel = document.getElementById("calendar-month-year");
  const prevBtn = document.getElementById("cal-prev-btn");
  const nextBtn = document.getElementById("cal-next-btn");

  let currentDate = new Date();

  function renderMonth(date) {
    calendarGrid.innerHTML = "";
    const year = date.getFullYear();
    const month = date.getMonth();

    const monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];
    if (monthYearLabel) {
      monthYearLabel.textContent = `${monthNames[month]} ${year}`;
    }

    const firstDayIndex = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Empty cells before first day
    for (let i = 0; i < firstDayIndex; i++) {
      const blank = document.createElement("div");
      blank.className = "calendar-cell empty";
      calendarGrid.appendChild(blank);
    }

    // Days in current month
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
      const cell = document.createElement("div");
      cell.className = "calendar-cell";

      const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
      if (isToday) cell.classList.add("today");

      const dayNum = document.createElement("span");
      dayNum.className = "day-number";
      dayNum.textContent = day;
      cell.appendChild(dayNum);

      // Check if deadlines exist for this day (from embedded data attribute)
      const dayDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      if (window.LIFELEDGER_DEADLINES && window.LIFELEDGER_DEADLINES[dayDateStr]) {
        const events = window.LIFELEDGER_DEADLINES[dayDateStr];
        events.forEach(ev => {
          const badge = document.createElement("div");
          badge.className = `event-pill priority-${ev.priority}`;
          badge.textContent = ev.title;
          badge.title = `${ev.title} ($${ev.cost || 0})`;
          cell.appendChild(badge);
        });
      }

      calendarGrid.appendChild(cell);
    }
  }

  renderMonth(currentDate);

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      currentDate.setMonth(currentDate.getMonth() - 1);
      renderMonth(currentDate);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentDate.setMonth(currentDate.getMonth() + 1);
      renderMonth(currentDate);
    });
  }
}

/* 3. Client-Side Vault Search & Filter */
function initSearch() {
  const searchInput = document.getElementById("vault-search-input");
  const tableRows = document.querySelectorAll(".vault-doc-row");
  if (!searchInput || tableRows.length === 0) return;

  searchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    tableRows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(q) ? "" : "none";
    });
  });
}

/* 4. Warranty Claim Letter Modal */
function initClaimLetterModal() {
  const modal = document.getElementById("claim-letter-modal");
  const closeBtn = document.getElementById("close-claim-modal-btn");
  const copyBtn = document.getElementById("copy-claim-letter-btn");
  const letterBodyEl = document.getElementById("claim-letter-text");

  if (!modal) return;

  document.querySelectorAll(".open-claim-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const assetName = btn.dataset.assetName;
      const serialNumber = btn.dataset.serialNumber;
      const manufacturer = btn.dataset.manufacturer;
      const expiry = btn.dataset.expiry;

      const bodyText = `Date: ${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}

To: ${manufacturer || "Manufacturer"} Warranty Service Department
Device: ${assetName}
Serial Number: ${serialNumber || "N/A"}
Warranty Status: Active (Expires ${expiry})

Subject: Official Warranty Repair / Replacement Claim Notice

Dear Customer Support,

I am writing to formally submit a warranty claim under the terms of the manufacturer's limited warranty for the device identified above.

DEFECT DESCRIPTION:
Hardware malfunction preventing normal operation under standard household usage.

REQUESTED RESOLUTION:
Expedited warranty repair or equivalent product replacement, along with RMA documentation and prepaid return shipping.

Sincerely,
Registered Warranty Owner (LifeLedger Verified)
`;
      if (letterBodyEl) letterBodyEl.value = bodyText;
      modal.classList.add("open");
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", () => modal.classList.remove("open"));
  }

  if (copyBtn && letterBodyEl) {
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(letterBodyEl.value).then(() => {
        copyBtn.textContent = "Copied to Clipboard!";
        setTimeout(() => (copyBtn.textContent = "Copy Claim Letter"), 2500);
      });
    });
  }
}

/* 5. 1-Click Complete Deadline */
async function completeDeadline(deadlineId) {
  try {
    const resp = await fetch(`/api/v1/deadlines/${deadlineId}/complete`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
    });
    if (resp.ok) {
      window.location.reload();
    } else {
      alert("Unable to update deadline.");
    }
  } catch (err) {
    console.error(err);
    alert("Network error.");
  }
}
