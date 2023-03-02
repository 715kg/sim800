# функция, кодирующая юникодную строку в формат SMS
def text_to_sms(text):
    b = text
    result = ''
    i = 0
    while i < len(b):
        o = ord(b[i])
        result += ("%0.2X" % (o // 256)) + ("%0.2X" % (o % 256))
        i += 1
    return result
