"""
app.py
------
Main Flask application for "Indian Multilingual Sentiment Analysis using IndicBERT".

This file ONLY handles the web layer (routing, request/response, DB persistence,
rendering). The actual ML prediction logic lives in model/predictor.py, which
wraps the user's existing, untouched `predict_sentiment(text, language)` function.

Run with:
    python app.py
"""

import csv
import io
import json
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
    Response,
)

from model.predictor import predict_sentiment
from database.db_setup import (
    init_db,
    insert_prediction,
    get_record_by_id,
    get_history,
    count_history,
    delete_record,
    get_all_records_for_export,
)

# --------------------------------------------------------------------------
# App configuration
# --------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "replace-this-with-a-real-secret-key-in-production"  # TODO: move to env var

# List of languages supported by the UI (must match keys your model understands)
SUPPORTED_LANGUAGES = [
    {"code": "hindi", "label": "Hindi", "native": "हिन्दी"},
    {"code": "english", "label": "English", "native": "English"},
    {"code": "gujarati", "label": "Gujarati", "native": "ગુજરાતી"},
    {"code": "marathi", "label": "Marathi", "native": "मराठी"},
    {"code": "bengali", "label": "Bengali", "native": "বাংলা"},
    {"code": "tamil", "label": "Tamil", "native": "தமிழ்"},
    {"code": "telugu", "label": "Telugu", "native": "తెలుగు"},
    {"code": "kannada", "label": "Kannada", "native": "ಕನ್ನಡ"},
    {"code": "malayalam", "label": "Malayalam", "native": "മലയാളം"},
    {"code": "punjabi", "label": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    {"code": "assamese", "label": "Assamese", "native": "অসমীয়া"},
    {"code": "odia", "label": "Odia", "native": "ଓଡ଼ିଆ"},
]

PER_PAGE = 8  # records per page on the History page

# Make supported languages available in every template without passing manually
@app.context_processor
def inject_globals():
    return {"supported_languages": SUPPORTED_LANGUAGES, "current_year": datetime.now().year}


# --------------------------------------------------------------------------
# Page routes
# --------------------------------------------------------------------------

@app.route("/")
def home():
    """Landing page: hero, project intro, features, supported languages."""
    return render_template("home.html")


@app.route("/language", methods=["GET", "POST"])
def language():
    """Language selection page. Stores the chosen language in the session
    and forwards the user to the Analyze page."""
    if request.method == "POST":
        selected = request.form.get("language")
        valid_codes = [lang["code"] for lang in SUPPORTED_LANGUAGES]

        if not selected or selected not in valid_codes:
            flash("Please select a valid language before continuing.", "warning")
            return redirect(url_for("language"))

        session["selected_language"] = selected
        return redirect(url_for("analyze"))

    return render_template("language.html")


@app.route("/analyze")
def analyze():
    """Text analysis page: language dropdown + textarea + Analyze button.
    Actual analysis happens client-side via a fetch() call to /api/analyze."""
    preselected_language = session.get("selected_language", "hindi")
    return render_template("analyze.html", preselected_language=preselected_language)


@app.route("/result/<int:record_id>")
def result(record_id):
    """Displays the result for a previously stored prediction (by DB id).
    Rendering by id (rather than passing data through the URL/session) keeps
    the result page refresh-safe and shareable."""
    record = get_record_by_id(record_id)

    if record is None:
        flash("That result could not be found. It may have been deleted.", "danger")
        return redirect(url_for("analyze"))

    probabilities = json.loads(record["probabilities"])

    return render_template("result.html", record=record, probabilities=probabilities)


@app.route("/history")
def history():
    """Prediction history page with search, language filter, and pagination."""
    search_query = request.args.get("q", "").strip()
    language_filter = request.args.get("language", "").strip()
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1

    total_records = count_history(search_query, language_filter)
    total_pages = max(1, (total_records + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages)

    records = get_history(search_query, language_filter, page, PER_PAGE)

    return render_template(
        "history.html",
        records=records,
        search_query=search_query,
        language_filter=language_filter,
        page=page,
        total_pages=total_pages,
        total_records=total_records,
    )


@app.route("/history/delete/<int:record_id>", methods=["POST"])
def history_delete(record_id):
    """Deletes a single history record and returns to the History page."""
    delete_record(record_id)
    flash("Record deleted successfully.", "success")

    # Preserve any active search/filter/page state on redirect
    return redirect(
        url_for(
            "history",
            q=request.form.get("q", ""),
            language=request.form.get("language", ""),
            page=request.form.get("page", 1),
        )
    )


@app.route("/history/export")
def history_export():
    """Exports the (optionally filtered) history as a downloadable CSV file."""
    search_query = request.args.get("q", "").strip()
    language_filter = request.args.get("language", "").strip()

    rows = get_all_records_for_export(search_query, language_filter)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Text", "Language", "Prediction", "Confidence", "Created At"])

    for row in rows:
        writer.writerow(
            [row["id"], row["text"], row["language"], row["prediction"], row["confidence"], row["created_at"]]
        )

    csv_data = buffer.getvalue()
    buffer.close()

    filename = f"sentiment_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/about")
def about():
    """About page: IndicBERT explanation, workflow, tech stack."""
    return render_template("about.html")


# --------------------------------------------------------------------------
# API route
# --------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    JSON API used by analyze.html (via fetch) to run a prediction.

    Expects JSON body: { "text": "...", "language": "hindi" }
    Returns JSON body: {
        "id": 12,
        "prediction": "Positive",
        "confidence": 0.98,
        "probabilities": {"Positive": 0.98, "Negative": 0.02},
        "text": "...",
        "language": "hindi"
    }
    """
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    language = (data.get("language") or "").strip()

    valid_codes = [lang["code"] for lang in SUPPORTED_LANGUAGES]

    if not text:
        return jsonify({"error": "Please enter some text to analyze."}), 400
    if language not in valid_codes:
        return jsonify({"error": "Please select a supported language."}), 400

    try:
        # --- This is the ONLY call into the user's existing ML code ---
        result_data = predict_sentiment(text, language)
        # ----------------------------------------------------------------

        prediction = result_data["prediction"]
        confidence = float(result_data["confidence"])
        probabilities = result_data["probabilities"]

    except Exception as exc:  # pragma: no cover - surfaced to the client
        return jsonify({"error": f"Prediction failed: {str(exc)}"}), 500

    record_id = insert_prediction(
        text=text,
        language=language,
        prediction=prediction,
        confidence=confidence,
        probabilities=json.dumps(probabilities),
    )

    return jsonify(
        {
            "id": record_id,
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "text": text,
            "language": language,
        }
    )


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()  # Creates database/history.db and the predictions table if missing
    app.run(debug=True)
