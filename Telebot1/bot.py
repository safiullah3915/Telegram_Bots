from config import *
import telebot
import openai

chatStr = ''

def ChatModel(prompt):
    global chatStr
    openai.api_key = OPENAI_KEY
    chatStr += f"Safi: {prompt}\nBanana-Bot: "
    response = openai.completions.create(
        model = "gpt-3.5-turbo",
        prompt=chatStr,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    chatStr += f"{response['choice'][0]['text']}"
    return response['choice'][0]['text']

bot = telebot.TeleBot(BOT_API) #(token=BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello Welcome to Our Bot")

@bot.message_handler()
def chat(message):
     try:
         reply = ChatModel(message.text)
         bot.reply_to(message, reply)
     except Exception as e:
         print(e)
         bot.reply_to(message, e)


print("Bot Started: ")
bot.polling()


