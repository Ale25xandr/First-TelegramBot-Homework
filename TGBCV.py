import requests
from bs4 import BeautifulSoup
import telebot

Token = '5610801813:AAG0j29OvQ2wCwKD3qNMnkZuBZOrJTj3OMc'
bot = telebot.TeleBot(Token)

keys = {'доллар': 'USD',
        "евро": "EUR",
        'рубль': 'RUB'}


class ConverterExceptionUser(Exception):
    pass


class ConverterExceptionServer(Exception):
    pass


@bot.message_handler(commands=['start', 'help'])
def welcome(message: telebot.types.Message):
    text = "Привет! Чтобы начать работу с ботом, " \
           "введите запрос в следующем формате: " \
           "<валюта, из которой хотите перевести>, " \
           "<валюта, в которую хотите перевести>, " \
           "<количество первой валюты>" \
           "\n" \
           "\nСписок доступных валют: \n/values"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['values'])
def welcome(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for k in keys.keys():
        text = '\n'.join((text, k))
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def send_welcome(message):
    if message.content_type == 'text':
        value = message.text.split(" ")
        try:
            if len(value) != 3:
                raise ConverterExceptionUser
        except ConverterExceptionUser:
            bot.send_message(message.chat.id, 'Введите 3 параметра!')
            return

        currency_1, currency_2, amount = value

        try:
            if not currency_1.isalpha() or not currency_2.isalpha():
                raise ConverterExceptionUser
        except ConverterExceptionUser:
            bot.send_message(message.chat.id, 'Неверный формат запроса!')
            return

        try:
            if float(amount.replace(",", ".")) < 0:
                raise ConverterExceptionUser
        except ConverterExceptionUser:
            bot.send_message(message.chat.id, 'Сумма не может быть отрицательной!')
            return
        except ValueError:
            bot.send_message(message.chat.id, 'Неверно введена сумма!')
            return

        try:
            if currency_1.lower() not in keys.keys():
                raise ConverterExceptionUser
        except ConverterExceptionUser:
            bot.send_message(message.chat.id, f'Валюта {currency_1} не поддерживается!')
            return

        try:
            if currency_2.lower() not in keys.keys():
                raise ConverterExceptionUser
        except ConverterExceptionUser:
            bot.send_message(message.chat.id, f'Валюта {currency_2} не поддерживается!')
            return

        try:
            if currency_1.lower() == currency_2.lower():
                raise ConverterExceptionUser
        except ConverterExceptionUser:
            bot.send_message(message.chat.id, 'Валюты одинаковы!')
            return

        r = requests.get(f'https://www.x-rates.com/calculator/?from={keys[currency_1.lower()]}'
                         f'&to={keys[currency_2.lower()]}&amount={amount}')

        try:
            if 400 <= r.status_code <= 599:
                raise ConverterExceptionServer
        except ConverterExceptionServer:
            bot.send_message(message.chat.id, "Ошибка сервера. Повторите попытку позже.")
            return

        soup = BeautifulSoup(r.text, 'lxml')

        s = soup.find_all('span', {'class': "ccOutputRslt"})

        s_1 = s[0].text.split(" ")

        bot.send_message(message.chat.id, f'{amount} {currency_1.lower()} в '
                                          f'{currency_2.lower()} = {round(float(s_1[0]),2)} {keys[currency_2.lower()]}')
    else:
        bot.send_message(message.chat.id, 'Введите запрос')


bot.polling(none_stop=True)
