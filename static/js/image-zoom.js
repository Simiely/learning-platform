/**
 * Image zoom / pan utility.
 * Supports wheel zoom, pinch zoom, mouse drag, touch drag, double-click reset.
 *
 * Usage:
 *   ImageZoom.init('card-fs-overlay', 'fs-zoom-wrap', 'fs-img-clone');
 */
(function() {
    window.ImageZoom = {
        init: function(overlayId, wrapId, cloneId) {
            var overlay = document.getElementById(overlayId);
            var wrap = document.getElementById(wrapId);
            var clone = document.getElementById(cloneId);
            if (!overlay || !wrap || !clone) return;

            var scale = 1, minScale = 1, maxScale = 5;
            var tx = 0, ty = 0;

            function applyTransform() {
                clone.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
            }
            function resetAll() { scale = 1; tx = 0; ty = 0; applyTransform(); }

            // Wheel zoom
            wrap.addEventListener('wheel', function(e) {
                e.preventDefault();
                scale = Math.min(maxScale, Math.max(minScale, scale + (e.deltaY > 0 ? -0.15 : 0.15)));
                if (scale === 1) { tx = 0; ty = 0; }
                applyTransform();
                clone.style.cursor = scale > 1 ? 'grab' : 'zoom-in';
            }, { passive: false });

            // Pinch zoom (touch)
            var initialDist = 0, initialScale = 1;
            wrap.addEventListener('touchstart', function(e) {
                if (e.touches.length === 2) {
                    initialDist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                                             e.touches[0].clientY - e.touches[1].clientY);
                    initialScale = scale;
                }
            });
            wrap.addEventListener('touchmove', function(e) {
                if (e.touches.length === 2 && initialDist > 0) {
                    scale = Math.min(maxScale, Math.max(minScale,
                        initialScale * Math.hypot(
                            e.touches[0].clientX - e.touches[1].clientX,
                            e.touches[0].clientY - e.touches[1].clientY
                        ) / initialDist));
                    applyTransform();
                }
            });

            // Drag (mouse) — attach to overlay, not window, so cleanup is automatic
            var dragging = false, dx = 0, dy = 0;
            clone.addEventListener('mousedown', function(e) {
                if (scale > 1) {
                    dragging = true; dx = e.clientX - tx; dy = e.clientY - ty;
                    clone.style.cursor = 'grabbing';
                    e.preventDefault();
                }
            });
            document.addEventListener('mousemove', function onMove(e) {
                if (!dragging) return;
                tx = e.clientX - dx; ty = e.clientY - dy;
                applyTransform();
            });
            document.addEventListener('mouseup', function onUp() {
                if (dragging) { dragging = false; clone.style.cursor = scale > 1 ? 'grab' : 'zoom-in'; }
            });

            // Drag (touch single finger) — on wrap element only
            wrap.addEventListener('touchstart', function(e) {
                if (e.touches.length === 1 && scale > 1) {
                    dragging = true; dx = e.touches[0].clientX - tx; dy = e.touches[0].clientY - ty;
                }
            });
            wrap.addEventListener('touchmove', function(e) {
                if (dragging && e.touches.length === 1 && scale > 1) {
                    tx = e.touches[0].clientX - dx; ty = e.touches[0].clientY - dy;
                    applyTransform();
                }
            });
            wrap.addEventListener('touchend', function() { dragging = false; });

            // Double-click to reset
            clone.addEventListener('dblclick', function() { resetAll(); clone.style.cursor = 'grab'; });

            // Reset on close
            overlay.addEventListener('click', function(e) {
                var t = e.target;
                if (t.classList.contains('fs-close') || t.id === overlayId
                    || t.id === wrapId || t.classList.contains('fs-tip')) {
                    resetAll(); clone.style.cursor = 'grab';
                }
            });
        }
    };
})();
