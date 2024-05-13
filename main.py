"""Base logic for Voice Assistance"""
import json
import re
import time

import requests
import speech_recognition
import pyttsx3
from ru_word2number import w2n
from CustomRecognizer import CustomRecognizer
import Levenshtein
import commands


def start():
    """
    Функция для входа в голосового помощника
    :return если запрос пользователя - существующая команда, программа перенаправляет его на эту команду,
    В случае команды "привет марвин", программа сообщает о всех возможных действиях пользователя,
    в противном случае, просит повторить
    """
    global default_user
    if "привет марвин" in recognizer.background_listener_text:
        tell_function(textDescriptionFunction)
    elif commands.dict_commands['intents']["имя"] in recognizer.background_listener_text:
        cmd = recognize_cmd(recognizer.background_listener_text, commands.dict_commands['intents'].keys())
        if cmd['cmd'] == "":
            start()
        else:
            try:
                if default_user is not None:
                    commands.dict_commands['intents'][cmd['cmd']]["responses"]()
                else:
                    default_user = commands.dict_commands['intents']['login']["responses"]()
                    start()
            except TypeError:
                tell_function('Команда не найдена, попробуйте еще раз')
                start()


def login():
    '''
    Функция для авторизации
    программа запрашивает у пользователя номер телефона, чтобы войти,
    :return если это реальный пользователь, она запоминает логин пользователя и дает доступ к данным,
    в противном случае, говорит об ошибке и просит повторить
    '''
    global BASE_URL
    global default_user
    user_authorized = False
    first = False
    while not user_authorized:
        if not first:
            first = True
            tell_function("Команды доступны только для авторизированных пользователей.")
        phone = convert_telephone_number(check_length("Скажите номер телефона чтобы войти в профиль"))
        if phone == "":
            continue
        response = requests.get(BASE_URL + "login?userphone=" + str(phone))
        if response.status_code == 200:
            user_authorized = True
            default_user = json.loads(response.text)["username"]
            tell_function(f"Здравствуйте {default_user}, Вы вошли в свой профиль. Скажите Марвин и название команды.")
            return default_user
        else:
            tell_function("Пользователь с таким номером телефона не обнаружен, попробуйте ещё раз")


def balance():
    """
    Функция для проверки баланса
    спрашивает, какую баланс какой карты пользователь хочет проверить
    :return информация о балансе карты пользователя,
    в случае ошибки говорит об этом
    """
    global default_user
    global BASE_URL
    card = choose_card()
    if card is not None:
        response = requests.get(BASE_URL + "balance?username=" + default_user + "&card=" + card)
        if response.status_code == 200:
            amount = json.loads(response.text)["balance"]
            tell_function(f"Баланс вашей карты {card} составляет {amount}")
        else:
            tell_function("Карта не обнаружена")
            balance()


def rename_deposite():
    """
    Функция для переименования существующего вклада
    спрашивает пользователя о текущем названии вклада и просит дать новое
    :return результат операции: успешно(навзание вклада изменено),или "Вклад не найден" и повторяет функцию
    """
    response = requests.get(
        BASE_URL + "alldeposits?username=" + default_user)
    if response.status_code == 200:
        deposit_name = json.loads(response.text)
        deposits = " или ".join("".join(el) for el in deposit_name)
        reci = check_length("Скажите название какого вклада вы хотите изменить ." + deposits)
        topic = recognize_cmd(reci, deposit_name)['cmd']
        new_name = check_length("Скажите новое название ")
        conf_bool = conf("Поменять название вклада" + topic + " на " + new_name)
        if conf_bool:
            response = requests.get(
                BASE_URL + "deposit?username=" + default_user + "&olddepositname=" + topic + "&newdepositname=" + new_name)
            if response.status_code == 200:
                tell_function(f"Операция выполнена")
                start()
            else:
                tell_function("Вклад не обнаружен")
                rename_deposite()
        else:
            start()
    else:
        tell_function("У вас нет вкладов")
        start()


