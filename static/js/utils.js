/* Shared utility functions — DEPRECATED (2026-07-31).
 *
 * 这两个函数在重构后已无调用方：
 *   - centerPos()   → 已由 ipad-detect.js 的 iPadDetect.centerPos() 取代
 *   - mediaUrl()    → 模板直接使用 Django {{ item.image.url }} 生成绝对路径
 *
 * 保留文件仅作兼容参考，待确认无外部引用后删除。
 */
function centerPos(pos) {
    return pos || '50% 50%';
}

function mediaUrl(path) {
    if (!path) return '';
    return path.startsWith('/') ? path : '/media/' + path;
}
