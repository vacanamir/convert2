
import os
import random
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from functools import wraps
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from ratelimit import limits, sleep_and_retry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7449691904:AAG1PPVODTRopC5qr7bzQ00aFi2NmKli5dQ"
bot = telebot.TeleBot(BOT_TOKEN)

@dataclass
class UserState:
    difficulty: str = "Easy Mode 😊"
    message_count: int = 0
    last_message_time: float = 0

class LeetSpeakBot:
    def __init__(self, token: str):
        self.bot = bot
        self.user_states: Dict[int, UserState] = {}
        self._setup_handlers()
        
    def _get_user_state(self, user_id: int) -> UserState:
        if user_id not in self.user_states:
            self.user_states[user_id] = UserState()
        return self.user_states[user_id]

    @sleep_and_retry
    @limits(calls=30, period=60)
    def _rate_limited_reply(self, message: telebot.types.Message, text: str, **kwargs):
        try:
            self.bot.reply_to(message, text, **kwargs)
        except telebot.apihelper.ApiException as e:
            logger.error(f"Telegram API error: {e}")
            self.bot.reply_to(message, "Sorry, an error occurred. Please try again later.")

    def _setup_handlers(self):
        self.bot.message_handler(commands=['start', 'help'])(self.send_welcome)
        self.bot.message_handler(commands=['mode'])(self.change_mode)
        self.bot.message_handler(func=lambda m: True)(self.handle_message)

    def send_welcome(self, message: telebot.types.Message):
        welcome_text = (
            "Welcome to the Leet Speak Converter Bot! 🤖\n\n"
            "Choose your mode:\n"
            "• Easy Mode 😊 - Simple replacements\n"
            "• Medium Mode 😐 - More complex symbols\n"
            "• Hard Mode 😈 - Complex symbols + Cyrillic\n"
            "• Binary Mode 🤖 - Convert to binary\n\n"
            "Change mode anytime with /mode"
        )
        self._rate_limited_reply(
            message, 
            welcome_text,
            reply_markup=self._get_keyboard(),
            parse_mode='Markdown'
        )

    def handle_message(self, message: telebot.types.Message):
        try:
            user_state = self._get_user_state(message.from_user.id)
            
            if message.text in ["Easy Mode 😊", "Medium Mode 😐", "Hard Mode 😈", "Binary Mode 🤖"]:
                user_state.difficulty = message.text
                self._rate_limited_reply(message, f"Mode set to: {message.text}\nNow send me any text!")
                return

            converted = TextConverter.convert_message(message.text, user_state.difficulty)
            self._rate_limited_reply(message, f'`{converted}`', parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._rate_limited_reply(message, "Sorry, an error occurred. Please try again.")

    @staticmethod
    def _get_keyboard() -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            KeyboardButton("Easy Mode 😊"),
            KeyboardButton("Medium Mode 😐"),
            KeyboardButton("Hard Mode 😈")
        )
        keyboard.add(KeyboardButton("Binary Mode 🤖"))
        return keyboard

    def run(self):
        logger.info("Bot started...")
        try:
            self.bot.polling()
        except Exception as e:
            logger.error(f"Critical error: {e}")

class TextConverter:
    
    @staticmethod
    def text_to_binary(text: str) -> str:
        return ' '.join(format(ord(char), '08b') for char in text)

    @staticmethod
    def convert_message(message: str, difficulty: str) -> str:
        if difficulty == "Binary Mode 🤖":
            return TextConverter.text_to_binary(message)
            
        words = message.split()
        return " ".join(
            TextConverter.convert_text_to_leet(word, difficulty) 
            if len(word) > 2 else word 
            for word in words
        )

    @staticmethod
    def convert_text_to_leet(text: str, difficulty: str) -> str:
        maps = {
            "easy": {
                'a': ['4'], 'e': ['3'], 'i': ['1'], 'o': ['0'],
                's': ['5'], 't': ['7'], 'b': ['8'], 'g': ['9'], 'l': ['1']
            },
            "medium": {
                'a': ['4', '@'], 'e': ['3', '€'], 'i': ['1', '!'],
                'o': ['0', '()'], 's': ['5', '$'], 't': ['7', '+'],
                'b': ['8', '|3'], 'g': ['9', '6'], 'l': ['1', '|'],
                'z': ['2', '7_'], 'q': ['9', '2'], 'w': ['uu'],
                'k': ['|<'], 'x': ['}{'], 'y': ['¥']
            },
            "cyrillic": {
                'a': 'а', 'b': 'в', 'c': 'с', 'd': 'д', 'e': 'е',
                'f': 'ф', 'g': 'г', 'h': 'н', 'i': 'и', 'j': 'й',
                'k': 'к', 'l': 'л', 'm': 'м', 'n': 'п', 'o': 'о',
                'p': 'р', 'r': 'я', 's': 'с', 't': 'т', 'u': 'у',
                'v': 'в', 'w': 'ш', 'x': 'х', 'y': 'у', 'z': 'з'
            }
        }

        result = []
        for char in text:
            lower_char = char.lower()
            
            if difficulty == "Hard Mode 😈":
                if random.random() < 0.5 and lower_char in maps["cyrillic"]:
                    result.append(maps["cyrillic"][lower_char].upper() if char.isupper() else maps["cyrillic"][lower_char])
                elif lower_char in maps["medium"]:
                    choice = random.choice(maps["medium"][lower_char])
                    result.append(choice.upper() if char.isupper() else choice)
                else:
                    result.append(char)
            elif difficulty == "Medium Mode 😐":
                if lower_char in maps["medium"]:
                    choice = random.choice(maps["medium"][lower_char])
                    result.append(choice.upper() if char.isupper() else choice)
                else:
                    result.append(char)
            else:
                if lower_char in maps["easy"]:
                    choice = maps["easy"][lower_char][0]
                    result.append(choice.upper() if char.isupper() else choice)
                else:
                    result.append(char)
                    
        return ''.join(result)

def main():
    bot = LeetSpeakBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
