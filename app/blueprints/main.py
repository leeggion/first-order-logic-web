from flask import Blueprint, render_template, request
from app.utilities.FolConvertion import FolConverterEn

main_bp = Blueprint("main", __name__, template_folder="../templates")

converter = FolConverterEn()

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/test/base_converter", methods=["GET", "POST"])
def index():
    fol_formula = None
    sentence = None

    if request.method == "POST":
        sentence = request.form.get("sentence")
        if sentence:
            fol_formula = converter.convert_to_fol(sentence)

    return render_template("base_converter.html", sentence=sentence, fol_formula=fol_formula)
