import requests
import pytz
from telegram import Bot, Update
from datetime import date, time, tzinfo, timezone, datetime
from telegram.ext import Updater, CommandHandler, Filters
from config import TG_TOKEN, PROXY, WEATHER_APP_ID, CITY


def filter_by_time(item):
  datenow = datetime.date(datetime.now())
  begin = "{datenow} 12:00".format(datenow=datenow)
  end = "{datenow} 15:00".format(datenow=datenow)
  dateBegin = datetime.strptime(begin, "%Y-%m-%d %H:%M")
  dateEnd = datetime.strptime(end, "%Y-%m-%d %H:%M")  
  itemDate = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")

  if itemDate == dateBegin or itemDate == dateEnd:
    return 1 
  else:
    return 0

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

  @staticmethod
  def get_avg_weather():
      try:
        res = requests.get(
          "http://api.openweathermap.org/data/2.5/forecast",
          params={'q': CITY, 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_APP_ID}
        )
        data = res.json()

        listOfTimes = list(filter(filter_by_time, data['list']))
        firstTime = listOfTimes[0]['main']['temp']
        secondTime = listOfTimes[1]['main']['temp']

        avg_temp = round((firstTime + secondTime) / 2)

        return avg_temp

      except Exception as e:
        print("Exception (find):", e)
        pass

class Rates:
  @staticmethod
  def get_all_rates(currency="EUR"):
    try:
      res = requests.get(
        "https://api.exchangeratesapi.io/latest",
        params={'base': currency}
      )

      data = res.json()
      return data['rates']
    except Exception as e:
      print("Exception (find):", e)
      pass

  @staticmethod
  def get_rate(fromCurrency = "EUR", toCurrency = "RUB"):
    rates = Rates().get_all_rates(currency=fromCurrency)

    return rates[toCurrency]

def message_handler(bot: Bot, job):
    username = User().get_username(job.context['username'])
    weather = Weather().get_weather()
    day_temp = Weather().get_avg_weather()

    rates = {
      "USD": round(Rates().get_rate(fromCurrency="USD", toCurrency="RUB")),
      "EUR": round(Rates().get_rate(fromCurrency="EUR", toCurrency="RUB"))
    }

    desc = weather['desc']
    temp = round(weather['temp'])
    feels_like = round(weather['feels_like'])
    reply_text = f"*Привет {username}* 👋\n\nСейчас в Москве {desc} ⛅\nТемпература воздуха {temp}°C\nОщущается как {feels_like}°C\nДнем будет {day_temp}°C\n\n🇺🇸 ${rates['USD']} RUB \n🇪🇺 €{rates['EUR']} RUB\n\nХорошего дня 🙂"

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

    bot.send_message(chat_id=update.message.chat_id, text='Starting!')
    job_queue.run_daily(message_handler, days=(0, 1, 2, 3, 4, 5, 6),time = time(hour = 9, minute = 0, second = 0, tzinfo=d_aware.tzinfo), context=context)

def stop_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id, text='Stoped!')
    job_queue.stop()

def main():
    bot = Bot(
      token=TG_TOKEN,
      base_url=PROXY
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
