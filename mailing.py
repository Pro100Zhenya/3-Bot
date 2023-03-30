import requests
from Token import BOT_TOKEN
import sqlite3


con = sqlite3.connect("Bot_database.db")
cur = con.cursor()
result = cur.execute(f"""SELECT chat_id FROM subscription""").fetchall()
con.close()
TOKEN = BOT_TOKEN
message = 'Тебе еще нужно какие-то тесты сегодня решать?'
for chat_id in result:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id[0]}&text={message}"
    print(requests.get(url).json())
