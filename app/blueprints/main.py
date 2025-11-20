from flask import Blueprint, render_template, request
from utilities.FolConvertion import FolConverterEn
from utilities.FolAnalyzer import FolAnalyzerEn
from googletrans import Translator
from utilities.LLMCall import call_yandex_neuro, call_gemma, call_giga
import re

converter = FolConverterEn()
analyzer = FolAnalyzerEn()
translator = Translator()

main_bp = Blueprint("main", __name__, template_folder="../templates")

@main_bp.route("/")
def home():
    return render_template(
        "home.html"
    )

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

    return render_template(
        "base_converter.html", 
        sentence=sentence, 
        fol_formula=fol_formula, 
        pattern=pattern
    )

@main_bp.route("/test/display", methods=["GET", "POST"])
def display():
    result = None

    if request.method == "POST":
        text = request.form.get("sentence")
        result = analyzer.analyze(text)

    return render_template(
        "display.html", 
        result=result
    )

def translate_fol_terms(fol_formula: str, target_lang: str) -> str:
    """
    Переводит только термы (слова) в формуле FOL обратно на исходный язык,
    сохраняя всю логическую структуру.
    """
    terms = set(re.findall(r"[A-Za-z]+", fol_formula))

    translation_map = {}

    for term in terms:
        translated = translator.translate(term, src="en", dest=target_lang).text
        translated = translated.replace(" ", "_")
        translation_map[term] = translated

    translated_formula = fol_formula
    for en_term, tr_term in translation_map.items():
        translated_formula = re.sub(rf"\b{en_term}\b", tr_term, translated_formula)

    return translated_formula

@main_bp.route("/test/trans_page", methods=["GET", "POST"])
def trans_page():
    fol_formula = None
    fol_formula_native = None
    sentence = None
    pattern = None
    detected_lang = None
    translated_sentence = None

    if request.method == "POST":
        sentence = request.form.get("sentence")
        if sentence:
            detection = translator.detect(sentence)
            detected_lang = detection.lang  # например "ru", "en", "de"
            if detected_lang != "en":
                translated_sentence = translator.translate(sentence, dest="en").text
            else:
                translated_sentence = sentence
            fol_formula = converter.convert_to_fol(translated_sentence)
            pattern = converter.get_pattern(translated_sentence)
            fol_formula_native = translate_fol_terms(fol_formula, detected_lang)

    return render_template(
        "trans_page.html",
        sentence=sentence,
        translated_sentence=translated_sentence,
        detected_lang=detected_lang,
        fol_formula=fol_formula,
        fol_formula_native=fol_formula_native,
        pattern=pattern,
    )
    return render_template("display.html", result=result)

@main_bp.route('/test/neuro', methods=['GET', 'POST'])
def predicate_form():
    sentence = None
    yandex_result = None
    giga_result = None
    gemma_result = None
    
    if request.method == 'POST':
        sentence = request.form.get('sentence')
        yandex_result = call_yandex_neuro(sentence)
        giga_result = call_giga(sentence)
        gemma_result = call_gemma(sentence)
    
    return render_template('neuro.html', 
                         sentence=sentence,
                         yandex_result=yandex_result,
                        giga_result = giga_result,
                         gemma_result=gemma_result)
