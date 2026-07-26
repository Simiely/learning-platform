/**
 * Confetti burst effect for quiz correct answers.
 *
 * Usage:
 *   Confetti.launch(targetElement);
 *   // or with a specific canvas:
 *   Confetti.launch(imgElement, 'confetti-canvas');
 */
(function() {
    var _audioCtx = null;
    function getAudioCtx() {
        if (!_audioCtx) {
            try { _audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch(e) {}
        }
        return _audioCtx;
    }

    window.Confetti = {
        launch: function(targetImg, canvasId) {
            canvasId = canvasId || 'confetti-canvas';
            this.playCorrectSound();

            var c = document.getElementById(canvasId);
            if (!c) return;

            c.style.display = 'block';
            var ctx = c.getContext('2d');
            var dpr = window.devicePixelRatio || 1;
            if (dpr > 2) dpr = 2;
            c.width = window.innerWidth * dpr;
            c.height = window.innerHeight * dpr;
            c.style.width = window.innerWidth + 'px';
            c.style.height = window.innerHeight + 'px';
            ctx.scale(dpr, dpr);

            var colors = ['#ff9292','#f4a261','#e76f51','#2a9d8f','#e9c46a','#90be6d'];
            var particles = [];
            var total = 80;

            var rect = targetImg ? targetImg.getBoundingClientRect() : null;
            var ox = rect ? (rect.left + rect.width / 2) : window.innerWidth / 2;
            var oy = rect ? rect.bottom : window.innerHeight * 0.45;

            for (var i = 0; i < total; i++) {
                var angle = Math.random() * Math.PI * 2;
                var speed = 2 + Math.random() * 6;
                var size = 4 + Math.random() * 6;
                particles.push({
                    x: ox, y: oy,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    size: size,
                    life: 1
                });
            }

            var frame = 0;
            function draw() {
                ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
                for (var i = 0; i < particles.length; i++) {
                    var p = particles[i];
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.08;
                    p.life -= 0.01;
                    if (p.life <= 0) continue;
                    ctx.save();
                    ctx.globalAlpha = p.life;
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
                frame++;
                if (frame < 120) { requestAnimationFrame(draw); }
                else { c.style.display = 'none'; }
            }
            requestAnimationFrame(draw);
        },

        playCorrectSound: function() {
            try {
                var ctx = getAudioCtx();
                if (!ctx) return;
                var now = ctx.currentTime;
                [523, 659, 784].forEach(function(freq, i) {
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.value = freq;
                    gain.gain.setValueAtTime(0.03, now + i * 0.12);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.12 + 0.2);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + i * 0.12);
                    osc.stop(now + i * 0.12 + 0.2);
                });
            } catch(e) {}
        },

        playWrongSound: function() {
            try {
                var ctx = getAudioCtx();
                if (!ctx) return;
                var osc = ctx.createOscillator();
                var gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(440, ctx.currentTime);
                osc.frequency.linearRampToValueAtTime(300, ctx.currentTime + 0.5);
                gain.gain.setValueAtTime(0.02, ctx.currentTime);
                gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.6);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.6);
            } catch(e) {}
        }
    };
})();
