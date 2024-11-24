import random
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "7449691904:AAG1PPVODTRopC5qr7bzQ00aFi2NmKli5dQ"
bot = telebot.TeleBot(BOT_TOKEN)

user_difficulties = {}

def get_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("Easy Mode 😊"),
        KeyboardButton("Medium Mode 😐"),
        KeyboardButton("Hard Mode 😈")
    )
    keyboard.add(KeyboardButton("Binary Mode 🤖"))
    return keyboard

def text_to_binary(text: str) -> str:
    return ' '.join(format(ord(char), '08b') for char in text)

def convert_message(message: str, difficulty: str) -> str:
    if difficulty == "Binary Mode 🤖":
        return text_to_binary(message)
        
    words = message.split()
    converted = []
    
    for word in words:
        if len(word) > 2:
            converted.append(convert_text_to_leet(word, difficulty))
        else:
            converted.append(word)
            
    return " ".join(converted)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Welcome to the Leet Speak Converter Bot! 🤖\n\n"
        "Choose your mode:\n"
        "• Easy Mode 😊 - Simple replacements, very readable\n"
        "• Medium Mode 😐 - More complex symbols\n"
        "• Hard Mode 😈 - Complex symbols + Cyrillic letters\n"
        "• Binary Mode 🤖 - Convert text to binary\n\n"
        "You can change the mode at any time by sending /mode"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_keyboard(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text in ["Easy Mode 😊", "Medium Mode 😐", "Hard Mode 😈", "Binary Mode 🤖"]:
        user_difficulties[message.from_user.id] = message.text
        bot.reply_to(message, f"Mode set to: {message.text}\nNow send me any text!")
        return

    difficulty = user_difficulties.get(message.from_user.id, "Easy Mode 😊")
    converted = convert_message(message.text, difficulty)
    formatted_message = f'`{converted}`'
    bot.reply_to(message, formatted_message, parse_mode='Markdown')

def convert_text_to_leet(text: str, difficulty: str) -> str:
    easy_map = {
        'a': ['4'],
        'e': ['3'],
        'i': ['1'],
        'o': ['0'],
        's': ['5'],
        't': ['7'],
        'b': ['8'],
        'g': ['9'],
        'l': ['1']
    }
    
    medium_map = {
        'a': ['4', '@'],
        'e': ['3', '€'],
        'i': ['1', '!'],
        'o': ['0', '()'],
        's': ['5', '$'],
        't': ['7', '+'],
        'b': ['8', '|3'],
        'g': ['9', '6'],
        'l': ['1', '|'],
        'z': ['2', '7_'],
        'q': ['9', '2'],
        'w': ['uu'],
        'k': ['|<'],
        'x': ['}{'],
        'y': ['¥']
    }
    
    cyrillic_map = {
        'a': 'а', 'b': 'в', 'c': 'с', 'd': 'д', 'e': 'е',
        'f': 'ф', 'g': 'г', 'h': 'н', 'i': 'и', 'j': 'й',
        'k': 'к', 'l': 'л', 'm': 'м', 'n': 'п', 'o': 'о',
        'p': 'р', 'r': 'я', 's': 'с', 't': 'т', 'u': 'у',
        'v': 'в', 'w': 'ш', 'x': 'х', 'y': 'у', 'z': 'з'
    }
    
    result = ""
    for char in text:
        lower_char = char.lower()
        
        if difficulty == "Hard Mode 😈":
            if random.random() < 0.5 and lower_char in cyrillic_map:
                result += cyrillic_map[lower_char] if char.islower() else cyrillic_map[lower_char].upper()
            elif lower_char in medium_map:
                result += random.choice(medium_map[lower_char]) if char.islower() else random.choice(medium_map[lower_char]).upper()
            else:
                result += char
        elif difficulty == "Medium Mode 😐":
            if lower_char in medium_map:
                result += random.choice(medium_map[lower_char]) if char.islower() else random.choice(medium_map[lower_char]).upper()
            else:
                result += char
        else:  # Easy Mode
            if lower_char in easy_map:
                result += easy_map[lower_char][0] if char.islower() else easy_map[lower_char][0].upper()
            else:
                result += char
            
    return result

def convert_message(message: str, difficulty: str) -> str:
    words = message.split()
    converted = []
    
    for word in words:
        if len(word) > 2:
            converted.append(convert_text_to_leet(word, difficulty))
        else:
            converted.append(word)
            
    return " ".join(converted)

@bot.message_handler(commands=['mode'])
def change_mode(message):
    bot.reply_to(message, "Select conversion difficulty:", reply_markup=get_keyboard())

def main():
    try:
        print("Bot started...")
        bot.polling()
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
