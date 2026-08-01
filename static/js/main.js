/**
 * main.js
 * --------
 * Shared, page-agnostic behavior loaded on every page via base.html.
 * Page-specific logic (language selection, analyze, history) lives in its
 * own file and is loaded only where needed.
 *
 * Responsibilities:
 *   1. Add a shadow/border to the navbar once the page is scrolled.
 *   2. Reveal `.vs-reveal` elements (fade + rise) as they enter the viewport,
 *      applying a staggered delay based on their position within a group.
 *   3. Auto-dismiss flash messages after a few seconds.
 */

document.addEventListener("DOMContentLoaded", function () {
    initNavbarScrollShadow();
    initScrollReveal();
    initFlashAutoDismiss();
});

/**
 * Adds `.vs-navbar-scrolled` to the navbar once the user scrolls past a small
 * threshold, giving it a subtle border/shadow instead of floating flat over
 * page content.
 */
function initNavbarScrollShadow() {
    const navbar = document.querySelector(".vs-navbar");
    if (!navbar) return;

    const SCROLL_THRESHOLD = 12;

    function updateNavbarState() {
        if (window.scrollY > SCROLL_THRESHOLD) {
            navbar.classList.add("vs-navbar-scrolled");
        } else {
            navbar.classList.remove("vs-navbar-scrolled");
        }
    }

    updateNavbarState();
    window.addEventListener("scroll", updateNavbarState, { passive: true });
}

/**
 * Uses IntersectionObserver to add `.vs-reveal-visible` to any `.vs-reveal`
 * element once it scrolls into view. Elements that share a parent with
 * `data-reveal-group` get a staggered delay class (`.vs-reveal-delay-N`)
 * based on their order, so groups of cards fade up in sequence rather than
 * all at once.
 */
function initScrollReveal() {
    const revealElements = document.querySelectorAll(".vs-reveal");
    if (!revealElements.length) return;

    // Assign stagger-delay classes per group (max 6 steps, then it repeats)
    const groups = {};
    revealElements.forEach((el) => {
        const groupKey = el.closest("[data-reveal-group]")
            ? el.closest("[data-reveal-group]").dataset.revealGroup
            : "default";
        groups[groupKey] = groups[groupKey] || 0;
        const indexInGroup = groups[groupKey] % 6;
        el.classList.add(`vs-reveal-delay-${indexInGroup + 1}`);
        groups[groupKey] += 1;
    });

    // Fallback for older browsers: just show everything immediately
    if (!("IntersectionObserver" in window)) {
        revealElements.forEach((el) => el.classList.add("vs-reveal-visible"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("vs-reveal-visible");
                    obs.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    revealElements.forEach((el) => observer.observe(el));
}

/**
 * Automatically fades out and removes Bootstrap flash alerts after a short
 * delay, so confirmation/warning messages don't linger indefinitely.
 */
function initFlashAutoDismiss() {
    const alerts = document.querySelectorAll(".vs-alert");
    if (!alerts.length) return;

    const AUTO_DISMISS_MS = 5000;

    alerts.forEach((alert) => {
        setTimeout(() => {
            // Use Bootstrap's own Alert API if it is available
            if (window.bootstrap && window.bootstrap.Alert) {
                const bsAlert = window.bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } else {
                alert.remove();
            }
        }, AUTO_DISMISS_MS);
    });
}
