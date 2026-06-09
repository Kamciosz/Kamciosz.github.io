// Theme toggle + reading time helpers
(function () {
  var STORAGE_KEY = "stem-news-theme";
  var toggle = document.getElementById("themeToggle");
  if (!toggle) return;

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
    toggle.textContent = theme === "dark" ? "☀" : "◐";
  }

  function getTheme() {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored) return stored;
    } catch (e) {}
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  setTheme(getTheme());
  toggle.addEventListener("click", function () {
    var current = document.documentElement.getAttribute("data-theme") || "light";
    setTheme(current === "dark" ? "light" : "dark");
  });
})();

// Topic filter (?filter=ai|security|hardware|opensource)
(function () {
  var params = new URLSearchParams(window.location.search);
  var filter = params.get("filter");
  if (!filter || filter === "all") return;
  var items = document.querySelectorAll(".news-item");
  items.forEach(function (el) {
    var tags = (el.getAttribute("data-tags") || "").toLowerCase().split(",");
    if (tags.indexOf(filter) === -1) {
      el.style.display = "none";
    }
  });
})();
