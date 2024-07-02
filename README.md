# Python Telegram Tamagotchi Bot
> Бот, який реплікує гру тамагочі.

Бот використовує бібліотеку pyTelegramBotAPI для роботи з телеграм, pickle для зберігання об'єктів пайтон міже сессіями.


## Installing / Getting started

```shell
git clone https://github.com/yaroslav-demchenko/python-tamagotchi-telegram-bot.git
cd python-tamagotchi-telegram-bot
python3 -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
Enter your telegram api key to config.py
python bot.py run
```

### Ideas for improvement
продумати економіку, додати більше міні-ігр, товарів, речей в магазин. 
Створити різні типи яєць і різних тварин. Розробити систему грейдів для тварин.
Додати можливість обмінюватися ітемами між користувачами, влаштувати змагання між користувачами. 
Додати рейтинг користувачів.
