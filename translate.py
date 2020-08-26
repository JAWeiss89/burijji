from google.cloud import translate_v2 as translate

translate_client = translate.Client()

def translate(text, target_language):
    """ target language can be en for english, """
    # text = text.decode('utf-8')

    output = translate_client.translate(text, target_language=target_language)
    translation = output['translatedText']

    return translation


 