/* Popup overlay for browse mode -- shared by all browse pages */

var popupData = null;

function showPopup(data) {
    popupData = data;
    var p = document.getElementById('browse-popup');
    document.getElementById('popup-zh').textContent = data.name || '';
    document.getElementById('popup-en').textContent = data.english_name || '';
    document.getElementById('popup-fact').textContent = data.fact || '';

    // Image
    var imgEl = document.getElementById('popup-img-el');
    var emojiEl = document.getElementById('popup-emoji');
    if (data.image) {
        imgEl.src = data.image.startsWith('/') ? data.image : '/media/' + data.image;
        imgEl.style.objectFit = 'cover';
        imgEl.style.objectPosition = data.image_position || '50% 50%';
        imgEl.style.display = 'block';
        emojiEl.style.display = 'none';
    } else {
        imgEl.style.display = 'none';
        emojiEl.style.display = 'block';
        emojiEl.textContent = data.emoji || '';
        var pi = document.querySelector('.popup-img');
        if (pi) pi.style.backgroundColor = '';
    }

    // Fact row
    document.getElementById('popup-fact-row').style.display = data.fact ? 'flex' : 'none';

    // Sound indicators
    document.getElementById('popup-sound-zh').className = 'ph-sound' + (data.audio_zh ? '' : ' muted');
    document.getElementById('popup-sound-en').className = 'ph-sound' + (data.audio_en ? '' : ' muted');
    document.getElementById('popup-sound-fact').className = 'ph-sound' + (data.audio_fact ? '' : ' muted');

    p.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    // Auto-play: Chinese first, then English after 1 second
    setTimeout(function () { playBrowseAudio('zh'); }, 400);
    setTimeout(function () { playBrowseAudio('en'); }, 1400);
}

function closeBrowsePopup(e) {
    // Only check event-target when called from an event handler
    if (e && e.type && e.target !== document.getElementById("browse-popup")) return;
    document.getElementById("browse-popup").style.display = "none";
    document.body.style.overflow = "";
    var audio = document.getElementById("popup-audio");
    audio.pause();
    audio.removeAttribute("src");
}

function playBrowseAudio(type) {
    var audio = document.getElementById('popup-audio');
    if (!audio || !popupData) return;
    var src = popupData['audio_' + type];
    if (!src) return;
    audio.src = src.startsWith('/') ? src : '/media/' + src;
    audio.load();
    audio.play().catch(function (e) {
        console.log('Audio play error:', e);
    });
}

function zoomBrowseImage() {
    var fs = document.getElementById('img-fs-overlay');
    var imgEl = document.getElementById('popup-img-el');
    var emojiEl = document.getElementById('popup-emoji');
    if (imgEl.style.display !== 'none') {
        document.getElementById('fs-emoji-el').style.display = 'none';
        var clone = fs.querySelector('img.fs-img-clone');
        if (!clone) {
            clone = document.createElement('img');
            clone.className = 'fs-img-clone';
            clone.style.cssText = 'max-width:90vw;max-height:90vh;object-fit:contain;';
            fs.insertBefore(clone, fs.querySelector('.fs-tip'));
        }
        clone.src = imgEl.src;
        clone.style.display = 'block';
    } else {
        document.getElementById('fs-emoji-el').style.display = 'block';
    }
    fs.classList.add('show');
}
