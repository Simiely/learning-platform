/* Cards mode — full-viewport flashcard with prev/next/random, audio, zoom.
 * Usage: window.cardsApp({items, csrfToken}) — called from category_cards.html.
 */
(function (global) {
    'use strict';

    global.cardsApp = function (cfg) {
        var items = cfg.items;
        var csrf = cfg.csrfToken;
        var current = Math.floor(Math.random() * items.length);
        var cardAudio = AudioPlayer(document.getElementById('card-audio'));

        function markCardViewed() {
            var it = items[current];
            fetch(cfg.markViewedUrl + it.id + '/', { method: 'POST', headers: { 'X-CSRFToken': csrf } }).catch(function () {});
        }

        function autoPlaySequence() {
            cardAudio.playSequence(items, current);
        }

        function render() {
            var it = items[current];
            if (!it) return;
            document.getElementById('card-counter').textContent = (current + 1) + ' / ' + items.length;
            document.getElementById('card-zh').textContent = it.name;
            document.getElementById('card-en').textContent = it.english_name || '';
            document.getElementById('card-fact').textContent = it.fact || '';

            var img = document.getElementById('card-img');
            var emoji = document.getElementById('card-emoji');
            if (it.image) {
                img.src = it.image;
                img.style.objectFit = 'cover';
                img.style.objectPosition = iPadDetect.centerPos(iPadDetect.getImagePos(it));
                img.style.display = 'block';
                emoji.style.display = 'none';
            } else {
                img.style.display = 'none';
                emoji.style.display = 'block';
                emoji.textContent = it.emoji || '';
            }

            document.getElementById('card-fact-row').style.display = it.fact ? 'flex' : 'none';
            document.getElementById('card-sound-zh').className = 'ph-sound' + (it.audio_zh ? '' : ' muted');
            document.getElementById('card-sound-en').className = 'ph-sound' + (it.audio_en ? '' : ' muted');
            document.getElementById('card-sound-fact').className = 'ph-sound' + (it.audio_fact ? '' : ' muted');
        }

        global.cardPrev = function () { current = current > 0 ? current - 1 : items.length - 1; render(); markCardViewed(); autoPlaySequence(); };
        global.cardNext = function () { current = current < items.length - 1 ? current + 1 : 0; render(); markCardViewed(); autoPlaySequence(); };
        global.cardRandom = function () { current = Math.floor(Math.random() * items.length); render(); markCardViewed(); autoPlaySequence(); };

        global.playCardAudio = function (type) {
            cardAudio.play(type, items, current);
        };

        global.zoomCardImage = function () {
            var img = document.getElementById('card-img');
            if (img.style.display === 'none') return;
            var clone = document.getElementById('fs-img-clone');
            clone.src = img.src;
            document.getElementById('card-fs-overlay').classList.add('show');
        };

        global.closeZoom = function (e) {
            var t = e.target;
            if (t.classList.contains('fs-close') || t.id === 'card-fs-overlay'
                || t.id === 'fs-zoom-wrap' || t.classList.contains('fs-tip')) {
                document.getElementById('card-fs-overlay').classList.remove('show');
            }
        };

        // Init shared zoom module
        ImageZoom.init('card-fs-overlay', 'fs-zoom-wrap', 'fs-img-clone');

        render();
        markCardViewed();
        // Try autoplay on load; if blocked, unlock audio on first user interaction
        autoPlaySequence();
        var unlockAudio = function () { autoPlaySequence(); };
        document.addEventListener('click', unlockAudio, { once: true });
        document.addEventListener('touchend', unlockAudio, { once: true });

        document.querySelector('main.container').classList.add('container-card');
    };
})(window);
