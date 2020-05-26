import requests
import pytz
from telegram import Bot, Update
from datetime import time, tzinfo, timezone, datetime
from telegram.ext import Updater, CommandHandler, Filters
from config import TG_TOKEN, PROXY, WEATHER_APP_ID, CITY

class User: 
  @staticmethod
  def get_username(user):      
      if user:
        name = user.first_name
      else:
        name = 'anonym'

      return name


class Weather:
  @staticmethod
  def get_weather():
      try:
        res = requests.get(
          "http://api.openweathermap.org/data/2.5/find",
          params={'q': CITY, 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_APP_ID}
        )
        data = res.json()

        item = data['list'][0]
        main = item['main']
        weather = item['weather'][0]
        weather_desc = weather['description']
        temp = main['temp']
        feels_like = main['feels_like']

        return {
          'desc': weather_desc,
          'temp': temp,
          'feels_like': feels_like
        }

      except Exception as e:
        print("Exception (find):", e)
        pass

def message_handler(bot: Bot, job):
    username = User().get_username(job.context['username'])
    weather = Weather().get_weather()

    desc = weather['desc']
    temp = round(weather['temp'])
    feels_like = round(weather['feels_like'])
    reply_text = f"*Привет {username}* 👋\n\nСейчас в Москве {desc} ⛅\nТемпература воздуха {temp}°C\nОщущается как {feels_like}°C\nХорошего дня 🙂"

    bot.send_message(
      chat_id = job.context['chat_id'],
      text = reply_text,
      parse_mode= "Markdown"
    )

def callback_timer(bot, update, job_queue):
    d = datetime.now()
    timezone = pytz.timezone("Europe/Moscow")
    d_aware = timezone.localize(d)
    context = {
      'chat_id': update.message.chat_id,
      'username': update.effective_user
    }
    notify_time = time(8, 30, 0, 0, tzinfo=d_aware.tzinfo)

    bot.send_message(chat_id=update.message.chat_id, text='Starting!')
    job_queue.run_daily(message_handler, notify_time, context=context)

def stop_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id, text='Stoped!')
    job_queue.stop()

def main():
    bot = Bot(
      token=TG_TOKEN,
      base_url=PROXY,
    )
    updater = Updater(
      bot=bot,
    )  
    updater.dispatcher.add_handler(CommandHandler('start', callback_timer, pass_job_queue=True))
    updater.dispatcher.add_handler(CommandHandler('stop', stop_timer, pass_job_queue=True))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
