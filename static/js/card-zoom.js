/* Image zoom interactions for card mode */

var zoomScale = 1;
var zoomBaseX = 0, zoomBaseY = 0;
var zoomDragging = false, zoomDragStartX, zoomDragStartY, zoomStartBaseX, zoomStartBaseY;
var touchDist = 0;

function zoomCardImage() {
    var fs = document.getElementById('card-fs-overlay');
    var img = document.getElementById('card-img');
    if (img.style.display === 'none') return;
    var clone = document.getElementById('fs-img-clone');
    clone.src = img.src;
    zoomScale = 1;
    zoomBaseX = 0;
    zoomBaseY = 0;
    clone.style.transform = 'scale(1) translate(0,0)';
    fs.classList.add('show');
}

function closeZoom(e) {
    var el = e.target;
    if (el === e.currentTarget || el.classList.contains('fs-close') || el.classList.contains('fs-tip') || el.classList.contains('fs-zoom-wrap') || (el.tagName === 'IMG' && zoomScale <= 1 && zoomBaseX === 0 && zoomBaseY === 0)) {
        document.getElementById('card-fs-overlay').classList.remove('show');
    }
}

function initCardZoom() {
    var wrap = document.getElementById('fs-zoom-wrap');
    if (!wrap) return;

    wrap.addEventListener('wheel', function (e) {
        e.preventDefault();
        var delta = e.deltaY > 0 ? -0.1 : 0.1;
        zoomScale = Math.max(0.5, Math.min(5, zoomScale + delta));
        var clone = document.getElementById('fs-img-clone');
        clone.style.transform = 'scale(' + zoomScale + ') translate(' + zoomBaseX + 'px,' + zoomBaseY + 'px)';
        clone.style.transition = zoomScale === 1 && zoomBaseX === 0 && zoomBaseY === 0 ? 'transform .15s ease' : 'none';
    });

    wrap.addEventListener('mousedown', function (e) {
        if (e.button !== 0 || zoomScale <= 1) return;
        zoomDragging = true;
        zoomDragStartX = e.clientX;
        zoomDragStartY = e.clientY;
        zoomStartBaseX = zoomBaseX;
        zoomStartBaseY = zoomBaseY;
        document.getElementById('fs-img-clone').style.cursor = 'grabbing';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function (e) {
        if (!zoomDragging) return;
        zoomBaseX = zoomStartBaseX + (e.clientX - zoomDragStartX);
        zoomBaseY = zoomStartBaseY + (e.clientY - zoomDragStartY);
        document.getElementById('fs-img-clone').style.transform =
            'scale(' + zoomScale + ') translate(' + zoomBaseX + 'px,' + zoomBaseY + 'px)';
    });

    document.addEventListener('mouseup', function () {
        zoomDragging = false;
        document.getElementById('fs-img-clone').style.cursor = 'grab';
    });

    // Touch pinch support
    wrap.addEventListener('touchstart', function (e) {
        if (e.touches.length === 2) {
            var dx = e.touches[0].clientX - e.touches[1].clientX;
            var dy = e.touches[0].clientY - e.touches[1].clientY;
            touchDist = Math.sqrt(dx * dx + dy * dy);
        }
    });

    wrap.addEventListener('touchmove', function (e) {
        if (e.touches.length === 2) {
            e.preventDefault();
            var dx = e.touches[0].clientX - e.touches[1].clientX;
            var dy = e.touches[0].clientY - e.touches[1].clientY;
            var dist = Math.sqrt(dx * dx + dy * dy);
            var delta = (dist - touchDist) / 200;
            zoomScale = Math.max(0.5, Math.min(5, zoomScale + delta));
            touchDist = dist;
            document.getElementById('fs-img-clone').style.transform =
                'scale(' + zoomScale + ') translate(' + zoomBaseX + 'px,' + zoomBaseY + 'px)';
        }
    });
}
