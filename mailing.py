from Token import BOT_TOKEN
import music_functions_async
import asyncio
import yandex_music.exceptions
import os
import telegram.error
import schedule
import time

from data import db_session

db_session.global_init("db/database.db")


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
    for chat_id in id_subscription:
        await bot.send_message(chat_id=chat_id, text='···\n'
                                                     'Ежедневная рассылка изменений в чартах')
        if tracks:
            for track in tracks:
                file_sent = False
                while not file_sent:
                    try:
                        if tracks[0]['chart']['progress'] == 'new':
                            await bot.send_document(
                                document=open(
                                    f'downloads/{await music_functions_async.get_name_for_file(track["track"])}',
                                    'rb'),
                                chat_id=chat_id,
                                caption=f'{(await music_functions_async.get_track_name(track["track"]))}\n'
                                        f'находится на {track["chart"]["position"]} месте чартов')
                        else:
                            await bot.send_document(
                                document=open(
                                    f'downloads/{await music_functions_async.get_name_for_file(track["track"])}',
                                    'rb'),
                                chat_id=chat_id,
                                caption=f'{(await music_functions_async.get_track_name(track["track"]))}\n'
                                        f'находится на {track["chart"]["position"]} месте чартов\n'
                                        f'трек поднялся на {track["chart"]["shift"]} позиций')
                        file_sent = True
                    except telegram.error.TimedOut:
                        continue
            if tracks[0]['chart']['progress'] == 'new':
                await bot.send_message(chat_id=chat_id, text='Это список всех новых песен в списке чартов\n'
                                                             '···')
            else:
                await bot.send_message(chat_id=chat_id,
                                       text='Новых песен в чартах не появилось, а выше представлены'
                                            ' все самые значимые изменения\n'
                                            '···')
        else:
            await bot.send_message(chat_id=chat_id, text='Сегодня в чартах не произошло значимых изменений\n'
                                                         '···')

    # удаляет треки
    for track in tracks:
        track = track['track']
        os.remove(f'downloads/{await music_functions_async.get_name_for_file(track)}')
    return


def main():
    global bot, id_subscription

    # считывает id подписок из DB
    id_subscription = music_functions_async.get_id_subscription()

    bot = telegram.Bot(token=BOT_TOKEN)
    tracks = (asyncio.run(music_functions_async.search_new_track_chart()))
    asyncio.run(download_send_remove_track(tracks))


schedule.every().day.at("13:00").do(main)

while True:
    schedule.run_pending()
    time.sleep(30)
