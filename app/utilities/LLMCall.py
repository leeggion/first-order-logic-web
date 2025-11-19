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

        print("Status:", getattr(response, 'status', 'Unknown'))
        print("Full response:", response)

        if hasattr(response, 'output') and hasattr(response.output, 'text'):
            print("Text:", response.output.text)
        elif hasattr(response, 'output_text'):
            print("Output text:", response.output_text)
        else:
            print("Available attributes:", [attr for attr in dir(response) if not attr.startswith('_')])
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
def call_gemma(sentence):
    pass
def call_giga(sentence):
    pass