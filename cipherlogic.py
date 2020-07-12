import string
from enum import Enum, unique
import morsedicts

@unique
class Language(Enum):
    ENG = 1
    RUS = 2


@unique
class Operation(Enum):
    ENCODE = 1
    DECODE = 2


class Cryptoprocessor:
    '''
    Contains algorithms for encoding and decoding data:\n
    Morse, ROT and XOR\n
    All methods of this class are static
    '''
    
    @staticmethod
    def encode_morse(input, language=Language.ENG):
        '''
        Returns a numeric string of symbol codes divided by spaces.
        '''
        letters = []
        for i in filter(str.isalnum, input.lower()):
            try:
                if i.isnumeric():
                    letters.append(morsedicts.MORSE_CODE_NUMBER_DICT[i])
                elif language == Language.ENG:
                    letters.append(morsedicts.MORSE_CODE_ENG_DICT[i])
                elif language == Language.RUS:
                    letters.append(morsedicts.MORSE_CODE_RUS_DICT[i])
            except Exception:
                raise Exception('Проверьте входные данные')
        return ' '.join(letters)

    @staticmethod
    def decode_morse(input, language=Language.ENG):
        '''
        Returns a string of russian or english letters and numbers.
        '''
        result = ''
        for i in input.split(' '):
            if not i.isnumeric():
                raise Exception('Входная строка может содержать только числа и пробелы')
            for item in morsedicts.MORSE_CODE_NUMBER_DICT.items():
                if item[1] == i:
                    result += item[0]
            if language == Language.ENG:
                for item in morsedicts.MORSE_CODE_ENG_DICT.items():
                    if item[1] == i:
                        result += item[0]
            elif language == Language.RUS:
                for item in morsedicts.MORSE_CODE_RUS_DICT.items():
                    if item[1] == i:
                        result += item[0]
        return result

    @staticmethod
    def do_caesar_rotation(input, language=Language.ENG, shift=13,
                            operation=Operation.ENCODE):
        '''
        Returns a string of russian or english letters and spaces
        '''
        # power of the alphabet
        total = 26 if language == Language.ENG else 32
        # code of the first letter in the alphabet
        first = ord('a') if language == Language.ENG else ord('а')
        result = ''
        if (shift < 1 or shift >= total):
            raise Exception('Неверная величина сдвига')
        clean_string = ''
        # remain only letters, numbers and spaces
        for i in input.lower():
            if (i.isalnum() or i.isspace()):
                clean_string += i
        for i in clean_string:        
            if i != ' ':
                if (language == Language.RUS and (ord(i) > 1103 or ord(i) < 1072)):
                    raise Exception('Допустимы только буквы а-я')
                if (language == Language.ENG and (ord(i) < 97 or ord(i) > 122)):
                    raise Exception('Допустимы только буквы a-z')
                if operation == Operation.ENCODE:
                    result += chr(first + ((ord(i) + shift - first) % total))
                else:
                    result += chr(first + ((ord(i) - shift - first) % total))
            else:
                # algorithm saves all spaces
                result += ' '
        return result

    @staticmethod
    def encrypt_with_xor(input, key):
        '''
        Returns a string of numbers divided by dots.
        '''
        if len(input) != len(key):
            raise Exception('Длины строки и ключа должны быть равными')
        for i in input:
            if not i.isalnum():
                raise Exception('Строка может содержать только буквы и числа,"\
                    " пунктуация и пробелы запрещены')
        for i in key:
            if not i.isalnum():
                raise Exception('Ключ может содержать только буквы и числа,"\
                    " пунктуация и пробелы запрещены')
        symbols = string.ascii_lowercase + '1234567890абвгдежзийклмнопрстуфхцчшщъыьэюя'
        result = ''
        for i in range(len(input)):
            a = input[i]
            b = key[i]
            c = symbols.index(a) ^ symbols.index(b)
            # don't make a dot after the result
            if i == len(input) - 1:
                result += str(c)
            else:
                result += str(c) + '.'
        return result

    @staticmethod
    def decrypt_with_xor(code, key):
        '''
        Returns a string of russian letters, english letters and numbers.
        '''
        for i in code:
            if not i.isnumeric() and i != '.':
                raise Exception ('Входная строка может содержать только числа и точки')
        characters = code.split('.')
        for i in range(len(characters)):
            characters[i] = int(characters[i])
        if len(characters) != len(key):
            raise Exception('Длины строки и ключа должны быть равными')
        for i in key:
            if not i.isalnum():
                raise Exception('Ключ может содержать только буквы и числа,"\
                    " пунктуация и пробелы запрещены')
        symbols = string.ascii_lowercase + '1234567890абвгдежзийклмнопрстуфхцчшщъыьэюя'
        answer = ''
        for i in range(len(characters)):
            c = characters[i]
            b = symbols.index(key[i])
            a = c ^ b
            answer += symbols[a]
        return answer