def is_telephone_number(number):
    """
    Функция для проверки соответствия телефонных номеров стандарту
    :param number: номер телефона был взят из def convert_telephone_number
    :return Если число соответствует стандарту, она возвращает значение True, в противном случае, она возвращает значение False
    """
    r = re.compile(
        r'^((\+7|\+8)[-.\s]??(9[1-79]{2}|80[0-9])[-.\s]??\d{3}[-.\s]??\d{4}|\(\+7|\+8\)\s*(9[0-79]{2}|80[0-9])['
        r'-.\s]??\d{3}[-.\s]??\d{4}|\+7[-.\s]??(9[0-79]{2}|80[0-9])[-.\s]??\d{4})$')
    if r.search(number):
        return True
    else:
        return False


def convert_telephone_number(rec):
    """
    Функция преобразования словесного представления телефонного номера в цифровое представление
    :param rec: текст, записанный с микро
    :return возвращает числовое представление телефонного номера, который был записан. Если числовое значение не
    расшифровывается или не соответствует стандарту телефонных номеров, возвращает пустую строку
    """
    while True:
        rec = list(rec.split())
        converted_rec = list()

        if len(rec) > 0 and rec[0] == "плюс":
            rec.remove("плюс")

        cur_digit = -1
        prev_digit = -1
        try:
            while rec:
                    tmp = w2n.word_to_num(rec.pop(0))
                    if len(converted_rec) == 0 and (tmp == 7 or tmp == 8):
                        converted_rec.append("+7")
                    else:
                        if tmp // 100 > 0:
                            cur_digit = 3
                        elif tmp // 10 > 1:
                            cur_digit = 2
                        elif tmp // 10 <= 1 and tmp != 0:
                            cur_digit = 1
                        else:
                            cur_digit = 0
                        if cur_digit < prev_digit and tmp != 0:
                            converted_rec[len(converted_rec) - 1] += tmp
                        else:
                            converted_rec.append(tmp)
                        if tmp // 100 > 0 and len(rec) <= 4:
                            prev_digit = 2
                        else:
                            prev_digit = cur_digit
        except ValueError:
            tell_function("Цифры не были распознаны, пожалуйста, повторите")
            rec = check_length("")
            continue

        converted_rec = "".join(str(el) for el in converted_rec)
        if is_telephone_number(converted_rec):
            return converted_rec
        else:
            tell_function("Номер телефона не существует, пожалуйста, введите другой номер телефона")
            rec = check_length("")


def send():
    """
    Функция для перевода денег
    Сначала клиент делает выбор: по номеру карты или по номеру телефона,
    затем запрашивает информацию для перевода: номер карты и сумму
    : return выполняет перевод и информирует пользователя об успешном завершении операции. В случае провала,
     информирует пользователя о неправильных введенных данных или ошибке.
    """
    response = requests.get(
        BASE_URL + "allcards?username=" + default_user)
    if response.status_code == 200:
        cards = json.loads(response.text)
        cards_last_numbers = list(el[-4:] for el in cards)
        card_names = " или ".join(" ".join(el) for el in cards_last_numbers)
        from_card = check_length("Выберите номер карты, с которой хотите перевести " + card_names, 4)
        if from_card in cards_last_numbers:
            from_card = cards[cards_last_numbers.index(from_card)]
            dis = {"cmd": ["карта", "номер телефона"]}
            reci = check_length("Выберите, через что вы хотите осуществить перевод: " + str(dis['cmd']))
            topic = recognize_cmd(reci, dis['cmd'])
            if 'карта' in topic['cmd']:
                card_num = check_length("Скажите номер карты цифрами ", 16)
                response = requests.get(
                    BASE_URL + "card?username=" + default_user + "&card=" + card_num)
                if response.status_code == 200:
                    card_sum = check_length("Скажите cумму ", -1)
                    conf_bool = conf("Перевести" + card_sum + " на карту" + card_num)
                    if conf_bool:
                        response = requests.get(
                            BASE_URL + "send?username=" + default_user + "&fromcard=" + from_card + "&tocard=" + card_num + "&amount=" + card_sum)
                        if response.status_code == 200:
                            tell_function("Операция выполнена")
                            start()
                        else:
                            resp = check_length(
                                "Не достаточно средств на карте. Хотите попробовать с другой картой? ")
                            if "да" in resp:
                                send()
                            else:
                                tell_function("Операция отменена")
                                start()
                    else:
                        start()
                else:
                    resp = check_length("Карта с таким номером не обнаружена. Хотите попробовать еще раз? ")
                    if "нет" in resp:
                        tell_function(f"Операция отменена")
                        start()
                    else:
                        send()
            elif 'номер' in topic['cmd']:
                rec_tel = convert_telephone_number(check_length("Скажите номер телефона "))
                response = requests.get(
                    BASE_URL + "login?userphone=" + rec_tel)
                if response.status_code == 200:
                    card_sum = (check_length("Скажите сумму ", -1))
                    conf_bool = conf("Перевести" + card_sum + " по номеру" + ' '.join(list(rec_tel[1:])))
                    if conf_bool:
                        response = requests.get(
                            BASE_URL + "send?username=" + default_user + "&fromcard=" + from_card + "&tophone=" + rec_tel + "&amount=" + card_sum)
                        if response.status_code == 200:
                            tell_function("Операция выполнена")
                            start()
                        else:
                            tell_function("Операция отклонена")
                            send()
                    else:
                        start()
                else:
                    tell_function("Карта не обнаружена")
                    send()


