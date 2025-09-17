import sys

# кодирование идёт вверх по таблице
# декодирование идёт вниз по таблице
def apply_caesar_algorithm(pattern, string, shift):
    pattern_encode = 'encode'
    pattern_decode = 'decode'
    # по ASCII таблице
    start_eng_char = 97
    end_eng_char = 122


    if pattern == pattern_encode:
        phrase = encode(string, shift, start_eng_char, end_eng_char)
        print(phrase)
        return phrase
    elif pattern == pattern_decode:
        phrase = decode(string, shift, start_eng_char, end_eng_char)
        print(phrase)
        return phrase
    print(f'wrong pattern: {pattern}')
    return



def encode(string, shift, start_code, end_code):
    power_alphabet = end_code - (start_code - 1) # если не -1, то убирает и позицию старта
    code_phrase = ''
    shift = int(shift)
    for ch in string:
        if ch.isalpha():
            char = ch.lower()
            if is_char_eng(char):
                # если нужны более гибкие рабоды в кодом
                # number_in_alphabet = ord(char) - start_code
                # code_char = (number_in_alphabet + shift) % power_alphabet
                # print(((ord(char) + shift) - start_code) % power_alphabet)
                code_phrase += chr(start_code + ((ord(char) + shift) - start_code) % power_alphabet).lower()
                continue
            else:
                return False
        code_phrase += ch

    return code_phrase

def decode(string, shift, start_code, end_code):
    power_alphabet = end_code - (start_code - 1)  # если не -1, то убирает и позицию старта
    code_phrase = ''
    shift = int(shift)
    for ch in string:
        if ch.isalpha():
            char = ch.lower()
            if is_char_eng(char):
                # number_in_alphabet = ord(char) - start_code
                # code_char = (number_in_alphabet + shift) % power_alphabet
                # print(((ord(char) - shift) - start_code) % power_alphabet)
                code_phrase += chr(start_code + ((ord(char) - shift) - start_code) % power_alphabet).lower()
                continue
            else:
                return False
        code_phrase += ch

    return code_phrase
    return

# проверка на русские символы, ё и Ё находятся где-то отдельно, после "я"
def is_char_cyrillic(ch):
    return True if 'а' <= ch <= 'я' or 'А' <= ch <= 'Я' or ch in ('ё', 'Ё') else False
# char.isalpha() - проверка на букву
# char.isascii() - проверяет, находится ли символ в ASCII-диапазоне
# этот пододойдёт лучше

def is_char_eng(ch):
    return True if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' else False

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Enter: pattern, string, shift')
        sys.exit(0)

    apply_caesar_algorithm(sys.argv[1], sys.argv[2], sys.argv[3])