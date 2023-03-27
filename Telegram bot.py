# Импортируем необходимые классы.
import logging
from telegram.ext import Application, MessageHandler, filters
from Token import BOT_TOKEN
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup,InputMediaPhoto,MenuButtonCommands,MenuButton,ReplyKeyboardRemove,MenuButtonWebApp,\
    InlineKeyboardButton, InlineKeyboardMarkup, MenuButton
# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.

# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я поисковая машина. Напишите мне что-нибудь, и я все сделаю, хозяин!",
    )

async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Этот умеет искать, сранивать и сохранять товары) А кирилл лох")

async def favourites_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Ничерта")


async def search_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    static_api_request = f"https://yandex.ru/images/search?pos=0&text=%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B0%20%D0%BD%D0%BE%D0%B6%D0%B0%20%D0%B4%D0%BB%D1%8F%20%D0%B8%D0%B3%D1%80&img_url=http%3A%2F%2Fw7.pngwing.com%2Fpngs%2F518%2F558%2Fpng-transparent-hunting-survival-knives-bowie-knife-utility-knives-weapon-knife-angle-arm-weapon.png&source=serp&rpt=simage&lr=53"
    medias = [InputMediaPhoto(static_api_request),
              InputMediaPhoto(static_api_request)]
    await context.bot.send_media_group(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её![](knife_6_01153805.jpg), не скачивая предварительно карту.
        medias, caption='''Нож питерский\nfgfgfg\nfgfgf😘'''
    )
    await update.message.reply_photo('knife_6_01153805.jpg', caption='''Нож питерский\nfgfgfg\nfgfgf😘''')
    await update.message.reply_text('knife_6_01153805.jpg')
async def photo_command(update,context):
    pass

async def echo(update, context):
    if (update.message.text).split()[0]=='Поиск:':
        static_api_request = (update.message.text).split()[1]
        medias = [InputMediaPhoto(static_api_request),
                  InputMediaPhoto(static_api_request)]
        await context.bot.send_media_group(
            update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
            # Ссылка на static API, по сути, ссылка на картинку.
            # Телеграму можно передать прямо её![](knife_6_01153805.jpg), не скачивая предварительно карту.
            medias, caption='''...
Первый товар
Цена: 250р
Отзывы: ⭐⭐⭐⭐
Ссылка для покупки: url.fgsjjhd
...
Второй товар
Цена: 250р
Отзывы: ⭐⭐⭐⭐
Ссылка для покупки: url.fgsjjhd
...
Третий товар
Цена: 250р
Отзывы: ⭐⭐⭐⭐
Ссылка для покупки: url.fgsjjhd
...'''
        )
    else:
        await update.message.reply_text(update.message.text)


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Регистрируем обработчик в приложении.
    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("favourites", favourites_command))
    application.add_handler(CommandHandler("search", search_command))

    # Запускаем приложение.
    application.run_polling()

async def start(update, context):
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
    )


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()