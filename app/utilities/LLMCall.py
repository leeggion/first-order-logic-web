import openai
import os
from dotenv import load_dotenv

def to_promt_1(sentence):
    return f"""
        CONVERT THIS SENTENCE TO FIRST-ORDER PREDICATE LOGIC (FOL). OUTPUT ONLY THE FORMULA.
        Sentence: "{sentence}"
        Rules
        Use: ∀ (universal), ∃ (existential), →, ∧, ∨, ¬.
        Use descriptive lowercase predicates: man(x), loves(x,y), smart(x).
        Variables: x, y, z…
        Use parentheses to show quantifier scope.
        Output must be only one final FOL formula (no explanations, no comments).
        Determiners
        “every”, “all” → ∀x (A(x) → …)
        “some”, “a”, “at least one” → ∃x (A(x) ∧ …)
        “no” → ∀x (A(x) → ¬(...))
        “exactly one” → ∃x (A(x) ∧ ∀y (A(y) → y=x))
        Structure rules
        Noun phrases introduce predicates: student(x), dog(x).
        Adjectives are unary predicates: smart(x), young(x).
        Verbs are relations: loves(x,y), barks(x).
        Relative clauses → conjunction: student(x) ∧ studies(x).
        Proper names may be constants: john, mary.
        Scope & ambiguity
        Prefer surface quantifier order unless strongly unnatural.
        Subject quantifier usually takes widest scope.
        Do not ask clarifying questions; choose the most standard reading.
        Examples
        "Every man loves a woman" → ∀x (man(x) → ∃y (woman(y) ∧ loves(x,y)))
        "Some students are smart" → ∃x (student(x) ∧ smart(x))
        "No dog barks" → ∀x (dog(x) → ¬barks(x))
        "All students who study pass" → ∀x ((student(x) ∧ studies(x)) → pass(x))
        Now convert: "{sentence}"
            """
    
def to_promt_2(sentence, var_1, var_2, var_3):
    return f"""
        You are a senior logic expert. Your task is to analyze, compare, and synthesize multiple FOL translations into one definitive, most correct version.

        Original Statement:
        "{sentence}"

        Proposed FOL Translations:
        1. Assistant 1: {var_1}
        2. Assistant 2: {var_2} 
        3. Assistant 3: {var_3}

        Analysis & Synthesis Task:

        COMPARE the variants on these dimensions:
        - Quantifier scope & order - Which captures the natural language semantics best?
        - Predicate consistency - Are predicates descriptive and uniformly formatted?
        - Logical completeness - Is anything missing or superfluous?
        - Structural accuracy - Proper handling of determiners, modifiers, relations.
        - Parenthesization - Correct scope boundaries.

        SYNTHESIZE the optimal formula by:
        - Selecting the most logically accurate version as base
        - Incorporating strengths from other variants
        - Correcting any identified errors
        - Ensuring maximal clarity and conciseness

        Output Format:
        ONLY the final, synthesized FOL formula. No explanations, no commentary.
            """
def call_yandex_neuro(sentence, to_promt, temp = 0.3):
    load_dotenv()
    YANDEX_CLOUD_FOLDER=os.getenv("YANDEX_CLOUD_FOLDER")
    YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_MODEL = "yandexgpt/rc"
    if(type(sentence) == list):
        prompt = to_promt(sentence[0], sentence[1], sentence[2], sentence[3])
    else:
        prompt = to_promt(sentence)


    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )

    try:
        response = client.responses.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
            temperature=temp,
            input=prompt,
            max_output_tokens=500
        )

        if hasattr(response, 'output') and hasattr(response.output, 'text'):
            return (response.output.text)
        elif hasattr(response, 'output_text'):
            return (response.output_text)
        else:
            return ("Available attributes:", [attr for attr in dir(response) if not attr.startswith('_')])
    except Exception as e:
        return (f"Error: {e}")
def call_gemma(sentence, to_promt, temp = 0.3):
    load_dotenv()
    YANDEX_CLOUD_FOLDER=os.getenv("YANDEX_CLOUD_FOLDER")
    YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_MODEL = "gemma-3-27b-it/latest"
    prompt = to_promt(sentence)
    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )

    try:
        response = client.responses.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
            temperature=temp,
            input=prompt,
            max_output_tokens=500
        )

        if hasattr(response, 'output') and hasattr(response.output, 'text'):
            return (response.output.text)
        elif hasattr(response, 'output_text'):
            return (response.output_text)
        else:
            return ("Available attributes:", [attr for attr in dir(response) if not attr.startswith('_')])
    except Exception as e:
        return (f"Error: {e}") 
def call_giga(sentence, to_promt, temp = 0.0):
    load_dotenv()
    prompt = to_promt(sentence)
    client_id = os.getenv("GIGA_CLIENT_ID")
    client_secret = os.getenv("GIGA_CLIENT_SECRET")
    from gigachat import GigaChat
    import base64

    credentials = f"{client_id}:{client_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    from gigachat import GigaChat
    if(temp == 0):
        giga = GigaChat(credentials=f'{base64_credentials}', model='GigaChat-2', verify_ssl_certs=False)
    else:
        giga = GigaChat(credentials=f'{base64_credentials}', model='GigaChat-2',temperature=temp, verify_ssl_certs=False)
    response = giga.chat(prompt)
    return(response.choices[0].message.content)

def ensemble(sentence):
    var_1  = call_yandex_neuro(sentence, to_promt_1, 1.2)
    var_2 = call_gemma(sentence,to_promt_1, 1.2)
    var_3 = call_giga(sentence,to_promt_1, 1.2)
    final = call_yandex_neuro([sentence, var_1, var_2, var_3],to_promt_2, 0.2)
    return final