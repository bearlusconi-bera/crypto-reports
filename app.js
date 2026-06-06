/* Daily Crypto Reports — client-side SPA (no build step).
 * Reads manifest.json, renders a list, and renders individual reports
 * from reports/*.md using marked + DOMPurify. Hash routing: #/<date>. */

(function () {
  "use strict";

  var REPO_URL = "https://github.com/bearlusconi-bera/crypto-reports";

  var els = {};
  var manifest = null;

  function $(id) { return document.getElementById(id); }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  function fmtDate(dateStr) {
    // dateStr: YYYY-MM-DD
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateStr || "");
    if (!m) return dateStr || "";
    var d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
    return d.toLocaleDateString(undefined, {
      weekday: "short", year: "numeric", month: "short", day: "numeric",
      timeZone: "UTC"
    });
  }

  function setStatus(msg) {
    els.status.textContent = msg || "";
    els.status.style.display = msg ? "block" : "none";
  }

  function showList() {
    els.reportView.hidden = true;
    els.reportView.innerHTML = "";
    els.listView.hidden = false;
    els.backBtn.hidden = true;
    els.title.textContent = "📈 Daily Crypto Reports";
    if (manifest && manifest.reports) {
      els.count.textContent = manifest.reports.length + " reports";
    }
    window.scrollTo(0, 0);
  }

  function renderList() {
    var list = els.reportList;
    list.innerHTML = "";
    if (!manifest || !manifest.reports || !manifest.reports.length) {
      setStatus("No reports yet.");
      return;
    }
    setStatus("");

    var daily = manifest.reports.filter(function (r) { return r.type !== "other"; });
    var other = manifest.reports.filter(function (r) { return r.type === "other"; });

    daily.forEach(function (r) { list.appendChild(card(r, false)); });

    if (other.length) {
      var label = document.createElement("div");
      label.className = "section-label";
      label.textContent = "Summaries & other";
      list.appendChild(label);
      other.forEach(function (r) { list.appendChild(card(r, true)); });
    }
  }

  function card(r, isSummary) {
    var a = document.createElement("a");
    a.className = "card" + (isSummary ? " summary" : "");
    a.href = "#/" + encodeURIComponent(r.id || r.date || r.file);

    var date = document.createElement("div");
    date.className = "card-date";
    date.textContent = r.type === "other" ? (r.title || r.file) : fmtDate(r.date);
    a.appendChild(date);

    if (r.type !== "other" && r.title) {
      var t = document.createElement("div");
      t.className = "card-title";
      t.textContent = r.title;
      a.appendChild(t);
    }
    if (r.preview) {
      var p = document.createElement("p");
      p.className = "card-preview";
      p.textContent = r.preview;
      a.appendChild(p);
    }
    return a;
  }

  function findReport(id) {
    if (!manifest || !manifest.reports) return null;
    for (var i = 0; i < manifest.reports.length; i++) {
      var r = manifest.reports[i];
      if ((r.id && r.id === id) || r.date === id || r.file === id) return r;
    }
    return null;
  }

  function renderMarkdown(md) {
    var html = window.marked.parse(md, { gfm: true, breaks: false });
    if (window.DOMPurify) {
      html = window.DOMPurify.sanitize(html, { ADD_ATTR: ["target"] });
    }
    return html;
  }

  function openReport(id) {
    var r = findReport(id);
    if (!r) { setStatus("Report not found."); showList(); return; }

    els.listView.hidden = true;
    els.reportView.hidden = false;
    els.backBtn.hidden = false;
    els.count.textContent = "";
    els.title.textContent = r.type === "other" ? (r.title || r.file) : fmtDate(r.date);
    els.reportView.innerHTML = "";
    setStatus("Loading…");
    window.scrollTo(0, 0);

    fetch("./reports/" + encodeURIComponent(r.file), { cache: "no-cache" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.text();
      })
      .then(function (md) {
        setStatus("");
        els.reportView.innerHTML = renderMarkdown(md);
        enhance(els.reportView);
        window.scrollTo(0, 0);
      })
      .catch(function (err) {
        setStatus("Could not load report: " + err.message);
      });
  }

  function enhance(root) {
    // External links open in a new tab
    root.querySelectorAll("a[href^='http']").forEach(function (a) {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    });
    // Wrap tables so they scroll horizontally instead of overflowing
    root.querySelectorAll("table").forEach(function (tbl) {
      if (tbl.parentElement && tbl.parentElement.classList.contains("table-wrap")) return;
      var wrap = document.createElement("div");
      wrap.className = "table-wrap";
      tbl.parentNode.insertBefore(wrap, tbl);
      wrap.appendChild(tbl);
    });
  }

  function route() {
    var hash = window.location.hash || "";
    var m = /^#\/(.+)$/.exec(hash);
    if (m) openReport(decodeURIComponent(m[1]));
    else showList();
  }

  function boot() {
    els = {
      main: $("main"), listView: $("listView"), reportView: $("reportView"),
      reportList: $("reportList"), backBtn: $("backBtn"), title: $("title"),
      count: $("count"), status: $("status"), repoLink: $("repoLink")
    };
    els.repoLink.href = REPO_URL;
    els.backBtn.addEventListener("click", function () {
      if (window.location.hash) window.location.hash = "";
      else showList();
    });
    window.addEventListener("hashchange", route);

    setStatus("Loading reports…");
    fetch("./manifest.json", { cache: "no-cache" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        manifest = data;
        renderList();
        route();
      })
      .catch(function (err) {
        setStatus("Could not load manifest.json: " + err.message);
      });
  }

  // marked/DOMPurify are deferred; ensure they're present before booting.
  function whenLibsReady(fn, tries) {
    tries = tries || 0;
    if (window.marked && typeof window.marked.parse === "function") return fn();
    if (tries > 100) { setStatus("Failed to load markdown library."); return; }
    setTimeout(function () { whenLibsReady(fn, tries + 1); }, 50);
  }

  ready(function () { whenLibsReady(boot); });
})();
