/* Quiz mode — Alpine-driven 10-question practice.
 * Usage: x-data="quizApp({categorySlug, csrfToken, questionUrl, submitUrl, quizUrl, browseUrl})"
 */
function quizApp(cfg) {
    'use strict';
    var QUIZ_SIZE = 10; // 每轮题数

    return {
        categorySlug: cfg.categorySlug,
        quizUrl: cfg.quizUrl,
        browseUrl: cfg.browseUrl,
        state: 'playing',
        current: 0,
        score: 0,
        currentQuestion: null,
        selectedId: null,
        answered: false,
        isCorrect: false,

        async nextQuestion() {
            if (this.current >= QUIZ_SIZE) {
                this.state = 'done';
                this.submitResult();
                return;
            }
            this.selectedId = null;
            this.answered = false;
            this.isCorrect = false;
            var r = await fetch(cfg.questionUrl);
            this.currentQuestion = await r.json();
            this.currentQuestion.image_position = iPadDetect.getImagePos(this.currentQuestion);
        },

        selectAnswer(id) {
            if (this.answered) return;
            this.selectedId = id;
            this.answered = true;
            this.isCorrect = (id === this.currentQuestion.correct_id);
            if (this.isCorrect) {
                this.score++;
                Confetti.launch(document.querySelector('.quiz-img'));
            } else {
                Confetti.playWrongSound();
            }
            this.current++;
            this.playQuizAudio(this.currentQuestion);
        },

        playQuizAudio(q) {
            var audio = document.getElementById('quiz-audio');
            if (!audio || !q) return;

            var self = this;
            audio.pause();
            if (this._quizSeqId !== undefined) this._quizSeqId++;
            else this._quizSeqId = 0;
            var mySeqId = this._quizSeqId;

            function play(src) {
                if (!src) return;
                if (self._quizSeqId !== mySeqId) return;
                audio.src = src;
                audio.load();
                audio.play().catch(function (e) { console.log('Audio error:', e); });
            }

            if (!q.audio_zh) {
                if (q.audio_en) play(q.audio_en);
                return;
            }
            play(q.audio_zh);

            var probe = new Audio();
            var done = false;
            probe.src = q.audio_zh;
            probe.preload = 'metadata';
            function onReady() {
                if (done || self._quizSeqId !== mySeqId) return;
                done = true;
                var duration = probe.duration || 2;
                setTimeout(function () { play(q.audio_en); }, duration * 1000 + 500);
                probe.src = '';
            }
            probe.addEventListener('loadedmetadata', onReady);
            setTimeout(function () {
                if (!done && self._quizSeqId === mySeqId) onReady();
            }, 2000);
        },

        async submitResult() {
            await fetch(cfg.submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': cfg.csrfToken
                },
                body: JSON.stringify({
                    total: QUIZ_SIZE,
                    correct: this.score
                })
            });
        }
    };
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('main.container').classList.add('container-quiz');
});
