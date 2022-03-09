import logging
from os import getenv
from dotenv import load_dotenv

from telegram import Update
from telegram import InputFile
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from telegram.ext import Updater
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler

# Take environment variables from .env.
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# States for ConversationHandler
ASK, CAR, VIN, DETAIL, LOCATION, CONTACT = range(6)

# Links for channels
CHANNELS = {
    'lviv': '@lvivavtopro', #
    'kyiv': '@kyivavtopro', #
    'sumy': '@sumyavtopro', #
    'volyn': '@volynavtopro', #
    'odesa': '@odessaavtopro', #
    'ivano-frankivsk': '@ivanofrankivskavtopro', #
    'ternopil': '@ternopilavtopro', #
    'khmelnitsky': '@khmelnitskyavtopro', #
    'zakarpattya': '@zakarpattiaavtopro', #
    'chernivetskya': '@chernivtsiavtopro', #
    'vinnytsia': '@vinnytsiaavtopro', #
    'zhytomyr': '@zhytomyravtopro', #
    'dnipro': '@dniproavtopro', #
    'zaporozhye': '@zaporozhyeavtopro', #
    'kropyvnytskyi': '@kropyvnytskyiavtopro', #
    'mykolaiv': '@nikolaevavtopro', #
    'poltava': '@poltavaavtopro', #
    'kharkiv': '@kharkivavtopro', #
    'kherson': '@khersonavtopro', #
    'cherkasy': '@cherkasyavtopro', #
    'chernigiv': '@chernihivavtopro', #
    'rivne': '@rivneavtopro', #
    'lugansk': '@luganskavtopro', #
    'donezk': '@donezkavtopto', #
}


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user

    # Create the keyboard
    reply_keyboard = [
        [ KeyboardButton('Додати запит на деталь ⚙️') ],
        [ KeyboardButton('Наявні запити') ],
    ]

    # Send message
    update.message.reply_text(
        text="""Натискай "Додати запит на деталь ⚙", щоб у п’ять кроків знайти необхідне у своєму регіоні.""",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True, 
            input_field_placeholder='Тисни',
            resize_keyboard=True
        )
    )

    # Logger
    logger.info("%s: send /start command;", user.first_name)


def helper(update: Update, context: CallbackContext) -> int:
    """Command Help /help"""
    user = update.message.from_user

    # Send message
    update.message.reply_text(
        text="""ℹ️ Вкажи якомога докладніше, яку саме запчастину та на яке авто шукаєш. Виконуй вказівки бота, щоб надати необхідну інформацію продавцям та прискорити відгук на свій запит."""
    )

    # Logger
    logger.info("%s: send /help command;", user.first_name)


def channel_list(update: Update, context: CallbackContext) -> int:
    """Send list of chats to user"""
    user = update.message.from_user

    # Send message
    update.message.reply_text(
        text="""Якщо маєш запчастини на продаж, знайди покупця у місцевому чаті 🤝:\n"""+'\n'.join([x for x in CHANNELS.values()])
    )

    # Logger
    logger.info("%s: ask channel list;", user.first_name)


