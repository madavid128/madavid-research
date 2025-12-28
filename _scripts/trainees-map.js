/*
  Renders the trainees map using Plotly (world + USA views).
  Data source: <script type="application/json" class="trainee-map-data">…</script>

  Data:
  - `_data/trainees.yaml` (trainee entries)
  - `_data/trainee_institutions.yaml` (institution → city/region/country + lat/lon)

  UI:
  - View: World vs US projection
  - Show: Current vs Past
  - Time: year slider + play (optional)
*/
{
  const selector = "[data-trainee-map]";
  const dataSelector = ".trainee-map-data";

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const toNumber = (value) => (value === null || value === undefined || value === "" ? null : Number(value));
  const currentYear = () => new Date().getFullYear();

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

  const normalizeCountry = (raw) => String(raw || "").trim().toLowerCase();
  const isUSA = (country) => {
    const c = normalizeCountry(country);
    return c === "usa" || c === "united states" || c === "united states of america" || c.includes("united states");
  };

  const normalizeLink = (raw, siteRoot) => {
    if (!raw) return "";
    if (raw.includes("://")) return raw;
    const root = siteRoot || "/";
    const prefix = root.endsWith("/") ? root : `${root}/`;
    const path = raw.startsWith("/") ? raw.slice(1) : raw;
    return `${window.location.origin}${prefix}${path}`;
  };

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

  const buildTagControls = (root, trainees, state) => {
    const host = root.querySelector("[data-trainee-tags]");
    if (!host) return;

    const tags = new Set();
    (trainees || []).forEach((t) => {
      parseTags(t.tags).forEach((tag) => tags.add(tag));
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
        root.dispatchEvent(new CustomEvent("traineefilterschanged"));
      });
      wrap.append(button);
    };

    addChip("all");
    [...tags].sort().forEach(addChip);
    syncActive();
  };

  const placeLine = (geo) => {
    const parts = [];
    if (geo.city) parts.push(geo.city);
    if (geo.region) parts.push(geo.region);
    if (geo.country) parts.push(geo.country);
    return parts.filter(Boolean).join(", ");
  };

  const parseYearFromText = (raw) => {
    const s = String(raw || "").trim();
    const m = s.match(/\b(19|20)\d{2}\b/);
    if (!m) return null;
    const y = Number(m[0]);
    if (!Number.isFinite(y)) return null;
    return y;
  };

  const traineeYears = (t) => {
    const start = parseYearFromText(t && t.start);
    const endRaw = String(t && t.end ? t.end : "").trim();
    const end = endRaw.toLowerCase() === "present" ? currentYear() : parseYearFromText(endRaw);
    return { start, end: end ?? start };
  };

  const buildHoverInstitution = (inst, status, trainees) => {
    const where = placeLine(inst);
    const header = `<b>${escapeHtml(inst.institution || "Unknown institution")}</b>`;
    const whereLine = where ? `<br><span style="color:#b0b0b0">${escapeHtml(where)}</span>` : "";
    const sub = `<br>${escapeHtml(status === "past" ? "Past" : "Current")} trainees: ${escapeHtml(trainees.length)}`;

    const lines = trainees
      .slice()
      .sort((a, b) => String(a.name || "").localeCompare(String(b.name || "")))
      .map((t) => {
        const bits = [];
        bits.push(`<b>${escapeHtml(t.name || "Unknown")}</b>`);
        const meta = [];
        if (t.focus) meta.push(t.focus);
        if (t.department) meta.push(t.department);
        if (t._startYear || t._endYear) {
          if (t._startYear && t._endYear && t._startYear !== t._endYear) meta.push(`${t._startYear}–${t._endYear}`);
          else if (t._startYear) meta.push(String(t._startYear));
        } else if (t.start || t.end) {
          meta.push(`${t.start || ""} – ${t.end || ""}`.trim());
        }
        if (meta.length) bits.push(`<span style="color:#b0b0b0">${escapeHtml(meta.join(" · "))}</span>`);
        return bits.join("<br>");
      })
      .join("<br>• ");

    const list = trainees.length ? `<br><br>• ${lines}` : "";

    return `${header}${whereLine}${sub}${list}`;
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

  const buildLayout = (view) => {
    const background = getCssVar("--background", "#181818");
    const backgroundAlt = getCssVar("--background-alt", "#1c1c1c");
    const text = getCssVar("--text", "#ffffff");
    const lightGray = getCssVar("--light-gray", "#404040");

    return {
      paper_bgcolor: background,
      plot_bgcolor: background,
      margin: { l: 10, r: 10, t: 10, b: 10 },
      showlegend: true,
      legend: {
        orientation: "h",
        x: 0.5,
        xanchor: "center",
        y: -0.06,
        yanchor: "top",
        font: { color: text },
      },
      geo: {
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
      },
    };
  };

  const setPressed = (root, view) => {
    root.querySelectorAll("[data-trainee-view]").forEach((button) => {
      const isActive = button.dataset.traineeView === view;
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  };

  const buildTraces = (payload, state) => {
    const primary = getCssVar("--primary", "#00a878");
    const text = getCssVar("--text", "#ffffff");
    const darkGray = getCssVar("--dark-gray", "#b0b0b0");

    const home = payload.home || {};
    const homeLat = toNumber(home.lat);
    const homeLon = toNumber(home.lon);

    const instIndex = new Map();
    (payload.institutions || []).forEach((i) => {
      const key = String(i.institution || "").trim();
      if (!key) return;
      instIndex.set(key, i);
    });

    const byInst = new Map();
    const missing = [];
    let traineesTotal = 0;
    let traineesWithCoords = 0;

    (payload.trainees || []).forEach((t) => {
      traineesTotal += 1;

      const { start, end } = traineeYears(t);
      if (!state.allYears && state.year !== null) {
        if (start === null) return;
        if (state.yearMode === "active") {
          if (state.year < start || state.year > (end ?? start)) return;
        } else {
          // cumulative
          if (state.year < start) return;
        }
      }

      if (state.activeTags && state.activeTags.length) {
        const tags = parseTags(t.tags);
        const hasTag = tags.some((tag) => state.activeTags.includes(tag));
        if (!hasTag) return;
      }

      const instName = String(t.institution || "").trim();
      const inst = instIndex.get(instName);
      if (!inst) {
        missing.push({ ...t, _missingInstitution: instName });
        return;
      }
      const lat = toNumber(inst.lat);
      const lon = toNumber(inst.lon);
      if (lat === null || lon === null) {
        missing.push({ ...t, _missingInstitution: instName });
        return;
      }
      traineesWithCoords += 1;

      if (!byInst.has(instName)) {
        byInst.set(instName, { inst, current: [], past: [] });
      }

      let status = String(t.end || "").trim().toLowerCase() === "present" ? "current" : "past";
      if (!state.allYears && state.year !== null && start !== null) {
        const endY = end ?? start;
        status = endY !== null && endY < state.year ? "past" : "current";
      }
      byInst.get(instName)[status].push({ ...t, _startYear: start, _endYear: end ?? start });
    });

    const currentPoints = [];
    const pastPoints = [];

    for (const group of byInst.values()) {
      const inst = group.inst;
      const lat = toNumber(inst.lat);
      const lon = toNumber(inst.lon);
      if (lat === null || lon === null) continue;
      if (group.current.length) currentPoints.push({ inst, lat, lon, trainees: group.current });
      if (group.past.length) pastPoints.push({ inst, lat, lon, trainees: group.past });
    }

    const labelIndex = new Map();
    const addLabel = (p) => {
      const key = String(p && p.inst && p.inst.institution ? p.inst.institution : "").trim();
      if (!key) return;
      if (!labelIndex.has(key)) labelIndex.set(key, { lat: p.lat, lon: p.lon, text: key });
    };
    currentPoints.forEach(addLabel);
    pastPoints.forEach(addLabel);
    const labelPoints = [...labelIndex.values()];
    const labelsTrace = {
      type: "scattergeo",
      mode: "text",
      name: "Institutions",
      lat: labelPoints.map((p) => p.lat),
      lon: labelPoints.map((p) => p.lon),
      text: labelPoints.map((p) => p.text),
      textposition: "top center",
      // Keep labels readable, but subtle compared to marker points.
      textfont: { color: "#cbd5e1", size: 13 },
      hoverinfo: "skip",
      showlegend: false,
      visible: state.showLabels ? true : false,
    };

    const makeMarkerTrace = (items, name, color, symbol, status) => ({
      type: "scattergeo",
      mode: "markers",
      name,
      lat: items.map((p) => p.lat),
      lon: items.map((p) => p.lon),
      text: items.map((p) => buildHoverInstitution(p.inst, status, p.trainees)),
      hovertemplate: "%{text}<extra></extra>",
      marker: {
        size: items.map((p) => clamp(10 + Math.sqrt((p.trainees || []).length) * 4, 10, 26)),
        color,
        symbol,
        line: { width: 1, color: text },
        opacity: 0.95,
      },
      customdata: items.map((p) => ({
        link: p.inst && p.inst.link ? p.inst.link : "",
      })),
      visible: status === "past" ? (state.showPast ? true : "legendonly") : state.showCurrent ? true : "legendonly",
    });

    const makeLineTrace = (items, name, color, dash, opacity) => {
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
        line: { width: 2, color, dash },
        opacity,
        visible: name.toLowerCase().includes("past") ? (state.showPast ? true : "legendonly") : state.showCurrent ? true : "legendonly",
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
      hovertext: [`<b>${escapeHtml(homeText)}</b><br>${escapeHtml(home.label || "Home base")}`],
      hovertemplate: "%{hovertext}<extra></extra>",
      marker: {
        size: 16,
        color: "#ef4444",
        symbol: "star",
        line: { width: 2, color: text },
      },
      showlegend: true,
      visible: true,
    };

    const traces = [
      makeLineTrace(currentPoints, "Current connections", primary, "solid", 0.75),
      makeLineTrace(pastPoints, "Past connections", darkGray, "dash", 0.45),
      makeMarkerTrace(currentPoints, "Current trainees", primary, "circle", "current"),
      makeMarkerTrace(pastPoints, "Past trainees", darkGray, "circle", "past"),
      homeTrace,
    ];
    if (labelPoints.length) traces.push(labelsTrace);

    return {
      traces,
      stats: {
        traineesTotal,
        traineesWithCoords,
        institutionsShown: (state.showCurrent ? currentPoints.length : 0) + (state.showPast ? pastPoints.length : 0),
        institutionsCurrent: currentPoints.length,
        institutionsPast: pastPoints.length,
        missing,
      },
    };
  };

  const initOne = (root) => {
    if (root.__traineeInitDone) {
      if (typeof root.__traineeRender === "function") root.__traineeRender();
      return;
    }

    const container = root.querySelector(selector);
    const dataEl = root.querySelector(dataSelector);
    if (!container || !dataEl) return;

    const host = container;
    const loading = container.querySelector(".collab-map-loading");
    const summaryEl = root.querySelector("[data-trainee-summary]");

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

	    const viewButtons = [...root.querySelectorAll("[data-trainee-view]")];
	    const currentToggle = root.querySelector("input[data-trainee-filter='current']");
	    const pastToggle = root.querySelector("input[data-trainee-filter='past']");
	    const labelsToggle = root.querySelector("input[data-trainee-labels]");
	    const resetButton = root.querySelector("[data-trainee-reset]");
	    const timeHost = root.querySelector("[data-trainee-time]");
	    const yearAllToggle = root.querySelector("input[data-trainee-year-all]");
	    const yearSlider = root.querySelector("input[data-trainee-year]");
    const yearLabel = root.querySelector("[data-trainee-year-label]");
    const playButton = root.querySelector("[data-trainee-play]");
    const modeButtons = [...root.querySelectorAll("[data-trainee-mode]")];

	    let state = {
	      view: "world",
	      showCurrent: currentToggle ? currentToggle.checked : true,
	      showPast: pastToggle ? pastToggle.checked : true,
	      showLabels: labelsToggle ? labelsToggle.checked : true,
      activeTags: [],
      allYears: true,
      year: null,
      yearMode: "active",
	      _timer: null,
	    };

	    const prefersCompactLabels = () =>
	      Boolean(window.matchMedia && window.matchMedia("(max-width: 720px)").matches);

	    // Default labels off on mobile for readability.
	    if (labelsToggle && prefersCompactLabels()) {
	      labelsToggle.checked = false;
	      state.showLabels = false;
	    }

	    buildTagControls(root, payload.trainees, state);
	    root.addEventListener("traineefilterschanged", () => render());

    const computeYearBounds = () => {
      let minY = null;
      let maxY = null;
      for (const t of payload.trainees || []) {
        const { start, end } = traineeYears(t);
        if (start === null) continue;
        const e = end ?? start;
        minY = minY === null ? start : Math.min(minY, start);
        maxY = maxY === null ? e : Math.max(maxY, e);
      }
      return { minY, maxY };
    };

    const setModePressed = () => {
      modeButtons.forEach((btn) => {
        const key = String(btn.dataset.traineeMode || "");
        btn.setAttribute("aria-pressed", key === state.yearMode ? "true" : "false");
      });
    };

    const stopPlay = () => {
      if (state._timer) {
        window.clearInterval(state._timer);
        state._timer = null;
      }
      if (playButton) playButton.setAttribute("aria-pressed", "false");
      if (playButton) playButton.textContent = "Play";
    };

    const syncTimeControls = () => {
      if (!yearAllToggle || !yearSlider || !yearLabel) return;
      yearAllToggle.checked = Boolean(state.allYears);
      yearSlider.disabled = Boolean(state.allYears);
      if (state.allYears) {
        yearLabel.textContent = "All";
        stopPlay();
      } else {
        yearLabel.textContent = String(state.year ?? "");
      }
      setModePressed();
    };

    // Respect reduced motion: disable autoplay controls.
    const reduceMotion = document.documentElement.dataset.motion === "reduced";
    if (reduceMotion && playButton) {
      playButton.disabled = true;
      playButton.setAttribute("aria-disabled", "true");
      playButton.textContent = "Play";
      playButton.title = "Disabled (reduced motion)";
    }

	    const chooseDefaultView = () => {
      const inst = (payload.institutions || []).filter((i) => toNumber(i.lat) !== null && toNumber(i.lon) !== null);
      if (!inst.length) return "world";
      const usCount = inst.filter((i) => isUSA(i.country)).length;
      return usCount / inst.length >= 0.65 ? "us" : "world";
    };
	    state.view = chooseDefaultView();
	    setPressed(root, state.view);

    const { minY, maxY } = computeYearBounds();
    if (!minY || !maxY || !timeHost || !yearAllToggle || !yearSlider || !yearLabel || !playButton) {
      if (timeHost) timeHost.setAttribute("hidden", "hidden");
    } else {
      yearSlider.min = String(minY);
      yearSlider.max = String(maxY);
      yearSlider.step = "1";
      yearSlider.value = String(maxY);
      state.year = maxY;
      state.allYears = true;
      state.yearMode = "active";
      syncTimeControls();

      yearAllToggle.addEventListener("change", () => {
        state.allYears = Boolean(yearAllToggle.checked);
        if (!state.allYears) state.year = Number(yearSlider.value);
        syncTimeControls();
        render();
      });

      yearSlider.addEventListener("input", () => {
        state.year = Number(yearSlider.value);
        state.allYears = false;
        syncTimeControls();
        render();
      });

      modeButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
          state.yearMode = String(btn.dataset.traineeMode || "active");
          syncTimeControls();
          render();
        });
      });

      playButton.addEventListener("click", () => {
        if (state.allYears) state.allYears = false;
        if (state.year === null) state.year = Number(yearSlider.value);
        const isPlaying = Boolean(state._timer);
        if (isPlaying) {
          stopPlay();
          return;
        }
        playButton.setAttribute("aria-pressed", "true");
        playButton.textContent = "Pause";
        state._timer = window.setInterval(() => {
          if (state.allYears) {
            stopPlay();
            return;
          }
          const y = state.year ?? Number(yearSlider.value);
          const next = y >= maxY ? minY : y + 1;
          state.year = next;
          yearSlider.value = String(next);
          syncTimeControls();
          render();
        }, 700);
        syncTimeControls();
        render();
      });
    }

    const updateSummary = (stats) => {
      if (!summaryEl) return;
      const total = stats.traineesTotal || 0;
      const withCoords = stats.traineesWithCoords || 0;
      const missing = Math.max(0, total - withCoords);
      const bits = [];
      bits.push(`Trainees: ${withCoords}/${total} with coordinates`);
      bits.push(`Institutions: ${stats.institutionsCurrent || 0} current · ${stats.institutionsPast || 0} past`);
      if (state.activeTags && state.activeTags.length) bits.push(`Tags: ${state.activeTags.join(", ")}`);
      if (missing > 0) bits.push(`${missing} missing institution coordinates`);
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
      const stats = built.stats || {};
      updateSummary(stats);

      if ((stats.traineesWithCoords || 0) === 0) {
        if (loading) loading.textContent = "No trainee locations yet. Add lat/lon in _data/trainee_institutions.yaml.";
        return;
      }

      const layout = buildLayout(state.view);
      const reduceMotion = document.documentElement.dataset.motion === "reduced";
      const config = { responsive: true, displayModeBar: false };

      if (loading) loading.remove();
      await window.Plotly.react(host, traces, layout, config);
      if (reduceMotion) {
        try {
          window.Plotly.relayout(host, { "geo.projection.rotation": { lon: 0, lat: 0, roll: 0 } });
        } catch {
          // ignore
        }
      }

      if (!host.__traineeClickBound) {
        host.on("plotly_click", (event) => {
          const point = event && event.points && event.points[0];
          const link = point && point.customdata && point.customdata.link;
          if (!link) return;
          const siteRoot = host.dataset.siteRoot || "/";
          const url = normalizeLink(link, siteRoot);
          if (url) window.open(url, "_blank", "noopener,noreferrer");
        });
        host.__traineeClickBound = true;
      }
    };

    viewButtons.forEach((button) => {
      button.addEventListener("click", () => {
        state.view = button.dataset.traineeView;
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
	    if (labelsToggle) {
	      labelsToggle.addEventListener("change", () => {
	        state.showLabels = labelsToggle.checked;
	        render();
	      });
	    }

	    const resetFilters = () => {
	      stopPlay();

	      state.view = chooseDefaultView();
	      setPressed(root, state.view);

	      if (currentToggle) currentToggle.checked = true;
	      if (pastToggle) pastToggle.checked = true;
	      state.showCurrent = true;
	      state.showPast = true;

	      const labelsOn = !prefersCompactLabels();
	      if (labelsToggle) labelsToggle.checked = labelsOn;
	      state.showLabels = labelsOn;

	      state.activeTags = [];
	      buildTagControls(root, payload.trainees, state);

	      if (yearSlider && yearAllToggle) {
	        state.allYears = true;
	        yearAllToggle.checked = true;
	        const { maxY } = computeYearBounds();
	        if (maxY !== null) {
	          state.year = maxY;
	          yearSlider.value = String(maxY);
	        }
	        state.yearMode = "active";
	        syncTimeControls();
	      }

	      render();
	    };

	    if (resetButton) resetButton.addEventListener("click", resetFilters);

	    render();
	    root.__traineeInitDone = true;
	    root.__traineeRender = render;
	  };

  window.renderTraineesMaps = () => {
    const roots = document.querySelectorAll(".collab-map[data-map-kind='trainees']");
    roots.forEach((root) => {
      if (root.__traineeInitDone) return;
      if (root.__traineeObserved) {
        initOne(root);
        return;
      }
      root.__traineeObserved = true;

      const target = root.querySelector(".collab-map-plot") || root;
      if (!("IntersectionObserver" in window)) {
        initOne(root);
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => {
          const anyVisible = entries.some((e) => e.isIntersecting || e.intersectionRatio > 0);
          if (!anyVisible) return;
          observer.disconnect();
          initOne(root);
        },
        { rootMargin: "250px 0px", threshold: 0.01 },
      );

      observer.observe(target);
    });
  };

  window.addEventListener("directoryviewchange", () => {
    document.querySelectorAll(".collab-map[data-map-kind='trainees']").forEach((root) => {
      const host = root.querySelector("[data-trainee-map]");
      if (!host) return;
      if (host.offsetParent === null) return;
      if (root.__traineeInitDone && typeof root.__traineeRender === "function") {
        root.__traineeRender();
        if (window.Plotly && window.Plotly.Plots && typeof window.Plotly.Plots.resize === "function") {
          window.Plotly.Plots.resize(host);
        }
      } else if (window.renderTraineesMaps) {
        window.renderTraineesMaps();
      }
    });
  });

  window.addEventListener("DOMContentLoaded", window.renderTraineesMaps);
  window.addEventListener("load", window.renderTraineesMaps);
  if (document.readyState === "interactive" || document.readyState === "complete") {
    window.renderTraineesMaps();
  }
}
