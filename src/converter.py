from pydub import AudioSegment
import speech_recognition as sr


def ogg_to_wav(file_path):
    v_message = AudioSegment.from_ogg(file_path)
    v_message.export(f"converted.wav", format="wav")
    return

def get_text_from_voice(file_path, language="es-ES"):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        data = r.record(source)
    text = r.recognize_google(data, language=language)

    return text