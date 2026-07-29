/**
 * Shared audio player utility.
 * Handles audio playback with preload and error recovery — used by both
 * card mode and browse popup.
 *
 * Usage:
 *   var player = AudioPlayer(document.getElementById('my-audio'));
 *   player.play('zh', items, currentIndex);
 *   player.stop();
 *   player.playSequence(items, currentIndex);  // zh → wait 0.5s → en
 */
(function() {
    window.AudioPlayer = function(audioEl) {
        if (!audioEl) {
            console.warn('AudioPlayer: no audio element provided');
            return { play: function(){}, stop: function(){}, playSequence: function(){} };
        }

        var currentItems = null;
        var currentIndex = 0;
        var sequenceId = 0;       // increments each playSequence, cancels stale tasks
        var enTimer = null;       // pending English timeout
        var fallbackTimer = null; // pending metadata fallback timeout

        function play(type, items, idx) {
            if (items) { currentItems = items; }
            if (typeof idx === 'number') { currentIndex = idx; }
            var data = currentItems ? currentItems[currentIndex] : null;
            if (!data) return;
            var src = data['audio_' + type];
            if (!src) return;
            audioEl.src = typeof src === 'string' && !src.startsWith('/') && !src.startsWith('http')
                ? '/media/' + src
                : src;
            audioEl.load();
            audioEl.play().catch(function(e) {
                console.log('Audio play error:', e);
            });
        }

        function stop() {
            cancelPending();
            audioEl.pause();
            audioEl.removeAttribute('src');
        }

        function cancelPending() {
            sequenceId++;
            if (enTimer) { clearTimeout(enTimer); enTimer = null; }
            if (fallbackTimer) { clearTimeout(fallbackTimer); fallbackTimer = null; }
        }

        function playSequence(items, idx, gapSeconds) {
            if (arguments.length < 3) gapSeconds = 0.1;

            // Cancel anything from a previous sequence
            cancelPending();
            var mySeqId = sequenceId;

            currentItems = items;
            currentIndex = idx;
            var data = items ? items[idx] : null;
            if (!data) return;

            if (!data.audio_zh) {
                enTimer = setTimeout(function() {
                    if (sequenceId !== mySeqId) return;
                    play('en');
                }, 300);
                return;
            }

            // Play Chinese now
            audioEl.pause();
            play('zh');

            // Probe Chinese audio duration to schedule English
            var probe = new Audio();
            var done = false;
            probe.src = data.audio_zh.startsWith('/') || data.audio_zh.startsWith('http')
                ? data.audio_zh : '/media/' + data.audio_zh;
            probe.preload = 'metadata';

            function onDurationKnown() {
                if (done || sequenceId !== mySeqId) return;
                done = true;
                var duration = probe.duration || 2;
                var waitMs = (duration * 1000) + (gapSeconds * 1000);
                enTimer = setTimeout(function() {
                    if (sequenceId !== mySeqId) return;
                    play('en');
                }, waitMs);
                // Cleanup
                probe.removeEventListener('loadedmetadata', onDurationKnown);
                probe.src = '';
                probe.load();
            }

            probe.addEventListener('loadedmetadata', onDurationKnown);
            probe.addEventListener('error', function() {
                if (!done && sequenceId === mySeqId) {
                    done = true;
                    // Audio file might be missing; skip to English after short delay
                    enTimer = setTimeout(function() {
                        if (sequenceId !== mySeqId) return;
                        play('en');
                    }, 500);
                    probe.src = '';
                }
            });
            fallbackTimer = setTimeout(function() {
                if (!done && sequenceId === mySeqId) {
                    onDurationKnown();
                }
            }, 2000);
        }

        return { play: play, stop: stop, playSequence: playSequence };
    };
})();
