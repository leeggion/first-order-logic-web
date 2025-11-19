import openai

def call_yandex_neuro(sentence):

    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )

    try:
        response = client.responses.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
            temperature=0.3,
            input=sentence,
            max_output_tokens=500
        )

        # return ("Status:", getattr(response, 'status', 'Unknown'))
        # return ("Full response:", response)

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
    pass
def call_giga(sentence):
    pass