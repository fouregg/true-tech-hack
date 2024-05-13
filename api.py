import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Union

users = {
    "Kirill": {
        "phone": '+78005553535',
        "cards": {
            "card_1": {
                "card_number": '5487345623450234',
                "balance": "5000"
            },
            "card_2": {
                "card_number": '1234567898765678',
                "balance": "1000"
            }
        },
        "deposits": {
            "deposit_1": {
                "deposit_name": "премиум",
                "balance": "",
            },
            "deposit_2": {
                "deposit_name": "стандарт",
                "balance": "",
            }
        }
    },
    "Irina": {
        "phone": '+78005554545',
        "cards": {
            "card_1": {
                "card_number": '3456865412349012',
                "balance": "50000"},
        }
    }
}


def run_FASTAPI():
    uvicorn.run(app, host="127.0.0.1", port=8000)


app = FastAPI(docs_url="/swaggerUI", redoc_url="/openAPI")


@app.get("/login")
def login(userphone: Union[str, None] = None):
    """
    Конечная точка FastAPI для получения имени пользователя с заданным номером телефона
    :param userphone: номер телефона, который отправил пользователь
    :return: если пользователь с таким телефоном существует,имя пользователя с этим номером телефона;
    В противном случае, Exception
    """
    username = None
    for key in users:
        if (users[key]["phone"]) == userphone.replace(" ", "+"):
            username = key
            break
    if username is not None:
        return {"username": username, "phone": userphone}
    raise HTTPException(status_code=404, detail=f"User with telephone number: {userphone} not found")


@app.get("/card")
def get_cards(username: Union[str, None] = None, card: Union[str, None] = None):
    """
    Конечная точка FastAPI для проверки наличия карты с таким номером у пользователя
    :param card: номер карты
    :param username: имя пользователя
    :return: True, если карта с таким номером существует у пользователя;
    в противном случае, Exception
    """
    card_numbers = [card["card_number"] for user in users.values() for card in user["cards"].values()]
    if card in card_numbers:
        return True
    else:
        raise HTTPException(status_code=404, detail=f"User with username: {username} not found")


@app.get("/balance")
def get_balance(username: Union[str, None] = None, card: Union[str, None] = None):
    """
    Конечная точка FastAPI для получения баланса с карты пользователя
    :param username: имя пользователя
    :param card: последние 4 цифры номера карты
    :return: возвращает последние 4 цифры номера карты и количество денег на ней
    """
    if users[username] is not None:
        cards = users[username]["cards"]
        for el in cards.values():
            print(el)
            if el["card_number"][-4:] == card:
                return {"card": card, "balance": el["balance"]}
        raise HTTPException(status_code=404, detail=f"User with username: {username} haven't card {card}")
    raise HTTPException(status_code=404, detail=f"User with username: {username} not found")


@app.get("/alldeposits")
def deposit(username: Union[str, None] = None):
    """
    Конечная точка FastAPI для получения всех вкладов пользователя
    :param username: имя пользователя
    :return: если пользовател существует и у пользователя есть вклады, список всех вкладов пользователя4
    В противном случае, Exception
    """
    if users[username] is not None:
        deposits = users[username]["deposits"]
        if users[username]["deposits"] is not None:
            arr = list()
            for el in deposits.values():
                arr.append(el["deposit_name"])
            return arr
        return {"deposit_name": ""}
    else:
        raise HTTPException(status_code=404, detail=f"User with username: {username} not found")



@app.get("/allcards")
def allcards(username: Union[str, None] = None):
    """
    Конечная точка FastAPI для получения всех карт пользователя
    :param username: имя пользователя
    :return: если пользователь существует, список всех карт пользователя;
    В противном случае, Exception
    """
    if users[username] is not None:
        cards = users[username]["cards"]
        if users[username]["cards"] is not None:
            arr = list()
            for el in cards.values():
                arr.append(el["card_number"])
            return arr
        return
    else:
        raise HTTPException(status_code=404, detail=f"User with username: {username} not found")


