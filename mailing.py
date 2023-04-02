from Token import BOT_TOKEN
import sqlite3
import music_functions_async
import asyncio
import yandex_music.exceptions
import os
import telegram.error
import schedule
import time


async def download_send_remove_track(tracks):
    # скачивает треки
    for track in tracks:
        track = track['track']
        got_file = False
        while not got_file:
            try:
                await music_functions_async.download(track,
                                                     folder='downloads/')
                got_file = True
            except (yandex_music.exceptions.TimedOutError, asyncio.exceptions.TimeoutError):
                continue

    # отправляет всем пользователям
    for chat_id in result:
        chat_id = chat_id[0]
        print(chat_id)
        if chat_id == 1850220173:
            await bot.send_message(chat_id=chat_id, text='···\n'
                                                         'Ежедневная рассылка новых песен в чартах')
            if tracks:
                for track in tracks:
                    file_sent = False
                    while not file_sent:
                        try:
                            await bot.send_document(
                                document=open(
                                    f'downloads/{await music_functions_async.get_name_for_file(track["track"])}',
                                    'rb'),
                                chat_id=chat_id,
                                caption=f'{(await music_functions_async.get_track_name(track["track"]))}\n'
                                        f'находится на {track["chart"]["position"]} месте чартов')
                            file_sent = True
                        except telegram.error.TimedOut:
                            continue
                await bot.send_message(chat_id=chat_id, text='Это список всех новых песен в списке чартов\n'
                                                             '···')
            else:
                await bot.send_message(chat_id=chat_id, text='Сегодня в чартах не появилось новых песен\n'
                                                             '···')

    # удаляет треки
    for track in tracks:
        track = track['track']
        os.remove(f'downloads/{await music_functions_async.get_name_for_file(track)}')
    return


def main():
    global bot, result
    # считывает id подписок из DB
    con = sqlite3.connect("db/database.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT chat_id FROM subscription""").fetchall()
    con.close()

    bot = telegram.Bot(token=BOT_TOKEN)
    tracks = (asyncio.run(music_functions_async.search_new_track_chart()))
    asyncio.run(download_send_remove_track(tracks))


schedule.every().day.at("13:00").do(main)

while True:
    schedule.run_pending()
    time.sleep(30)
