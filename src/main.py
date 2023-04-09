import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import json
import converter
import os
from dotenv import load_dotenv

FFMPEG_STATIC = "dependencies/ffmpeg"

load_dotenv()
API_KEY = os.environ['API_KEY']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = ApplicationBuilder().token(API_KEY).build()


lang = "Es-ES"

responses = {
    "Es-ES": {
        "start": "**Voz a texto**\n\nEnvía un mensaje de voz para que sea transcrito a texto\.\n\nActualmente, los archivos deben tener una duracion maxima de 20 segundos\.\n\nSi quieres cambiar el idioma, usa el comando /lang",
        "processing": "La transcripcion esta en proceso",
        "too_long": "El archivo es demasiado largo\. La duracion maxima es de 20 segundos",
        "error": "Ha ocurrido un error\. Por favor, intenta de nuevo mas tarde",
        "lang_change": "El idioma ha sido cambiado a Español",
        "lang_change_prompt": "Idiomas disponibles:\n\nTo change the language to english, send\n/lang EN\n\nPara cambiar el idioma a español, send\n /lang ES\n\n Для смены языка на русский, отправьте\n/lang RU\n\nPer cambiare lingua in italiano, invia\n /lang IT",
        "lang_change_error": "El idioma que ingresó no esta disponible"
    },
    "En-US": {
        "start": "**Voice to text**\n\nSend a voice message to be transcribed to text\.\n\nCurrently, files must have a maximum duration of 20 seconds\.\n\nIf you want to change the language, use the /lang command",
        "processing": "Transcription is in progress",
        "too_long": "The file is too long\. The maximum duration is 20 seconds",
        "error": "An error has occurred\. Please try again later",
        "lang_change": "The language has been changed to English",
        "lang_change_prompt": "Available languages:\n\nTo change the language to english, send\n/lang EN\n\nPara cambiar el idioma a español, send\n /lang ES\n\n Для смены языка на русский, отправьте\n/lang RU\n\nPer cambiare lingua in italiano, invia\n /lang IT",
        "lang_change_error": "The language you entered is not available"
    },
    "ru-RU": {
        "start": "**Голос в текст**\n\nОтправьте голосовое сообщение, чтобы оно было преобразовано в текст\.\n\nВ настоящее время файлы должны иметь максимальную продолжительность 20 секунд\.\n\nЕсли вы хотите изменить язык, используйте команду /lang",
        "processing": "Транскрипция в процессе",
        "too_long": "Файл слишком длинный\. Максимальная продолжительность 20 секунд",
        "error": "Произошла ошибка\. Пожалуйста, повторите попытку позже",
        "lang_change": "Язык изменен на русский",
        "lang_change_prompt": "Доступные языки:\n\nTo change the language to english, send\n/lang EN\n\nPara cambiar el idioma a español, send\n /lang ES\n\n Для смены языка на русский, отправьте\n/lang RU\n\nPer cambiare lingua in italiano, invia\n /lang IT",
        "lang_change_error": "Введенный язык недоступен"
    },
    "it-IT": {
        "start": "**Voce a testo**\n\nInvia un messaggio vocale da trascrivere in testo\.\n\nAttualmente, i file devono avere una durata massima di 20 secondi\.\n\nSe vuoi cambiare la lingua, usa il comando /lang",
        "processing": "La trascrizione è in corso",
        "too_long": "Il file è troppo lungo\. La durata massima è di 20 secondi",
        "error": "Si è verificato un errore\. Riprova più tardi",
        "lang_change": "La lingua è stata cambiata in italiano",
        "lang_change_prompt": "Lingue disponibili:\n\nTo change the language to english, send\n/lang EN\n\nPara cambiar el idioma a español, send\n /lang ES\n\n Для смены языка на русский, отправьте\n/lang RU\n\nPer cambiare lingua in italiano, invia\n /lang IT",
    }

}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = update.effective_user.language_code
    set_language(language)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]["start"], parse_mode='MarkdownV2')

async def get_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MAX_DURATION = 20
    if update.message.voice.duration > MAX_DURATION:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['too_long'])
        return
    new_file = await update.message.effective_attachment.get_file()
    await new_file.download_to_drive('tmp/audio.ogg')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['processing'])
    

    converter.ogg_to_wav('tmp/audio.ogg')
    text = converter.get_text_from_voice('tmp/converted.wav', language=lang)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Transcripcion:\n\n{text}")

    os.remove('tmp/audio.ogg')
    os.remove('tmp/converted.wav')

async def user_set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global lang
    set_lang_keyboard =['/lang EN', '/lang ES', '/lang RU', '/lang IT']

    if len(context.args) == 0:
        await update.message.reply_text( 
            responses[lang]['lang_change_prompt'], 
            reply_markup=ReplyKeyboardMarkup([set_lang_keyboard], one_time_keyboard=True, resize_keyboard=True)
            )
        return
    
    language = " ".join(context.args)
    if language == "EN":
        lang = "En-US"
    elif language == "ES":
        lang = "Es-ES"
    elif language == "RU":
        lang = "ru-RU"
    elif language == "IT":
        lang = "it-IT"
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['lang_change_error'])
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=responses[lang]['lang_change'])

def set_language(language):
    global lang
    if language == "en":
        lang = "En-US"
    elif language == "es":
        lang = "Es-ES"
    elif language == "ru":
        lang = "ru-RU"
    elif language == "it":
        lang = "it-IT"
    else:
        lang = "En-US"

def lambda_handler(event, context):
     return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    update_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), get_voice_message)
    application.add_handler(update_handler)

    language_handler = CommandHandler('lang', user_set_language)
    application.add_handler(language_handler)

    try:
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )
        return {
            'statusCode': 200,
            'body': "Success"
        }
    except Exception as exec:
        return {
            'statusCode': 500,
            'body': json.dumps(str(exec))
        }
