import openai
import os
from dotenv import load_dotenv

def call_yandex_neuro(sentence):
    load_dotenv()
    YANDEX_CLOUD_FOLDER=os.getenv("YANDEX_CLOUD_FOLDER")
    YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_MODEL = "yandexgpt/rc"

    prompt = f"""
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


    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )

    try:
        response = client.responses.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
            temperature=0.3,
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
        return (f"Error type: {type(e)}")
def call_gemma(sentence):
    load_dotenv()
    YANDEX_CLOUD_FOLDER=os.getenv("YANDEX_CLOUD_FOLDER")
    YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_MODEL = "gemma-3-27b-it/latest"
    prompt = f"""
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
    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )

    try:
        response = client.responses.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
            temperature=0.3,
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
        return (f"Error type: {type(e)}")
def call_giga(sentence):
    load_dotenv()
    prompt = f"""
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
    client_id = os.getenv("GIGA_CLIENT_ID")
    client_secret = os.getenv("GIGA_CLIENT_SECRET")
    from gigachat import GigaChat
    import base64

    credentials = f"{client_id}:{client_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    from gigachat import GigaChat
    giga = GigaChat(credentials=f'{base64_credentials}', model='GigaChat-2', verify_ssl_certs=False)
    response = giga.chat(prompt)
    return(response.choices[0].message.content)