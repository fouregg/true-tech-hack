import main

dict_commands = {
    "intents":
        {
            "имя": ('марвин'),
            "перевод":
                {
                    "responses": main.send
                },
            "баланс":
                {
                    "responses": main.balance
                },
            "депозит":
                {
                    "responses": main.rename_deposite
                },
            "пополнить":
                {
                    "responses": main.pay_service
                },
            "login":
                {
                    "responses": main.login
                }
        }
}
