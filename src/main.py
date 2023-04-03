import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import json
import converter
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ['API_KEY']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

lang = "Es-ES"

responses = {
    "Es-ES": {
        "start": "**Voz a texto**\n\nEnvía un mensaje de voz para que sea transcrito a texto\.\n\nActualmente, los archivos deben tener una duracion maxima de 20 segundos\.\n\nSi quieres cambiar el idioma, usa el comando /lang",
        "processing": "La transcripcion esta en proceso",
        "too_long": "El archivo es demasiado largo\. La duracion maxima es de 20 segundos",
        "error": "Ha ocurrido un error\. Por favor, intenta de nuevo mas tarde",
        "lang_change": "El idioma ha sido cambiado a Español",
        "lang_change_prompt": "Escribe el idioma al que quieres cambiar.\n\nIdiomas disponibles:\n\n/lang *English* - En-US\n/lang *Español* - Es-ES",
        "lang_change_error": "El idioma que ingresó no esta disponible"
    },
    "En-US": {
        "start": "**Voice to text**\n\nSend a voice message to be transcribed to text\.\n\nCurrently, files must have a maximum duration of 20 seconds\.\n\nIf you want to change the language, use the /lang command",
        "processing": "Transcription is in progress",
        "too_long": "The file is too long\. The maximum duration is 20 seconds",
        "error": "An error has occurred\. Please try again later",
        "lang_change": "The language has been changed to English",
        "lang_change_prompt": "Write the language you want to change to\.\n\nAvailable languages:\n\n/lang *English* - En-US\n/lang *Español* - Es-ES",
        "lang_change_error": "The language you entered is not available"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]["start"], parse_mode='MarkdownV2')

async def get_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MAX_DURATION = 20
    if update.message.voice.duration > MAX_DURATION:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['too_long'])
        return
    new_file = await update.message.effective_attachment.get_file()
    await new_file.download_to_drive('audio.ogg')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['processing'])
    

    converter.ogg_to_wav('audio.ogg')
    text = converter.get_text_from_voice('converted.wav')

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Transcripcion:\n\n {text}")

    os.remove('audio.ogg')
    os.remove('converted.wav')

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global lang
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['lang_change_prompt'])
        return
    language = " ".join(context.args)
    if language == "English":
        lang = "En-US"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['lang_change'])
    elif language == "Español":
        lang = "Es-ES"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['lang_change'])


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    update_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), get_voice_message)
    application.add_handler(update_handler)

    language_handler = CommandHandler('lang', set_language)
    application.add_handler(language_handler)

    application.run_polling()