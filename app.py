import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

from analysis import build_dashboard

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
SAMPLE_DATA_PATH = os.path.join(BASE_DIR, "data", "ecommerce_data.csv")
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.secret_key = "dev-secret-key-change-me"  # replace in production


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a CSV file first.")
        return redirect(url_for("index"))
    if not allowed_file(file.filename):
        flash("Only .csv files are supported.")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return redirect(url_for("dashboard", source="upload", filename=filename))


@app.route("/sample")
def use_sample():
    return redirect(url_for("dashboard", source="sample"))


@app.route("/dashboard")
def dashboard():
    source = request.args.get("source", "sample")
    if source == "upload":
        filename = request.args.get("filename")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    else:
        filepath = SAMPLE_DATA_PATH

    if not os.path.exists(filepath):
        flash("That file could not be found. Please try uploading again.")
        return redirect(url_for("index"))

    try:
        results = build_dashboard(filepath)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Something went wrong analyzing the file: {e}")
        return redirect(url_for("index"))

    return render_template(
        "dashboard.html",
        kpis=results["kpis"],
        charts=results["charts"],
        columns=results["columns"],
        row_count=results["row_count"],
        source_label="your uploaded file" if source == "upload" else "the sample dataset",
    )


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
