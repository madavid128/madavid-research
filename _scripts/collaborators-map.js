/*
  Renders the collaborators map using Plotly (world + USA views).
  Data source: <script type="application/json" class="collab-map-data">…</script>

  Expected fields per person (from `_data/collaborators_map.csv` or `_data/collaborators.yaml`):
  - name (string)
  - status ("current" or "past")
  - tags (array or "a;b;c" string): supports `collaborator`, `institution` (entries tagged `trainee` are excluded)
  - department/institution/city/region/country (strings; shown in hover)
  - lat/lon (numbers; required to appear on the map)
  - link (optional; opens on click)

  UI:
  - View: World vs US projection
  - Show: Current vs Past
  - Type: Collaborators/Institutions (based on tags)
  - Layout: cluster duplicate coordinates into a single marker (or jitter if disabled)
*/
{
  const selector = "[data-collab-map]";
  const dataSelector = ".collab-map-data";

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const toNumber = (value) => (value === null || value === undefined || value === "" ? null : Number(value));
  const parseTags = (raw) => {
    if (!raw) return [];
    if (Array.isArray(raw)) {
      return raw
        .map((t) => String(t).trim().toLowerCase())
        .filter(Boolean);
    }
    if (typeof raw === "string") {
      return raw
        .split(/[,;]+/g)
        .map((t) => String(t).trim().toLowerCase())
        .filter(Boolean);
    }
    return [];
  };

  const getCssVar = (name, fallback) => {
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
  };

  const escapeHtml = (text) =>
    String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  const unique = (arr) => {
    const out = [];
    const seen = new Set();
    for (const item of arr || []) {
      const value = String(item || "").trim();
      if (!value) continue;
      const key = value.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(value);
    }
    return out;
  };

  const placeLine = (person) => {
    const parts = [];
    const dept = person.department ? String(person.department).trim() : "";
    const inst = person.institution ? String(person.institution).trim() : "";
    if (dept && inst) parts.push(`${dept}, ${inst}`);
    else if (dept) parts.push(dept);
    else if (inst) parts.push(inst);
    const cityParts = [];
    if (person.city) cityParts.push(person.city);
    if (person.region) cityParts.push(person.region);
    if (person.country) cityParts.push(person.country);
    if (cityParts.length) parts.push(cityParts.join(", "));
    return parts.filter(Boolean).join(" — ");
  };

  const buildHover = (person) => {
    if (person && person.clusterCount && Array.isArray(person.clusterItems)) {
      const names = person.clusterItems.map((p) => p.name).filter(Boolean);
      const first = names.slice(0, 10).map((n) => `• ${escapeHtml(n)}`).join("<br>");
      const more = names.length > 10 ? `<br>…and ${names.length - 10} more` : "";
      const where = person.clusterPlace ? `<br><span style="color:#b0b0b0">${escapeHtml(person.clusterPlace)}</span>` : "";
      return `<b>${escapeHtml(person.clusterCount)} at one location</b>${where}<br>${first}${more}`;
    }

    const lines = [];
    lines.push(`<b>${escapeHtml(person.name || "Unknown")}</b>`);

    const where = placeLine(person);
    if (where) lines.push(`<span style="color:#b0b0b0">${escapeHtml(where)}</span>`);

    const meta = [];
    if (person.status) meta.push(String(person.status).toLowerCase() === "past" ? "Past" : "Current");
    if (person.type) meta.push(person.type);
    if (meta.length) lines.push(meta.map(escapeHtml).join(" · "));

    if (person.papers) lines.push(`Papers: ${escapeHtml(person.papers)}`);

    const tags = unique(person.tags || []);
    if (tags.length) lines.push(`Tags: ${escapeHtml(tags.join(", "))}`);

    return lines.join("<br>");
  };

  const normalizeLink = (raw, siteRoot) => {
    if (!raw) return "";
    // absolute URL
    if (raw.includes("://")) return raw;
    // site-relative path (Jekyll baseurl aware)
    const root = siteRoot || "/";
    const prefix = root.endsWith("/") ? root : `${root}/`;
    const path = raw.startsWith("/") ? raw.slice(1) : raw;
    return `${window.location.origin}${prefix}${path}`;
  };

  const normalizeCountry = (raw) => String(raw || "").trim().toLowerCase();
  const isUSA = (person) => {
    const c = normalizeCountry(person && person.country);
    return c === "usa" || c === "united states" || c === "united states of america" || c.includes("united states");
  };

  const pickType = (tags) => {
    const t = (tags || []).map((x) => String(x || "").trim().toLowerCase());
    if (t.includes("institution")) return "institution";
    return "collaborator";
  };

  const applyDuplicateLayout = (items, options) => {
    const byKey = new Map();
    const rounded = (n) => Number(n).toFixed(4);

    for (const item of items) {
      const key = `${rounded(item.lat)},${rounded(item.lon)}`;
      if (!byKey.has(key)) byKey.set(key, []);
      byKey.get(key).push(item);
    }

    const out = [];
    const jitterRadius = 0.18;

    for (const group of byKey.values()) {
      if (group.length === 1) {
        out.push(group[0]);
        continue;
      }

      if (options.clusterDuplicates) {
        const first = group[0];
        const place = placeLine(first);
        out.push({
          ...first,
          name: `${group.length} at one location`,
          clusterCount: group.length,
          clusterItems: group.map((g) => ({ name: g.name, link: g.link })),
          clusterPlace: place,
          link: "",
          papers: group.reduce((sum, g) => sum + (Number(g.papers) || 0), 0) || "",
        });
        continue;
      }

      for (let i = 0; i < group.length; i++) {
        const base = group[i];
        const angle = (2 * Math.PI * i) / group.length;
        const latJ = base.lat + jitterRadius * Math.sin(angle);
        const cos = Math.cos((base.lat * Math.PI) / 180) || 1;
        const lonJ = base.lon + (jitterRadius * Math.cos(angle)) / cos;
        out.push({
          ...base,
          lat: clamp(latJ, -89.5, 89.5),
          lon: clamp(lonJ, -180, 180),
        });
      }
    }

    return out;
  };

  const buildTraces = ({ home, people }, options) => {
    const homeLat = toNumber(home && home.lat);
    const homeLon = toNumber(home && home.lon);

    const rawCurrent = [];
    const rawPast = [];
    const missingCoords = [];
    let allWithCoords = 0;

    for (const p of people || []) {
      const lat = toNumber(p.lat);
      const lon = toNumber(p.lon);
      if (lat !== null && lon !== null) allWithCoords += 1;
      const status = (p.status || "current").toLowerCase();
      const tags = parseTags(p.tags);
      if (tags.includes("trainee")) continue;
      const type = pickType(tags);
      const entry = { ...p, lat, lon, status, tags, type };
      if (options.activeTags && options.activeTags.length) {
        const hasTag = entry.tags.some((t) => options.activeTags.includes(String(t).toLowerCase()));
        if (!hasTag) continue;
      }

      if (!options.showTypes[type]) continue;

      if (lat === null || lon === null) {
        missingCoords.push(entry);
        continue;
      }

      if (status === "past") rawPast.push(entry);
      else rawCurrent.push(entry);
    }

    const current = applyDuplicateLayout(rawCurrent, options);
    const past = applyDuplicateLayout(rawPast, options);
    const markerPoints = current.length + past.length;

    const primary = getCssVar("--primary", "#00a878");
    const text = getCssVar("--text", "#ffffff");
    const darkGray = getCssVar("--dark-gray", "#b0b0b0");

    const markerTrace = (items, name, color, symbol) => ({
      type: "scattergeo",
      mode: "markers",
      name,
      lat: items.map((p) => p.lat),
      lon: items.map((p) => p.lon),
      text: items.map((p) => buildHover(p)),
      hovertemplate: "%{text}<extra></extra>",
      marker: {
        size: items.map((p) => (p.clusterCount ? clamp(8 + Math.sqrt(p.clusterCount) * 3, 10, 22) : 8)),
        color,
        symbol,
        line: { width: 1, color: text },
        opacity: 0.95,
      },
      customdata: items.map((p) => ({
        link: p.link || "",
        name: p.name || "",
        status: p.status || "",
        type: p.type || "",
      })),
    });

    const lineTrace = (items, name, dash, opacity) => {
      const lats = [];
      const lons = [];
      for (const p of items) {
        lats.push(homeLat, p.lat, null);
        lons.push(homeLon, p.lon, null);
      }
      return {
        type: "scattergeo",
        mode: "lines",
        name,
        lat: lats,
        lon: lons,
        hoverinfo: "skip",
        line: {
          width: 2,
          color: primary,
          dash,
        },
        opacity,
        showlegend: true,
      };
    };

    const homeText = "Michael A. David";
    const homeTrace = {
      type: "scattergeo",
      mode: "markers+text",
      name: "Michael A. David (Home)",
      lat: [homeLat],
      lon: [homeLon],
      text: [homeText],
      textposition: "top center",
      hovertext: [`<b>${escapeHtml(homeText)}</b><br>${escapeHtml((home && home.label) || "Home base")}`],
      hovertemplate: "%{hovertext}<extra></extra>",
      marker: {
        size: 16,
        color: "#ef4444",
        symbol: "star",
        line: { width: 2, color: text },
      },
      showlegend: true,
    };

    const filterByType = (items, type) => items.filter((p) => p.type === type);

    const traces = [
      lineTrace(current, "Current", "solid", 0.8),
      lineTrace(past, "Past", "dash", 0.5),
      markerTrace(filterByType(current, "collaborator"), "Current collaborators", text, "circle"),
      markerTrace(filterByType(current, "institution"), "Current institutions", primary, "square"),
      markerTrace(filterByType(past, "collaborator"), "Past collaborators", darkGray, "circle"),
      markerTrace(filterByType(past, "institution"), "Past institutions", darkGray, "square"),
      homeTrace,
    ];

    // apply filter visibility
    const showCurrent = options.showCurrent;
    const showPast = options.showPast;
    traces[0].visible = showCurrent ? true : "legendonly";
    traces[1].visible = showPast ? true : "legendonly";
    traces[2].visible = showCurrent ? true : "legendonly";
    traces[3].visible = showCurrent ? true : "legendonly";
    traces[4].visible = showPast ? true : "legendonly";
    traces[5].visible = showPast ? true : "legendonly";

    return {
      traces,
      stats: {
        missingCoords,
        total: (people || []).length,
        withCoordsAll: allWithCoords,
        withCoordsFiltered: rawCurrent.length + rawPast.length,
        markerPoints,
        shownCurrent: rawCurrent.length,
        shownPast: rawPast.length,
      },
    };
  };

  const buildLayout = (view) => {
    const background = getCssVar("--background", "#181818");
    const backgroundAlt = getCssVar("--background-alt", "#1c1c1c");
    const text = getCssVar("--text", "#ffffff");
    const lightGray = getCssVar("--light-gray", "#404040");

    const commonGeo = {
      projection: { type: view === "us" ? "albers usa" : "natural earth" },
      scope: view === "us" ? "usa" : "world",
      showland: true,
      landcolor: backgroundAlt,
      showocean: true,
      oceancolor: background,
      showcountries: true,
      countrycolor: lightGray,
      showcoastlines: true,
      coastlinecolor: lightGray,
      showlakes: true,
      lakecolor: background,
      showsubunits: view === "us",
      subunitcolor: lightGray,
      bgcolor: background,
    };

    return {
      paper_bgcolor: background,
      plot_bgcolor: background,
      margin: { l: 10, r: 10, t: 10, b: 10 },
      showlegend: true,
      legend: {
        orientation: "h",
        x: 0.5,
        xanchor: "center",
        y: -0.08,
        font: { color: text },
      },
      geo: commonGeo,
      font: { color: text },
    };
  };

  const setPressed = (root, view) => {
    root.querySelectorAll("[data-collab-view]").forEach((button) => {
      const isActive = button.dataset.collabView === view;
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  };

  const buildTagControls = (root, people, state) => {
    const host = root.querySelector("[data-collab-tags]");
    if (!host) return;

    const tags = new Set();
    (people || []).forEach((p) => {
      parseTags(p.tags).forEach((tag) => tags.add(tag));
    });

    host.innerHTML = "";
    if (!tags.size) return;

    const title = document.createElement("div");
    title.className = "collab-map-tags-label";
    title.textContent = "Tags";
    host.append(title);

    const wrap = document.createElement("div");
    wrap.className = "collab-map-tags-wrap";
    host.append(wrap);

    const syncActive = () => {
      const active = state.activeTags || [];
      wrap.querySelectorAll("button[data-tag]").forEach((button) => {
        const tag = String(button.dataset.tag || "");
        const isActive = tag === "all" ? active.length === 0 : active.includes(tag);
        if (isActive) button.dataset.active = "";
        else button.removeAttribute("data-active");
      });
    };

    const addChip = (tag) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "collab-tag";
      button.textContent = tag;
      button.dataset.tag = tag;
      button.addEventListener("click", () => {
        if (tag === "all") {
          state.activeTags = [];
        } else {
          const idx = state.activeTags.indexOf(tag);
          if (idx >= 0) state.activeTags.splice(idx, 1);
          else state.activeTags.push(tag);
        }
        syncActive();
        root.dispatchEvent(new CustomEvent("collabfilterschanged"));
      });
      wrap.append(button);
    };

    addChip("all");
    [...tags].sort().forEach(addChip);
    syncActive();
  };

  const ensurePlotly = async (loadingEl, timeoutMs = 10000) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (window.Plotly && typeof window.Plotly.react === "function") return true;
      if (loadingEl) loadingEl.textContent = "Loading map library…";
      await sleep(200);
    }
    return false;
  };

  const initOne = (root) => {
    if (root.__collabInitDone) {
      if (typeof root.__collabRender === "function") root.__collabRender();
      return;
    }
    const container = root.querySelector(selector);
    const dataEl = root.querySelector(dataSelector);
    if (!container || !dataEl) return;

    const host = container;
    const loading = container.querySelector(".collab-map-loading");
    if (!host) return;

    let payload;
    try {
      payload = JSON.parse(dataEl.textContent);
    } catch {
      if (loading) loading.textContent = "Map data failed to load.";
      return;
    }

    const homeLat = toNumber(payload && payload.home && payload.home.lat);
    const homeLon = toNumber(payload && payload.home && payload.home.lon);
    if (homeLat === null || homeLon === null) {
      if (loading) loading.textContent = "Home location missing (map_home.yaml).";
      return;
    }

    const viewButtons = [...root.querySelectorAll("[data-collab-view]")];
    const currentToggle = root.querySelector("input[data-collab-filter='current']");
    const pastToggle = root.querySelector("input[data-collab-filter='past']");
    const typeToggles = [...root.querySelectorAll("input[data-collab-type]")];
    const clusterToggle = root.querySelector("input[data-collab-cluster='duplicates']");
    const summaryEl = root.querySelector("[data-collab-summary]");

    let state = {
      view: "world",
      showCurrent: currentToggle ? currentToggle.checked : true,
      showPast: pastToggle ? pastToggle.checked : true,
      showTypes: { collaborator: true, institution: true },
      activeTags: [],
      clusterDuplicates: clusterToggle ? clusterToggle.checked : true,
    };

    buildTagControls(root, payload.people, state);
    root.addEventListener("collabfilterschanged", () => render());

    const chooseDefaultView = () => {
      const withCoords = [];
      for (const p of payload.people || []) {
        const lat = toNumber(p.lat);
        const lon = toNumber(p.lon);
        if (lat === null || lon === null) continue;
        withCoords.push(p);
      }
      if (!withCoords.length) return "world";
      const usCount = withCoords.filter((p) => isUSA(p)).length;
      return usCount / withCoords.length >= 0.65 ? "us" : "world";
    };

    state.view = chooseDefaultView();
    setPressed(root, state.view);

    const syncTypeState = () => {
      const next = { collaborator: false, institution: false };
      typeToggles.forEach((input) => {
        const key = String(input.dataset.collabType || "");
        if (key && Object.prototype.hasOwnProperty.call(next, key)) next[key] = Boolean(input.checked);
      });
      // never allow "none selected"
      if (!next.collaborator && !next.institution) {
        next.collaborator = true;
        typeToggles.forEach((input) => {
          if (input.dataset.collabType === "collaborator") input.checked = true;
        });
      }
      state.showTypes = next;
    };
    syncTypeState();

    const updateSummary = (payloadStats, traceStats) => {
      if (!summaryEl) return;
      const total = traceStats.total || (payload.people || []).length;
      const withCoordsAll = traceStats.withCoordsAll || 0;
      const shown = (traceStats.shownCurrent || 0) + (traceStats.shownPast || 0);
      const markerPoints = traceStats.markerPoints || 0;
      const missing = Math.max(0, total - withCoordsAll);
      const bits = [];
      bits.push(`Visible: ${shown} entries`);
      if (state.clusterDuplicates && markerPoints && markerPoints !== shown) {
        bits.push(`clustered into ${markerPoints} markers`);
      }
      bits.push(`coordinates: ${withCoordsAll}/${total}`);
      if (missing > 0) bits.push(`${missing} missing coordinates`);
      summaryEl.textContent = bits.join(" · ");
    };

    const render = async () => {
      const hasPlotly = await ensurePlotly(loading, 10000);
      if (!hasPlotly) {
        if (loading) loading.textContent = "Map library failed to load (Plotly).";
        return;
      }

      const built = buildTraces(payload, state);
      const traces = built.traces;
      const traceStats = built.stats || { missingCoords: [], shownCurrent: 0, shownPast: 0 };
      updateSummary(payload, traceStats);

      if ((traceStats.shownCurrent || 0) + (traceStats.shownPast || 0) === 0) {
        if (loading) loading.textContent = "No collaborator locations yet. Add lat/lon in _data/collaborators_map.csv.";
        return;
      }
      const layout = buildLayout(state.view);
      const config = { responsive: true, displayModeBar: false };

      if (loading) loading.remove();
      await window.Plotly.react(host, traces, layout, config);

      if (!host.__collabClickBound) {
        host.on("plotly_click", (event) => {
          const point = event && event.points && event.points[0];
          const link = point && point.customdata && point.customdata.link;
          if (!link) return;
          const siteRoot = host.dataset.siteRoot || "/";
          const url = normalizeLink(link, siteRoot);
          if (url) window.open(url, "_blank", "noopener,noreferrer");
        });
        host.__collabClickBound = true;
      }
    };

    viewButtons.forEach((button) => {
      button.addEventListener("click", () => {
        state.view = button.dataset.collabView;
        setPressed(root, state.view);
        render();
      });
    });

    if (currentToggle) {
      currentToggle.addEventListener("change", () => {
        state.showCurrent = currentToggle.checked;
        render();
      });
    }
    if (pastToggle) {
      pastToggle.addEventListener("change", () => {
        state.showPast = pastToggle.checked;
        render();
      });
    }
    typeToggles.forEach((input) => {
      input.addEventListener("change", () => {
        syncTypeState();
        render();
      });
    });
    if (clusterToggle) {
      clusterToggle.addEventListener("change", () => {
        state.clusterDuplicates = clusterToggle.checked;
        render();
      });
    }

    render();
    root.__collabInitDone = true;
    root.__collabRender = render;
  };

  window.renderCollaboratorsMaps = () => {
    document
      .querySelectorAll(".collab-map[data-map-kind='collaborators']")
      .forEach((root) => initOne(root));
  };

  window.addEventListener("DOMContentLoaded", window.renderCollaboratorsMaps);
  window.addEventListener("load", window.renderCollaboratorsMaps);
  if (document.readyState === "interactive" || document.readyState === "complete") {
    window.renderCollaboratorsMaps();
  }
}
