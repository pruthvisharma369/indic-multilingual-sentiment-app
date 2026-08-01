/**
 * analyze.js
 * ----------
 * Behavior for the Text Analysis page (templates/analyze.html).
 *
 * Responsibilities:
 *   1. Live character counter with a warning state near the limit.
 *   2. "Try a sample" button that fills in a demo sentence per language.
 *   3. Clear button.
 *   4. Analyze button: shows the loading overlay, calls POST /api/analyze,
 *      and redirects to /result/<id> on success (or shows an inline error).
 */

document.addEventListener("DOMContentLoaded", function () {
    const textArea = document.getElementById("vsTextArea");
    const languageSelect = document.getElementById("vsLanguageSelect");
    const charCounter = document.getElementById("vsCharCounter");
    const clearBtn = document.getElementById("vsClearBtn");
    const sampleBtn = document.getElementById("vsSampleBtn");
    const analyzeBtn = document.getElementById("vsAnalyzeBtn");
    const loadingOverlay = document.getElementById("vsLoadingOverlay");
    const errorBox = document.getElementById("vsAnalyzeError");
    const errorText = document.getElementById("vsAnalyzeErrorText");

    if (!textArea || !analyzeBtn) return;

    const MAX_LENGTH = 1000;
    const WARNING_THRESHOLD = 900;

    // One representative sample sentence per supported language, used only
    // to help demo the app quickly — not related to the ML model itself.
    const SAMPLE_TEXT = {
        hindi: "यह फिल्म वाकई शानदार थी, मुझे बहुत पसंद आई!",
        english: "This product completely exceeded my expectations, I love it!",
        gujarati: "આ સેવા ખૂબ જ નિરાશાજનક હતી.",
        marathi: "हा अनुभव खूपच छान होता, धन्यवाद!",
        bengali: "এই পরিষেবাটি সত্যিই হতাশাজনক ছিল।",
        tamil: "இந்த உணவகம் மிகவும் நன்றாக இருந்தது!",
        telugu: "ఈ సేవ చాలా నిరాశపరిచింది.",
        kannada: "ಈ ಚಿತ್ರ ನಿಜಕ್ಕೂ ಅದ್ಭುತವಾಗಿತ್ತು!",
        malayalam: "ഈ അനുഭവം വളരെ മോശമായിരുന്നു.",
        punjabi: "ਇਹ ਸੇਵਾ ਬਹੁਤ ਵਧੀਆ ਸੀ, ਧੰਨਵਾਦ!",
        assamese: "এই অভিজ্ঞতা যথেষ্ট হতাশাজনক আছিল।",
        odia: "ଏହି ସେବା ସତରେ ଚମତ୍କାର ଥିଲା!",
    };

    /** Updates the character counter text/color based on current input length. */
    function updateCharCounter() {
        const length = textArea.value.length;
        charCounter.textContent = `${length} / ${MAX_LENGTH} characters`;
        charCounter.classList.toggle("vs-char-counter-limit", length >= WARNING_THRESHOLD);
    }

    /** Hides the inline error alert, if visible. */
    function hideError() {
        if (errorBox) errorBox.classList.add("d-none");
    }

    /** Shows the inline error alert with a given message. */
    function showError(message) {
        if (!errorBox || !errorText) return;
        errorText.textContent = message;
        errorBox.classList.remove("d-none");
    }

    /** Toggles the full-screen loading overlay and disables the action buttons. */
    function setLoadingState(isLoading) {
        if (loadingOverlay) {
            loadingOverlay.classList.toggle("vs-loading-active", isLoading);
        }
        analyzeBtn.disabled = isLoading;
        if (clearBtn) clearBtn.disabled = isLoading;
    }

    // --- Character counter -------------------------------------------------
    textArea.addEventListener("input", updateCharCounter);
    updateCharCounter();

    // --- Clear button --------------------------------------------------------
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            textArea.value = "";
            updateCharCounter();
            hideError();
            textArea.focus();
        });
    }

    // --- Sample text button --------------------------------------------------
    if (sampleBtn) {
        sampleBtn.addEventListener("click", function () {
            const selectedLanguage = languageSelect ? languageSelect.value : "hindi";
            textArea.value = SAMPLE_TEXT[selectedLanguage] || SAMPLE_TEXT.english;
            updateCharCounter();
            hideError();
            textArea.focus();
        });
    }

    // --- Analyze button: call the prediction API -----------------------------
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async function () {
            const text = textArea.value.trim();
            const language = languageSelect ? languageSelect.value : "";

            hideError();

            if (!text) {
                showError("Please enter some text before analyzing.");
                textArea.focus();
                return;
            }

            setLoadingState(true);

            try {
                const response = await fetch("/api/analyze", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, language }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "The server could not process this request.");
                }

                // Success — send the user to the server-rendered result page.
                window.location.href = `/result/${data.id}`;
            } catch (err) {
                setLoadingState(false);
                showError(err.message || "Something went wrong while analyzing your text. Please try again.");
            }
        });
    }
});
