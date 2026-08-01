/**
 * result.js
 * ---------
 * Behavior for the Result page (templates/result.html).
 *
 * Progress bars are rendered server-side at width: 0 (class
 * `.vs-progress-bar-animated`, defined in animations.css) with their real
 * value stored in `data-target-width`. This script sets the real width
 * shortly after paint so the CSS `transition` on `.vs-progress-bar` actually
 * animates the fill-in, instead of appearing instantly at full width.
 */

document.addEventListener("DOMContentLoaded", function () {
    const bars = document.querySelectorAll(".vs-progress-bar[data-target-width]");
    if (!bars.length) return;

    // Small delay ensures the browser has painted the 0-width state first,
    // so the transition to the target width is actually visible.
    requestAnimationFrame(function () {
        setTimeout(function () {
            bars.forEach((bar) => {
                const target = bar.dataset.targetWidth || "0";
                bar.style.width = `${target}%`;
            });
        }, 150);
    });
});
