from flask import Blueprint, render_template, request
from utilities.FolConvertion import FolConverterEn
from utilities.FolAnalyzer import FolAnalyzerEn
from deep_translator import GoogleTranslator
from utilities.LLMCall import call_yandex_neuro, call_gemma, call_giga, to_promt_1, ensemble
import re
import time

ERROR_MESSAGE = "[Ошибка] Не удалось определить тип предложения."
translator_en=GoogleTranslator(source="ru", target="en")
translator_ru=GoogleTranslator(source="en", target="ru")
converter = FolConverterEn()
analyzer = FolAnalyzerEn()
# translator = Translator()

main_bp = Blueprint("main", __name__, template_folder="../templates")

def run_resolution(premises, goal):
    # Здесь твой резолюционный движок
    # Возвращает (результат, шаги)

    derived = True
    steps = "Step 1: ...\nStep 2: ..."

    return ("ENTAILS" if derived else "NOT ENTAILS", steps)


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
    vars = ["x", "w", "y", "z", "k", "r1", "r2", "r3"]
    translation_map = {}
    for term in terms:
        if term in vars:
            translation_map[term] = term
            continue
        translated = translator_ru.translate(term)
        # translated = translator.translate(term, src="en", dest=target_lang).text
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
            translated_sentence = translator_en.translate(sentence)
            # detection = translator.detect(sentence)
            # detected_lang = detection.lang  # например "ru", "en", "de"
            # if detected_lang != "en":
            #     translated_sentence = translator.translate(sentence, dest="en").text
            # else:
            #     translated_sentence = sentence
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

@main_bp.route('/test/neuro', methods=['GET', 'POST'])
def predicate_form():
    sentence = None
    yandex_result = None
    giga_result = None
    gemma_result = None
    ensemble_result = None
    
    if request.method == 'POST':
        sentence = request.form.get('sentence')
        yandex_result = call_yandex_neuro(sentence, to_promt_1)
        giga_result = call_giga(sentence, to_promt_1)
        gemma_result = call_gemma(sentence, to_promt_1)
        time.sleep(1)
        ensemble_result = ensemble(sentence)
    
    return render_template('neuro.html', 
                         sentence=sentence,
                         yandex_result=yandex_result,
                        giga_result = giga_result,
                         gemma_result=gemma_result,
                         ensemble_result=ensemble_result
                         )

def get_fol_with_fallback(text: str, converter, llm_only: bool = False) -> str:
    if not text.strip():
        return ""
    
    if llm_only:
        try:
            fol_from_neuro = ensemble(text)
            return f"{fol_from_neuro.strip()}"
        except Exception as e:
            return f""
        
    fol_result = converter.convert_to_fol(text)
    if fol_result == ERROR_MESSAGE:
        try:
            fol_from_neuro = ensemble(text)
            return f"{fol_from_neuro.strip()}" 
        except Exception as e:
            return f""
        
    return fol_result

@main_bp.route("/test/resol", methods=["GET", "POST"])
def resolution_test():
    if request.method == "GET":
        return render_template("resolution.html")

    premises_raw = request.form.get("premises", "").strip().split("\n")
    goal_raw = request.form.get("goal", "").strip()
    use_llm_only = request.form.get("use_llm_only") == "true"
    
    fol_premises = [get_fol_with_fallback(p, converter, use_llm_only) for p in premises_raw if p.strip()]
    fol_goal = get_fol_with_fallback(goal_raw, converter, use_llm_only)
    
    has_error = any("[Ошибка]" in fol for fol in fol_premises) or "[Ошибка]" in fol_goal

    if has_error:
        result = "FAILURE: Невозможно запустить резолюцию из-за ошибок в конвертации одной или нескольких формул."
        steps = []
    else:
        result, steps = run_resolution(fol_premises, fol_goal)

    return render_template("resolution.html",
                           premises="\n".join(premises_raw),
                           goal=goal_raw,
                           fol_premises=fol_premises,
                           fol_goal=fol_goal,
                           result=result,
                           resolution_steps=steps,
                           use_llm_only=use_llm_only)
    
@main_bp.app_template_filter("highlight_fol")
def highlight_fol_filter(text: str):
    if not text:
        return ""
    text = re.sub(r"(∀|∃)", r'<span class="quantifier">\1</span>', text)
    text = re.sub(r"\b([xyzkw])\b", r'<span class="var">\1</span>', text)
    text = re.sub(r"\b([A-Z][a-zA-Z0-9_]*)\s*\(",
                  r'<span class="predicate">\1</span>(', text)
    text = re.sub(r"(¬)", r'<span class="neg">\1</span>', text)
    return text