def pay_service():
    """
    Функция для осуществления платежей
    запрашиваетcя, какой объект должен быть оплачен, данные о получателе и сумме, а затем уточняет, уверен ли пользовтель
    :return выполняет операцию, если все правильно, сообщает об успехе, в противном случае, об ошибке
    """
    response = requests.get(
        BASE_URL + "allcards?username=" + default_user)
    if response.status_code == 200:
        cards = json.loads(response.text)
        cards_last_numbers = list(el[-4:] for el in cards)
        card_names = " или ".join(" ".join(el) for el in cards_last_numbers)
        from_card = check_length("Выберите номер карты для оплаты " + card_names, 4)
        if from_card in cards_last_numbers:
            from_card = cards[cards_last_numbers.index(from_card)]
            dis = {'cmd': {'связь и интернет'}}
            reci = check_length("Выберите то, что хотите оплатить " + str(dis['cmd']))
            topic = recognize_cmd(reci, dis['cmd'])
            phone = convert_telephone_number(check_length("Скажите номер телефона "))
            amount = check_length("Скажите сумму ", -1)
            conf_bool = conf(
                "Пополнить" + topic['cmd'] + " номер телефона" + ' '.join(list(phone[1:])) + " на сумму" + amount)
            if conf_bool:
                response = requests.get(
                    BASE_URL + "pay?username=" + default_user + "&card=" + from_card + "&phone=" + phone + "&amount=" + amount)
                if response.status_code == 200:
                    tell_function(f"Операция выполнена")
                else:
                    resp = check_length("Недостаточно средств. Хотите попробовать с пополнить с другой карты?")
                    if "да" in resp:
                        pay_service()
                    else:
                        tell_function("Операция отменена")
                        start()
            else:
                start()


def recognize_cmd(cmd, com):
    """
    Функция для разбиения команды и параметров запроса и сопоставление их существующим командам
    :param
    cmd: распознанная фраза;
    com: список команд, где мы ищем
    :return k: команда, которая найдена по фразе пользователя
    """
    k = {'cmd': "", 'percent': 0}
    if 'марвин' in cmd:
        cmd = cmd.replace('марвин', '')
    if cmd.count(" ") == 0:
        flag = True
    else:
        flag = False
        cmd = cmd.replace(" ", "")
    match_list = {}
    for key in com:
        if key.count(" ") != 0:
                key = key.replace(" ", "")
        concat_name = ''.join(key.split()).lower()
        match_list[key] = Levenshtein.jaro_winkler(cmd, concat_name) / len(key.split())
    k['cmd'] = max(match_list.items(), key=lambda x: x[1])[0]
    return k


def callback(recognizer, audio):
    """
    Функция для фонового прослушивания
    :params
    recognizer: средство распознавания данных (CustomRecognizer());
    audio: поток, который мы распознаем
    :return результат, который можно распознать из фона с помощью vosk_recognizer
    """
    recognized_data = recognizer.recognize_vosk(audio, language="rus")
    return json.loads(recognized_data)["text"]


