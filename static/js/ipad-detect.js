/**
 * iPad / device position detection.
 * Returns the correct image object-position based on screen size and orientation.
 *
 * Usage:
 *   var pos = iPadDetect.getImagePos(item);
 *   img.style.objectPosition = iPadDetect.centerPos(pos);
 */
(function() {
    window.iPadDetect = {
        /**
         * Returns object-position for the current device.
         * @param {Object} item - Must have image_position, image_position_ipad_portrait,
         *                        image_position_ipad_landscape properties.
         * @returns {string} CSS object-position value.
         */
        getImagePos: function(item) {
            if (screen.width >= 768) {
                return (window.innerWidth > window.innerHeight)
                    ? (item.image_position_ipad_landscape || '50% 50%')
                    : (item.image_position_ipad_portrait || '50% 50%');
            }
            return item.image_position || '50% 50%';
        },

        /**
         * Adjust vertical position upward for card mode.
         * Animal faces are typically in the upper portion of images.
         * @param {string} pos - CSS object-position string like "50% 50%".
         * @param {number} [bias=0.65] - Vertical bias factor (0.65 = shift up 35%).
         * @returns {string}
         */
        centerPos: function(pos, bias) {
            bias = (bias !== undefined) ? bias : 0.65;
            if (!pos || pos === '50% 50%') return '50% ' + Math.round(bias * 100) + '%';
            var parts = pos.split(' ');
            var x = parts[0];
            var yPct = parseInt(parts[1]) || 50;
            var adjustedY = Math.max(5, Math.round(yPct * bias));
            return x + ' ' + adjustedY + '%';
        }
    };
})();
