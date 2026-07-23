/* Theme toggle shared across all pages */

function toggleTheme() {
    var root = document.documentElement;
    var isDark = root.getAttribute('data-theme') === 'dark';
    if (isDark) {
        root.removeAttribute('data-theme');
        try { localStorage.setItem('theme', 'light'); } catch (e) {}
    } else {
        root.setAttribute('data-theme', 'dark');
        try { localStorage.setItem('theme', 'dark'); } catch (e) {}
    }
    updateThemeIcon();
}

function updateThemeIcon() {
    var btn = document.querySelector('.theme-toggle');
    if (!btn) return;
    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    btn.innerHTML = isDark ? '&#9728;' : '&#127769;';
}

/* Call once on load */
updateThemeIcon();
