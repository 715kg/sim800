

# функция преобразования телефонного номера в формат, пригодный для SMS
def phone_number_to_sms(number):
    number += 'F'
    result = '0B' + '91'
    i = 0
    while i < len(number):
        result += number[i+1] + number[i]
        i += 2
    return result