@app.get("/deposit")
def deposit(username: Union[str, None] = None, olddepositname: Union[str, None] = None,
            newdepositname: Union[str, None] = None):
    """
    Конечная точка FastAPI для смены названия существующего вклада пользователя
    :param newdepositname: новое название вклада
    :param olddepositname: текущее название, которое должно быть изменено
    :param username: имя пользователя
    :return: Если пользовтаель и вклад с текущем названием существуют, измененное название вклада;
    В противном случае, Exception
    """
    if users[username] is not None:
        deposit_key = next(
            (key for key, value in users[username]['deposits'].items() if value["deposit_name"] == olddepositname),
            None)
        if deposit_key is not None:
            users[username]['deposits'][deposit_key]["deposit_name"] = newdepositname
            return {"deposit_name": newdepositname}
        raise HTTPException(404, detail=f"User with username: {username} haven't deposit {olddepositname}")
    raise HTTPException(status_code=404, detail=f"User with username: {username} not found")


@app.get("/pay")
def pay_service(username: Union[str, None] = None, card: Union[str, None] = None, phone: Union[str, None] = None,
                amount: Union[str, None] = None):
    """
   Конечная точка FastAPI endpoint для осуществления платежей
    :param phone: номер телефона, за который необходимо заплатить
    :param amount: сумма, которая будет оплачена
    :param username: имя пользователя
    :param card: номер карты, с которой совершается оплата
    :return: если пользователь и карта с таким номреом сущесвуют и сумма не больше баланса карты, карта и ее обновленный баланс
    В противном случае, Exception
    """
    if users[username] is not None:
        card_key = next((key for key, value in users[username]['cards'].items() if value["card_number"] == card), None)

        if card_key is not None:
            if int(users[username]['cards'][card_key]["balance"]) >= int(amount):
                users[username]['cards'][card_key]["balance"] = str(
                    int(users[username]['cards'][card_key]["balance"]) - int(amount))
                return {"card": card, "balance": users[username]['cards'][card_key]["balance"]}
            raise HTTPException(404, detail=f"Insufficient funds")
        raise HTTPException(404, detail=f"User with username: {username} haven't card {card}")
    raise HTTPException(status_code=404, detail=f"User with username: {username} not found")


@app.get("/send")
def send(username: Union[str, None] = None, fromcard: Union[str, None] = None, tophone: Union[str, None] = None,
         tocard: Union[str, None] = None,
         amount: Union[str, None] = None):
    """
    Конечная точка FastAPI для перевода денег от пользователю другому пользователю
    :param username: имя пользователя - отправителя
    :param fromcard: номер карты, с которой совершается перевод
    :param tophone: номер телефона получателя
    :param tocard: номер карты получателя
    :param amount: сумма перевода
    :return: если пользователь-отправитель существует, если карта получателя существует, номер карты получателя и ее обновленный баланс,
    В противном случае, Exception
    """
    if users[username] is not None:
        card_key = None
        for key in users:
            if tocard is not None:
                for k in users[key]["cards"]:
                    if (users[key]["cards"][k]["card_number"]) == tocard:
                        card_key = k
                        to_user = key
                        break
            elif tophone is not None:
                if (users[key]["phone"]) == tophone.replace(" ", "+"):
                    card_key = "card_1"
                    to_user = key
                    break
        fromcard = next((key for key, value in users[username]['cards'].items() if value["card_number"] == fromcard),
                        None)
        if card_key is not None:
            if int(users[username]['cards'][fromcard]["balance"]) >= int(amount):
                users[username]['cards'][fromcard]["balance"] = str(
                    int(users[username]['cards'][fromcard]["balance"]) - int(amount))
                users[to_user]['cards'][card_key]["balance"] = str(
                    int(users[to_user]['cards'][card_key]["balance"]) + int(amount))
                return {"card": fromcard, "balance": users[username]['cards'][fromcard]["balance"]}
            return {"card": fromcard, "balance": users[username]['cards'][fromcard]["balance"]}
        raise HTTPException(404, detail=f"User with username: {username} haven't card {fromcard}")
    raise HTTPException(status_code=404, detail=f"User with username: {username} not found")
