/**
 * language.js
 * -----------
 * Behavior for the Language Selection page (templates/language.html).
 *
 * Each language is a hidden radio input + a visible <label class="vs-lang-card">.
 * This script keeps the visual "selected" state of the cards in sync with the
 * underlying radio group, and enables the Next button only once a language
 * has been chosen.
 */

document.addEventListener("DOMContentLoaded", function () {
    const radios = document.querySelectorAll(".vs-lang-radio");
    const nextBtn = document.getElementById("vsLanguageNextBtn");
    const hint = document.getElementById("vsLanguageHint");

    if (!radios.length || !nextBtn) return;

    function refreshSelectedCard() {
        let selectedLabelText = null;

        radios.forEach((radio) => {
            const card = document.querySelector(`label[for="${radio.id}"]`);
            if (!card) return;

            if (radio.checked) {
                card.classList.add("vs-lang-card-selected");
                selectedLabelText = card.querySelector(".vs-lang-card-name").textContent;
            } else {
                card.classList.remove("vs-lang-card-selected");
            }
        });

        if (selectedLabelText) {
            nextBtn.removeAttribute("disabled");
            if (hint) {
                hint.innerHTML = `<i class="fa-solid fa-circle-check me-1" style="color:var(--vs-success);"></i> Selected: <strong>${selectedLabelText}</strong>`;
            }
        } else {
            nextBtn.setAttribute("disabled", "disabled");
            if (hint) {
                hint.innerHTML = `<i class="fa-solid fa-circle-info me-1"></i> No language selected yet`;
            }
        }
    }

    radios.forEach((radio) => {
        radio.addEventListener("change", refreshSelectedCard);
    });

    // Run once on load in case a language was already selected in a previous
    // session (server pre-checks the radio; this syncs the visual state + button).
    refreshSelectedCard();
});
