from flask import Blueprint, render_template, request
from utilities.FolConvertion import FolConverterEn
from utilities.FolAnalyzer import FolAnalyzerEn
converter = FolConverterEn()
analyzer = FolAnalyzerEn()

main_bp = Blueprint("main", __name__, template_folder="../templates")

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/test/base_converter", methods=["GET", "POST"])
def index():
    fol_formula = None
    sentence = None
    pattern=None
    
    if request.method == "POST":
        sentence = request.form.get("sentence")
        if sentence:
            fol_formula = converter.convert_to_fol(sentence)
            pattern = converter.get_pattern(sentence)

    return render_template("base_converter.html", sentence=sentence, fol_formula=fol_formula, pattern=pattern)

@main_bp.route("/test/display", methods=["GET", "POST"])
def display():
    result = None

    if request.method == "POST":
        text = request.form.get("sentence")
        result = analyzer.analyze(text)

    return render_template("display.html", result=result)
