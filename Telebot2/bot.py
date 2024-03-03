import telebot
from PIL import Image
import io
from config import *

bot = telebot.TeleBot(BOT_API)  # Note the capital 'B' in 'TeleBot' based on pyTelegramBotAPI's convention.

# This dictionary will store the format the user wants to convert the image to.
user_requests = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hi, Welcome to the Image Converter Bot.\nPlease upload an image to convert.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the current user's image to a buffer.
    user_requests[chat_id] = {
        'image': io.BytesIO(downloaded_file)
    }

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='PNG', callback_data='convert_png'))
    markup.add(telebot.types.InlineKeyboardButton(text='JPEG', callback_data='convert_jpeg'))
    markup.add(telebot.types.InlineKeyboardButton(text='GIF', callback_data='convert_gif'))
    markup.add(telebot.types.InlineKeyboardButton(text='BMP', callback_data='convert_bmp'))
    
    bot.send_message(chat_id, "Please choose the format you want to convert to:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    chat_id = call.message.chat.id
    user_data = user_requests.get(chat_id)
    if not user_data or 'image' not in user_data:
        bot.answer_callback_query(call.id, "Something went wrong. Please try uploading the image again.")
        return

    image_io = user_data['image']
    image_io.seek(0)  # Go to the start of the StringIO buffer
    image = Image.open(image_io)

    # Determine the correct format based on user selection.
    format_to_convert = call.data.split('_')[-1].upper()
    if format_to_convert == 'JPG':
        format_to_convert = 'JPEG'

    # Save the converted image to a BytesIO buffer.
    output = io.BytesIO()
    image.save(output, format=format_to_convert)
    output.seek(0)

    # Prepare a filename that includes the desired format.
    filename = f"converted_image.{format_to_convert.lower()}"

    print(f"The file name: {filename}")

    # Instead of sending as photo, send as a document to bypass Telegram's auto-conversion.
    bot.send_document(chat_id, (filename, output), caption=f"Here is your image in {format_to_convert} format.")
    bot.answer_callback_query(call.id, f"Image converted to {format_to_convert}.")


if __name__ == '__main__':
    print("Bot Started: ")
    bot.polling()
