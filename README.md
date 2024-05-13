Локальное решение, для голосового помощника в рамках хакатона от МТС. 
Разработка происходила через IDE Pycharm. Голосовой помощник обращается к fastAPI для получения данных извне(иммитация внешнего API).


Instalation
------------    
Подтянуть библиотеки решения. В консоли: ``pip install -r requirements.txt``  

Запустить FASTapi. В консоли:``fastapi dev api.py``  

Сервер FASTapi работает локально, ``127.0.0.1:8000``

SwaggerUI ``127.0.0.1:8000/swaggerUI``. OpenAPI ``127.0.0.1:8000/openAPI``

Requirements
------------
* **Python** 3.8+ (required)
* **PyAudio** 0.2.11+ 
* **Speech_recognition** 3.10
* **Vosk**
* **Russian language model for vosk** folder model  

Examples
--------  
Авторизация в приложении происходит по номеру. Начальная команда - "Марвин привет" - описывает возможности голосового помощника и формат обращения.
Для начала работы с голосовым помощником, следует сказать: "Марвин" и название команды. Список доступных команд(commands.py):
* Перевод
* Баланс
* Пополнить
* Депозит

При вызове любой команды, кроме начальной, происходит авторизация пользователя по номеру телефона. Планируется осуществлять отправку кода.  

При вызове любой команды, кроме начальной, происходит авторизация пользователя по номеру телефона. Планируется осуществлять отправку кода.  

Мобильный телефон следует называть либо по цифрам, либо в обычном телефонном формате (8 800 535 35 35), либо по цифрам. 

Осуществляется проверка формата номера и правильность распознавания цифр.  

На текущем этапе, возможны не точности в распознавании разных форматов произношения мобильного телефона.  

\+ в начале не является обязательным.  
 
После авторизации, голосовой помощник готов к работе.   

Подвязка карты для осуществления операций производится через последние 4 цифры карты. Требуется называть именно цифры, не число.  

Команда баланс озвучивает количество денег на предварительно найденной и проверенной на наличие в банковской системе карте.  

Предполагается взаимодействие только с картами МТС банка, для распознавания и подвязки карт от других банков необходимо дополнительное обучение модели.  

Команда депозит позволяет изменить название вклада. Пользователю озвучиваются его вклады и предалагется выбрать тот из них, название которого необходимо изменить.  

Планируется добавление функции открытия, управления и закрытия вклада.  

Команда пополнить производит пополнение Мобильной связи и интернета. Планируется производит проверкусуществования введенного номера.  

Команда перевод позволяет перевести сумму, не превышающую количество денег на выбранной карте пользователя, по номеру карты или по телефону.   

Наличие пользователя с введенными данными проверяется в системе.   

При совершении операций, изменяющих баланс карты пользователя, сумма денег обновляется и при совершении операции баланс после операции перевод, пользователю будет озвучена меньшая сумма, чем была изначально.  

На данном этапе разработки команда "Выход отсутвует".  

В конце каждой команды, изменяющей баланс карты пользователя, происходит запрос подтвержения операции с возможной отменой.  

Каждый запрос от голосового ассистена является обязательным. Пропустить поле нельзя, пока не будет получена валидная информация, голсовой ассистент не озвучит следющую команду.  

Планируется улучшение алгоритма нахождения команды и работа с аргументами.  

На текущем этапе, для работы Марвину необходимо слышать четкую команду, без дополнительных слов.  

Голос Марвина - системный, так как используемая библиотека pyttsx3 требует предварительной установки голоса.   

Возможны трудности в распозвании текста в шумной обстановке или на отдаленном расстоянии от микрофона.  