def tell_function(what):
    """
    Функция для синтеза текста голосом
    :param
    what (str): текст, синтезированный в речь
    """
    tts.say(what)
    tts.runAndWait()
    tts.stop()


def convert_to_numbers(rec):
    """
    Функция для преобразования словесного представления числа в числовое представление
    :param rec: текст, записанный из микрофона
    :return цифровое представление числа, которое было записано
    Если числовое представление не расшифровано, возвращает пустую строку
    """
    s = list(rec.split())
    new_rec = list()
    for i in s:
        try:
            new_rec.append(w2n.word_to_num(i))
        except ValueError:
            tell_function("Цифры не были распознаны, пожалуйста повторите")
            return ""
    new_rec = "".join(str(el) for el in new_rec)
    return new_rec


def choose_card():
    """
    Функция распознавания карты авторизованного пользователя
    """
    rec = check_length("Скажите последние 4 цифры карты ", 4)
    return rec


def check_length(tell, length=0):
    """
    Функция проверки длины параметров
    :param length: длина, которая должна быть, (по умолчанию - 0)
    :param tell: что сказала программа
    :return если все верно - param; в противном случае, говорит об ошибке
    """
    while True:
        tell_function(tell)
        par = vosk_listen_recognize(5)
        if length == -1:
            par = count_sum(par.split())
            if par != "":
                return par
        if length != 0:
            par = convert_to_numbers(par)
            if len(par) == length:
                return par

        elif len(par) != 0:
            return par


def count_sum(numbers):
    """
    Функция для определения суммы
    :param numbers: слова пользователя
    :return "нормальная" (для программы) числовая строка.
    Если числовое представление не расшифровано, возвращает пустую строку
    """
    num = 0
    prev = None
    for i in numbers:
        try:
            tmp = w2n.word_to_num(i)
            if tmp > 999:
                num = num - num % 1000 + num % 1000 * tmp
            else:
                num += tmp
        except ValueError:
            tell_function("Цифры не были распознаны, пожалуйста повторите")
            return ""
    return str(num)


def conf(tell):
    """
    Функция для проверки уверенности пользователя в выборе
    спрашивает, уверен ли пользователь или нет
    :param tell: фраза, которую скажет программа
    :return True, если ответ 'да'; в противном случае, False
    """
    ans = check_length(tell + ". Скажите пожалуйста. Да или Нет")
    if "да" in ans:
        tell_function("выполняю команду" + tell)
        return True
    elif "нет" in ans:
        tell_function("Операция отменена")
        return False


def vosk_listen_recognize(time_listen):
    """
    Функция для прослушивания в основном потоке micro
    :param time_listen: сколько секунд мы должны слушать micro
    :return: распознанный текст
    :except: Exception, если vosk не может распознать звук
    """
    global microphone
    global recognizer
    with microphone as source:
        try:
            audio = recognizer.listen(source, time_listen)
        except:
            return ""
    try:
        recognize_text = json.loads(recognizer.recognize_vosk(audio))["text"]
    except speech_recognition.UnknownValueError:
        raise Exception("Vosk not understand what you say")
    return recognize_text


microphone = speech_recognition.Microphone()
recognizer = CustomRecognizer()
tts = pyttsx3.init()
default_user = None
BASE_URL = "http://127.0.0.1:8000/"
if __name__ == "__main__":
    textDescriptionFunction = """
    Вас приветствует голосовой помощник Марвин. Голосовому помощнику доступны следующие команды: 
    команда перевод, для перевода денег по номеру карты,или номеру телефона.
    команда баланс, для проверки баланса.
    команда пополнить для пополнения телефона.
    команда депозит, для изменения названия вклада.
    Скажите,Марвин и название команды для начала работы.
    """
    rate = tts.getProperty('rate')
    tts.setProperty('rate', rate - 40)
    voices = tts.getProperty('voices')
    tts.setProperty('voice', 'ru')
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
    stop_listen = recognizer.listen_in_background(source, callback, phrase_time_limit=5)
    for voice in voices:
        if voice.name == 'Vsevolod':
            tts.setProperty('voice', voice.id)
    print("Init complete. Let's talk")
    while True:
        start()
        time.sleep(2)
