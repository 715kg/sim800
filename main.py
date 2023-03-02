from Sim800.modem import sim800

sm = sim800('COM16', 115200, 2)

sms = sm.sms_send('79920000000', 'Привет мой друг!')

if sms:
    print('Отправлено')
else:
    print('ошибка')

sm.close()
