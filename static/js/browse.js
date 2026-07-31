/* Browse mode — tile grid, group filter, letter dividers, visited state.
 * Usage: window.browseApp({slug, items, csrfToken}) — called from category_browse.html.
 */
(function (global) {
    'use strict';

    global.browseApp = function (cfg) {
        var slug = cfg.slug;
        var csrf = cfg.csrfToken;
        var storageKey = 'lc-visited-' + slug;
        var browseItems = cfg.items;

        // Load visited from localStorage (wrapped for private browsing mode)
        var visited = new Set();
        try { visited = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]')); } catch (e) {}

        // Apply visited state to tiles
        function applyVisited() {
            document.querySelectorAll('#browse-grid-' + slug + ' .b-tile').forEach(function (t) {
                var id = parseInt(t.getAttribute('data-item-id'), 10);
                if (visited.has(id)) {
                    t.classList.add('visited');
                    t.querySelector('.bt-flag').style.display = 'flex';
                } else {
                    t.classList.remove('visited');
                    t.querySelector('.bt-flag').style.display = 'none';
                }
            });
        }

        function saveVisited() {
            try { localStorage.setItem(storageKey, JSON.stringify(Array.from(visited))); } catch (e) {}
        }

        applyVisited();

        // Reset visited state (button "再来一次")
        global.resetVisited = function (s) {
            if (s !== slug) return;
            visited.clear();
            try { localStorage.removeItem(storageKey); } catch (e) {}
            applyVisited();
            fetch(cfg.resetUrl + s + '/', { method: 'POST', headers: { 'X-CSRFToken': csrf } }).catch(function () {});
        };

        // Open popup for a tile
        global.openBrowsePopup = function (tile) {
            var id = parseInt(tile.getAttribute('data-item-id'), 10);
            visited.add(id);
            saveVisited();
            applyVisited();
            // Find index in browseItems array
            var idx = 0;
            for (var i = 0; i < browseItems.length; i++) {
                if (browseItems[i].id === id) { idx = i; break; }
            }
            showPopup(browseItems, idx);
            fetch(cfg.markViewedUrl + id + '/', { method: 'POST', headers: { 'X-CSRFToken': csrf } }).catch(function () {});
        };

        // ---- Letter divider toggle (拼音默认关；英文排序模式初始开启) ----
        var lettersEnabled = cfg.lettersEnabled === true;

        function updateLetterDividers() {
            var grid = document.getElementById('browse-grid-' + slug);
            if (!lettersEnabled) {
                grid.querySelectorAll('.b-letter-divider').forEach(function (dv) {
                    dv.style.display = 'none';
                });
                return;
            }
            // Letter dividers only show if a visible tile follows them
            var visibleLetters = new Set();
            grid.querySelectorAll('.b-tile').forEach(function (tile) {
                if (tile.style.display !== 'none') {
                    var prev = tile.previousElementSibling;
                    while (prev && !prev.classList.contains('b-letter-divider')) {
                        prev = prev.previousElementSibling;
                    }
                    if (prev) visibleLetters.add(prev.getAttribute('data-letter'));
                }
            });
            grid.querySelectorAll('.b-letter-divider').forEach(function (dv) {
                dv.style.display = visibleLetters.has(dv.getAttribute('data-letter')) ? '' : 'none';
            });
        }

        global.toggleLetters = function (btn) {
            lettersEnabled = !lettersEnabled;
            btn.classList.toggle('active', lettersEnabled);
            updateLetterDividers();
        };

        // 排序模式切换：mode = 'zh'（拼音）/ 'en'（英文首字母）
        // 不同模式点击 → 重新加载切换排序（英文模式加载后自动显示字母分块）；
        // 已是当前模式 → 当作字母分块开关
        global.toggleSort = function (btn, mode) {
            var curEn = window.location.search.indexOf('sort=en') !== -1;
            if (mode === 'en' && !curEn) {
                window.location.href = window.location.pathname + '?sort=en';
                return;
            }
            if (mode === 'zh' && curEn) {
                window.location.href = window.location.pathname;
                return;
            }
            toggleLetters(btn);
        };

        // ---- Group filter ----
        global.filterGroup = function (btn, group) {
            // Toggle active style (selected button shows text)
            document.querySelectorAll('#group-tabs-' + slug + ' .group-tab').forEach(function (t) {
                t.classList.remove('active');
            });
            btn.classList.add('active');

            // Show/hide tiles
            var grid = document.getElementById('browse-grid-' + slug);
            grid.querySelectorAll('.b-tile').forEach(function (tile) {
                tile.style.display = (group === 'all' || tile.getAttribute('data-group') === group) ? '' : 'none';
            });

            // Letter dividers follow the filtered tiles
            updateLetterDividers();
        };

        // Init: letter dividers hidden by default
        updateLetterDividers();
    };
})(window);