def ask(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user

    # Create user detail request in user_data
    context.user_data['detail_request'] = {}

    # Send message and remove keyboard
    update.message.reply_text(
        text="1️⃣ Вкажи марку та модель свого авто:",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Logger
    logger.info("%s: start creating the request", user.first_name)

    return CAR


def car(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user

    # Set car name to user_data
    value = update.message.text
    context.user_data['detail_request']['car'] = value

    # Send message
    update.message.reply_text(
        text="2️⃣Напиши VIN номер авто:"
    )

    # Logger
    logger.info("%s: set %s as car;", user.first_name, value)

    return VIN


def vin(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user

    # Set car VIN name to user_data
    value = update.message.text
    context.user_data['detail_request']['car_vin'] = value 

    # Send message
    update.message.reply_text(
        text="3️⃣Напиши через кому всі запчастини, які тобі потрібні:"
    )

    # Logger
    logger.info("%s: set VIN: %s;", user.first_name, value)

    return DETAIL

def error_vin(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    value = update.message.text

    # Send message
    update.message.reply_text(
        text="VIN номер неправильний. Він має містити 17 символів. Спробуй ще раз."
    )

    # Logger
    logger.info("%s: send invalid VIN: %s;", user.first_name, value)

    return VIN


def detail(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user

    # Set detail_name to user_data
    value = update.message.text
    context.user_data['detail_request']['detail'] = value   

    # Make the keyboard
    keyboard = [
        [
            InlineKeyboardButton("Львівська", callback_data='lviv'),
            InlineKeyboardButton("Івано-Франківська", callback_data='ivano-frankivsk'),
            InlineKeyboardButton("Тернопільська", callback_data='ternopil')
        ],
        [
            InlineKeyboardButton("Хмельницька", callback_data='khmelnitsky'),
            InlineKeyboardButton("Закарпатська", callback_data='zakarpattya'),
            InlineKeyboardButton("Чернівецька", callback_data='chernivetskya')
        ],
        [
            InlineKeyboardButton("Вінницька", callback_data='vinnytsia'),
            InlineKeyboardButton("Житомирська", callback_data='zhytomyr'),
            InlineKeyboardButton("Київська", callback_data='kyiv')
        ],
        [
            InlineKeyboardButton("Дніпропетровська", callback_data='dnipro'),
            InlineKeyboardButton("Запорізька", callback_data='zaporozhye'),
            InlineKeyboardButton("Кіровоградська", callback_data='kropyvnytskyi')
        ],
        [
            InlineKeyboardButton("Миколаївська", callback_data='mykolaiv'),
            InlineKeyboardButton("Волинська", callback_data='volyn'),
            InlineKeyboardButton("Одеська", callback_data='odesa')
        ],
        [
            InlineKeyboardButton("Полтавська", callback_data='poltava'),
            InlineKeyboardButton("Сумська", callback_data='sumy'),
            InlineKeyboardButton("Харківська", callback_data='kharkiv')
        ],
        [
            InlineKeyboardButton("Херсонська", callback_data='kherson'),
            InlineKeyboardButton("Черкаська", callback_data='cherkasy'),
            InlineKeyboardButton("Чернігівська", callback_data='chernigiv')
        ],
        [   
            InlineKeyboardButton("Луганська", callback_data='lugansk'),
            InlineKeyboardButton("Рівненська", callback_data='rivne'),
            InlineKeyboardButton("Донецька", callback_data='donezk'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message    
    update.message.reply_text(
        text="4️⃣ Вкажи свою область, щоб наші продавці швидше надали тобі запчастини:",
        reply_markup=reply_markup
    )

    # Logger
    logger.info("%s: ask detail: %s;", user.first_name, value)

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    query = update.callback_query
    query.answer()

    # Get callback
    chat_id = update.callback_query.message.chat.id
    message_id = update.callback_query.message.message_id

    # Set request location name to user_data
    location = update.callback_query.data
    context.user_data['detail_request']['location'] = location

    # Delete message with location inline keyboard
    context.bot.delete_message(chat_id, message_id)

    # Send message
    context.bot.send_message(
        chat_id=chat_id,
        text="""5⃣ Натискай "Відправити номер📞", щоб продавець міг з тобою зв'язатися" """,
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton(
                    text='Відправити номер 📞',
                    request_contact=True
                )]
            ], 
            one_time_keyboard=True, 
            input_field_placeholder='Надішли свій номер натиснувши кнопку нижче ⤵️',
            resize_keyboard=True
        ),
    )

    # Logger
    logger.info("%s: set location: %s;", chat_id, location)

    return CONTACT


def error_location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    value = update.message.text

    # Send message
    update.message.reply_text(
        text="Надішли локацію за допомогою клавіатури у повідомлені вище."
    )

    # Logger
    logger.info("%s: send invalid location: %s;", user.first_name, value)

    return LOCATION


def contact(update: Update, context: CallbackContext) -> int:
    """Get contact info about the user."""
    user = update.message.from_user

    # Get request info from user_data
    detail_request = context.user_data.get('detail_request', 'Not found')

    # get channel name
    channel_name = CHANNELS[detail_request['location']]

    # set contact
    contact = update.message.contact
    context.user_data['detail_request']['contact'] = {}
    context.user_data['detail_request']['contact']['user_id'] = contact.user_id
    context.user_data['detail_request']['contact']['phone_number'] = contact.phone_number

    # Send message
    update.message.reply_text(
        text=f"Дякую за звернення ✅\nОчікуй дзвінок від продавця найближчим часом!\nСтан запиту можна відстежувати у каналі - {channel_name}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Logger 1
    logger.info("%s: set contact: %s;", user.first_name, contact)

    # Send request to channels
    context.bot.send_message(
        chat_id=channel_name,
        text=f"""✅ Нова заявка на запчастину!\n\n🚗 Автомобіль: {detail_request['car']};\n⚙️ Необхідна деталь: {detail_request['detail']};\nVIN номер: {detail_request['car_vin']};\n\nОбласть: {detail_request['location']};\n📞 Контакт: {detail_request['contact']['phone_number']};""",
    )

    # Logger 2
    logger.info("Bot send %s`s request to %s;", user.first_name, channel_name)

    return ConversationHandler.END


def error_contact(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    value = update.message.text

    # Send message
    update.message.reply_text(
        text="Надішліть номер кнопкою нижче"
    )

    # Logger
    logger.info("%s: send invalid Contact: %s;", user.first_name, value)

    return CONTACT


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user    

    update.message.reply_text(
        text='Дякуємо за увагу, до побачення 👋', 
        reply_markup=ReplyKeyboardRemove()
    )

    # Logger
    logger.info("User %s canceled the conversation.", user.first_name)

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(getenv("BOT_TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^Додати запит на деталь ⚙️$'), ask)
        ],
        states={
            CAR: [ 
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, car)                
            ],

            VIN: [
                MessageHandler(
                    Filters.regex(r"^(?=.*[0-9])(?=.*[A-z])[0-9A-z-]{17}$"), vin
                ),
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, error_vin)
            ],

            DETAIL: [
                CommandHandler('cancel', cancel),            
                MessageHandler(Filters.text, detail)                
            ],

            LOCATION: [
                CallbackQueryHandler(location),
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, error_location)                
            ],

            CONTACT: [
                MessageHandler(Filters.contact, contact),
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, error_contact)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel)
        ]
    )

    dispatcher.add_handler(conv_handler)

    # command handler
    dispatcher.add_handler(CommandHandler("start", start)) 
    dispatcher.add_handler(CommandHandler("help", helper))

    dispatcher.add_handler(
        MessageHandler(Filters.regex('^Наявні запити$'), channel_list)
    )   

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()