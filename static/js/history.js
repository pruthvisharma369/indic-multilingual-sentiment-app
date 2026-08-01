/**
 * history.js
 * ----------
 * Behavior for the History page (templates/history.html).
 *
 * The page's core functionality (search, filter, pagination, delete, export)
 * all works via plain GET/POST forms server-side, so it degrades gracefully
 * without JavaScript. This file only adds small usability touches on top:
 *
 *   1. Auto-submit the filter form when the language dropdown changes,
 *      so the user doesn't have to also click "Apply".
 *   2. A gentle fade-in for the results table/empty-state on load.
 */

document.addEventListener("DOMContentLoaded", function () {
    initAutoSubmitLanguageFilter();
    initTableFadeIn();
});

/**
 * Automatically submits the search/filter form as soon as the language
 * dropdown changes, since choosing a language is a clear, deliberate action
 * (unlike typing in the search box, which should wait for the Apply button
 * or Enter key so it doesn't reload on every keystroke).
 */
function initAutoSubmitLanguageFilter() {
    const languageFilter = document.getElementById("vsLanguageFilter");
    if (!languageFilter) return;

    languageFilter.addEventListener("change", function () {
        languageFilter.form.submit();
    });
}

/**
 * Applies a subtle fade-in to the table (or empty state) so the page doesn't
 * feel like a static reload every time a search/filter/pagination link is
 * followed.
 */
function initTableFadeIn() {
    const table = document.querySelector(".table-responsive");
    const emptyState = document.querySelector(".vs-empty-state");
    const target = table || emptyState;

    if (target) {
        target.classList.add("vs-fade-in");
    }
}
