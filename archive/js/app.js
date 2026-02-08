/**
 * r/coys Match Survey Archive — client-side app.
 *
 * On index.html: fetches data/matches.json, renders match cards, handles filtering.
 * On match.html: reads ?id= query param and displays the infographic.
 */

(function () {
    "use strict";

    const DATA_URL = "data/matches.json";

    // -----------------------------------------------------------------------
    // Utility helpers
    // -----------------------------------------------------------------------

    function qs(selector) {
        return document.querySelector(selector);
    }

    function getQueryParam(name) {
        return new URLSearchParams(window.location.search).get(name);
    }

    // -----------------------------------------------------------------------
    // Index page — match list
    // -----------------------------------------------------------------------

    function isIndexPage() {
        return !!qs("#match-list");
    }

    async function initIndex() {
        let matches;
        try {
            const res = await fetch(DATA_URL);
            matches = await res.json();
        } catch {
            qs("#match-list").innerHTML =
                '<p class="empty">Could not load match data.</p>';
            return;
        }

        // Sort most recent first
        matches.sort((a, b) => (b.date > a.date ? 1 : b.date < a.date ? -1 : 0));

        populateFilterOptions(matches);
        renderMatchList(matches);
        bindFilterEvents(matches);
    }

    function populateFilterOptions(matches) {
        const opponents = [...new Set(matches.map((m) => m.opponent))].sort();
        const competitions = [...new Set(matches.map((m) => m.competition))].sort();

        const oppSelect = qs("#opponent-filter");
        opponents.forEach((o) => {
            const opt = document.createElement("option");
            opt.value = o;
            opt.textContent = o;
            oppSelect.appendChild(opt);
        });

        const compSelect = qs("#competition-filter");
        competitions.forEach((c) => {
            const opt = document.createElement("option");
            opt.value = c;
            opt.textContent = c;
            compSelect.appendChild(opt);
        });
    }

    function applyFilters(matches) {
        const opponent = qs("#opponent-filter").value;
        const competition = qs("#competition-filter").value;
        const dateFrom = qs("#date-from").value;
        const dateTo = qs("#date-to").value;

        return matches.filter((m) => {
            if (opponent && m.opponent !== opponent) return false;
            if (competition && m.competition !== competition) return false;
            if (dateFrom && m.date < dateFrom) return false;
            if (dateTo && m.date > dateTo) return false;
            return true;
        });
    }

    function renderMatchList(matches) {
        const container = qs("#match-list");
        const filtered = applyFilters(matches);

        if (filtered.length === 0) {
            container.innerHTML = '<p class="empty">No matches found.</p>';
            return;
        }

        container.innerHTML = filtered
            .map((m) => {
                const homeAway = m.is_tottenham_home ? "Home" : "Away";
                const score = `${m.home_score} – ${m.away_score}`;
                return `
        <a href="match.html?id=${m.match_id}" class="match-card">
          <span class="match-date">${m.date}</span>
          <span class="match-opponent">${m.opponent} (${homeAway})</span>
          <span class="match-score">${score}</span>
          <span class="match-comp">${m.competition} · ${m.matchday}</span>
        </a>`;
            })
            .join("");
    }

    function bindFilterEvents(matches) {
        ["#opponent-filter", "#competition-filter", "#date-from", "#date-to"].forEach(
            (sel) => qs(sel).addEventListener("change", () => renderMatchList(matches))
        );

        qs("#clear-filters").addEventListener("click", () => {
            qs("#opponent-filter").value = "";
            qs("#competition-filter").value = "";
            qs("#date-from").value = "";
            qs("#date-to").value = "";
            renderMatchList(matches);
        });
    }

    // -----------------------------------------------------------------------
    // Match detail page
    // -----------------------------------------------------------------------

    function isMatchPage() {
        return !!qs("#match-detail");
    }

    async function initMatch() {
        const matchId = getQueryParam("id");
        if (!matchId) {
            qs("#match-title").textContent = "No match specified";
            return;
        }

        // Load matches index to get metadata for the title
        try {
            const res = await fetch(DATA_URL);
            const matches = await res.json();
            const match = matches.find((m) => String(m.match_id) === matchId);
            if (match) {
                const homeAway = match.is_tottenham_home ? "Home" : "Away";
                qs("#match-title").textContent =
                    `${match.opponent} (${homeAway}) — ${match.competition} ${match.matchday}`;
            }
        } catch {
            // Non-critical — title stays as fallback
        }

        const img = document.createElement("img");
        img.src = `matches/${matchId}/infographic.png`;
        img.alt = "Match infographic";
        img.className = "infographic";
        img.onerror = () => {
            qs("#infographic-container").innerHTML =
                '<p class="empty">Infographic not available.</p>';
        };
        qs("#infographic-container").appendChild(img);
    }

    // -----------------------------------------------------------------------
    // Bootstrap
    // -----------------------------------------------------------------------

    if (isIndexPage()) initIndex();
    if (isMatchPage()) initMatch();
})();
