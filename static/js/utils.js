/* Shared utility functions */

/* Convert image_position to CSS object-position, defaulting to '50% 50%'. */
function centerPos(pos) {
    return pos || '50% 50%';
}

/* Resolve a relative media path to an absolute URL. */
function mediaUrl(path) {
    if (!path) return '';
    return path.startsWith('/') ? path : '/media/' + path;
}
