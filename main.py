from enum import Enum, unique
import time
import logging
import telebot
import data
import config
from cipherlogic import Operation, Language, Cryptoprocessor

bot = telebot.TeleBot(config.TOKEN)


@unique
class State(Enum):
    NOT_STARTED = 0
    STARTED = 1


@unique
class Cipher(Enum):
    NO = 0
    MORSE = 1
    CAESAR = 2
    XOR = 3


@bot.message_handler(
    commands = ['start', 'help', 'go', 'begin', 'hello', 'hi'])
def send_welcome(message):
    if BotHandler.state == State.NOT_STARTED:
        BotHandler.state = State.STARTED
        logging.info('Dialog started')
        bot.send_sticker(message.chat.id, data.HELLO_STICKER_ID)
        bot.send_message(message.chat.id, data.HELLO_PHRASE)         
        msg = bot.send_message(message.chat.id, data.HOW_TO_STOP)         
        BotHandler.send_possible_ciphers(message)
        bot.register_next_step_handler(msg, BotHandler.select_cipher)


class BotHandler:
    '''
    Handles events of the dialog\n
    All methods of this class are static
    '''
    state = State.NOT_STARTED
    cipher = Cipher.NO
    operation = Operation.ENCODE
    language = Language.ENG
    string = ''
    key = ''

    @staticmethod
    def send_possible_ciphers(message):
        bot.send_message(message.chat.id, data.CHOOSE_PHRASE)

    @staticmethod
    def select_cipher(message):
        if (message.text == '1' or message.text == '2' or 
                message.text == '3'):             
            bot.send_message(message.chat.id,
                data.CIPHER_SELECTED.format(data.CIPHER_NAMES[int(message.text) - 1]))
            BotHandler.cipher = Cipher(int(message.text))
            logging.info(f'Selected cipher {data.CIPHER_NAMES[int(message.text) - 1].upper()}')             
            msg = bot.send_message(message.chat.id, data.ACTIONS)
            bot.register_next_step_handler(msg, BotHandler.select_action)
        else:
            BotHandler.handle_wrong_input(message)

    @staticmethod
    def select_action(message):
        if (message.text == '1'):
            BotHandler.operation = Operation.ENCODE
            logging.info('Selected operation ENCODE')
            if (BotHandler.cipher == Cipher.MORSE or
                BotHandler.cipher == Cipher.CAESAR):
                msg = bot.send_message(message.chat.id, data.INPUT_LANG)
                bot.register_next_step_handler(msg, BotHandler.select_lang)
            elif (BotHandler.cipher == Cipher.XOR):
                msg = bot.send_message(message.chat.id, data.INPUT_XOR_STRING_ENC)
                bot.register_next_step_handler(msg, BotHandler.input_string)
        elif (message.text == '2'):
            logging.info('Selected operation DECODE')
            BotHandler.operation = Operation.DECODE
            if (BotHandler.cipher == Cipher.MORSE or
                BotHandler.cipher == Cipher.CAESAR):
                msg = bot.send_message(message.chat.id, data.INPUT_LANG)
                bot.register_next_step_handler(msg, BotHandler.select_lang)
            elif (BotHandler.cipher == Cipher.XOR):
                msg = bot.send_message(message.chat.id, data.INPUT_XOR_STRING_DEC)
                bot.register_next_step_handler(msg, BotHandler.input_string)
        elif (message.text == '3'):
            logging.info('Selected operation TELLABOUT')
            path = data.INFO_FILES[BotHandler.cipher.value - 1]
            info = ''
            with open(path, 'r', encoding='cp1251') as file:
                info = file.read()             
            bot.send_message(message.chat.id, info)             
            msg = bot.send_message(message.chat.id, data.ACTIONS)
            logging.info(f'Info about cipher ' +
                f'{data.CIPHER_NAMES[int(BotHandler.cipher.value) - 1].upper()} was sent successfully')
            bot.register_next_step_handler(msg, BotHandler.select_action)
        elif (message.text == '4'):
            BotHandler.send_possible_ciphers(message)
            logging.info('Back to choosing cipher')
            bot.register_next_step_handler(message, BotHandler.select_cipher)
        else:
            BotHandler.handle_wrong_input(message)

    @staticmethod
    def select_lang(message):
        if (message.text == '1' or message.text == '2'):
            BotHandler.language = Language(int(message.text))
            logging.info(f'Selected language {message.text}')
            msg = None
            if (BotHandler.cipher == Cipher.MORSE):
                if (BotHandler.operation == Operation.ENCODE):
                    msg = bot.send_message(message.chat.id, data.INPUT_MORSE_STRING_ENC)
                elif (BotHandler.operation == Operation.DECODE):
                    msg = bot.send_message(message.chat.id, data.INPUT_MORSE_STRING_DEC)
            elif (BotHandler.cipher == Cipher.CAESAR):
                msg = bot.send_message(message.chat.id, data.INPUT_CAESAR_STRING)
            bot.register_next_step_handler(msg, BotHandler.input_string)
        else:
            BotHandler.handle_wrong_input(message)

    @staticmethod
    def input_string(message):
        BotHandler.string = message.text
        logging.info(f'String was input: {message.text}')
        if message.text == '/stop' and BotHandler.state != State.NOT_STARTED:
            BotHandler.turn_off(message)
            return
        if (BotHandler.cipher == Cipher.CAESAR):
            msg = bot.send_message(message.chat.id, data.INPUT_KEY_CAESAR)
            bot.register_next_step_handler(msg, BotHandler.input_key)
        elif (BotHandler.cipher == Cipher.XOR):
            msg = bot.send_message(message.chat.id, data.INPUT_KEY_XOR)
            bot.register_next_step_handler(msg, BotHandler.input_key)
        elif (BotHandler.cipher == Cipher.MORSE):
            try:
                result = ''
                if (BotHandler.operation == Operation.ENCODE):
                    result = Cryptoprocessor.encode_morse(message.text, BotHandler.language)
                elif (BotHandler.operation == Operation.DECODE):
                    result = Cryptoprocessor.decode_morse(message.text, BotHandler.language)
                BotHandler.send_result(message, result)
            except Exception as e:
                BotHandler.handle_error(message, e)

    @staticmethod
    def handle_error(message, e):
        bot.send_sticker(message.chat.id, data.ERROR_STICKER_ID)
        bot.send_message(message.chat.id, data.ERROR_PHRASE.format(e.__str__()))
        msg = bot.send_message(message.chat.id, data.FINISH)
        bot.register_next_step_handler(msg, BotHandler.finish)
        logging.error(f'Exception {e.__str__()}')

    @staticmethod
    def input_key(message):
        BotHandler.key = message.text
        logging.info(f'Key was input: {message.text}')
        if message.text == '/stop' and BotHandler.state != State.NOT_STARTED:
            BotHandler.turn_off(message)
            return
        if (BotHandler.cipher == Cipher.CAESAR):
            try:
                result = Cryptoprocessor.do_caesar_rotation(BotHandler.string,
                    BotHandler.language, int(BotHandler.key), BotHandler.operation)
                BotHandler.send_result(message, result)
            except Exception as e:
                BotHandler.handle_error(message, e)
        elif (BotHandler.cipher == Cipher.XOR):
            try:
                result = ''
                if (BotHandler.operation == Operation.ENCODE):
                    result = Cryptoprocessor.encrypt_with_xor(BotHandler.string, BotHandler.key)
                elif (BotHandler.operation == Operation.DECODE):
                    result = Cryptoprocessor.decrypt_with_xor(BotHandler.string, BotHandler.key)
                BotHandler.send_result(message, result)
            except Exception as e:
                BotHandler.handle_error(message, e)

    @staticmethod
    def send_result(message, result):
        bot.send_message(message.chat.id, 'Результат:')
        bot.send_message(message.chat.id, result)
        logging.info('Processing cipher is finished')
        msg = bot.send_message(message.chat.id, data.FINISH)
        bot.register_next_step_handler(msg, BotHandler.finish)

    @staticmethod
    def finish(message):
        if (message.text == '1'):
            BotHandler.cipher = Cipher.NO             
            BotHandler.send_possible_ciphers(message)
            bot.register_next_step_handler(message, BotHandler.select_cipher)
        elif (message.text == '2'):
            BotHandler.turn_off(message)
        else:
            BotHandler.handle_wrong_input(message)

    @staticmethod
    def handle_wrong_input(message):
        if message.text == '/stop' and BotHandler.state != State.NOT_STARTED:
            BotHandler.turn_off(message)
        elif not message.text.isnumeric():
            logging.warning('Unknown phrase was input')
            msg = bot.send_message(message.chat.id, data.DONT_UNDERSTAND)
            bot.send_message(message.chat.id, data.CHOOSE_PHRASE)             
            bot.register_next_step_handler(msg, BotHandler.select_cipher)
        elif message.text.isnumeric():
            logging.warning('Wrong number was input')              
            msg = bot.send_message(message.chat.id, data.WRONG_CIPHER_VARIANT)
            bot.send_message(message.chat.id, data.CHOOSE_PHRASE)
            bot.register_next_step_handler(msg, BotHandler.select_cipher)

    @staticmethod
    def turn_off(message):
        BotHandler.state = State.NOT_STARTED
        BotHandler.cipher = Cipher.NO             
        bot.send_message(message.chat.id, data.BYE_PHRASE)
        bot.send_sticker(message.chat.id, data.BYE_STICKER_ID)
        logging.info('Dialog finished')

if __name__ == '__main__':
    logging.basicConfig(filename='EnigmaLogs.log',
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(module)s ' +
        '%(funcName)s %(levelname)s: %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    bot.polling(none_stop=True)