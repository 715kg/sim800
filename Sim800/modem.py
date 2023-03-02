import datetime
import random
import serial

from termcolor import colored

from Sim800.phone_nubmer_to_sms import phone_number_to_sms
from Sim800.str_send import str_send
from Sim800.text_to_sms import text_to_sms


class sim800:

    def __init__(self, com, rate=9600, timeout=1):
        try:
            self._com = serial.Serial(com, rate, timeout=timeout)
        except serial.serialutil.SerialException:
            print(colored(f'Отказано в доступе, порт - {com} занят другим процессом или не существует', 'red'))

    # Переводим смс в юникод
    def sms_send(self, phone, message):
        # Если SMS большое, режем его для конкатенации SMS
        chunks = []

        if len(message) > 70:
            while len(message) > 66:
                chunks.append(message[:66])
                message = message[66:]
        if len(message) > 0:
            chunks.append(message)

        # готовим номер группы сообщений и устанавливаем 6-й бит SMS_SUBMIT_PDU
        SMS_SUBMIT_PDU = "11"
        CSMS_reference_number = ""
        if len(chunks) > 1:
            SMS_SUBMIT_PDU = "51"
            CSMS_reference_number = "%0.4X" % random.randrange(1, 65536)

        # Обязательная команда перед началом, так модем сможет синхронизировать скорость с портом
        if str_send(self._com, 'AT\n'):

            # устанавливаем нужный формат передачи данных
            if str_send(self._com, 'AT+CMGF=0\n'):
                print(colored('OK', 'green'))
                # передаем кусочки сообщения
                i = 1
                for chunk in chunks:
                    emessage = text_to_sms(chunk)
                    if CSMS_reference_number != "":
                        emessage = "06" + "08" + "04" + CSMS_reference_number + \
                                   ("%0.2X" % len(chunks)) + ("%0.2X" % i) + emessage
                    sms = "00"  # Накидываем тело сообщения в формате PDU
                    sms += SMS_SUBMIT_PDU
                    sms += "00"
                    sms += phone_number_to_sms(phone)
                    sms += "00"
                    sms += "08"
                    sms += "AA"
                    sms += "%0.2X" % (len(emessage) // 2)
                    sms += emessage

                    if str_send(self._com, 'AT+CMGS=' + str(len(sms) // 2 - 1) + '\r'):
                        print(colored('OK', 'green'))
                        if str_send(self._com, sms + chr(26)):
                            print(colored('OK', 'green'))
                            i += 1
                        else:
                            return False
                    else:
                        return False

                return True
            else:
                return False
        else:
            return False

    # Получить Ревизию модуля
    def get_revision(self):
        AT_COMMAND = "AT+GMR"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "")
        else:
            return False

    # Получить идентификатор модуля
    def get_identification(self):
        AT_COMMAND = "AT+GMM"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "")
        else:
            return False

    # Получить возможности модуля
    def get_possibilities(self):
        AT_COMMAND = "AT+GCAP"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "")
        else:
            return False

    # Получить imei
    def get_imei(self):
        AT_COMMAND = "AT+GSN"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "")
        else:
            return False

    # Информация об операторе
    def get_info_operators(self):
        AT_COMMAND = "AT+COPS?"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "").replace("+COPS: 0,0,", "").replace(
                '"', "")
        else:
            return False

    # Доступные операторы
    def get_available_operators(self):
        AT_COMMAND = "AT+COPS=?"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "")
        else:
            return False

    # Состояние модуля
    def get_module_stat(self):
        """
        0 – готов к работе
        2 – неизвестно
        3 – входящий звонок
        4 – голосовое соединение
        :return: String Состояние модуля
        """

        AT_COMMAND = "AT+CPAS"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "").replace("+CPAS:", "")
        else:
            return False

    # Тип регистрации сети
    def get_network_registration_type(self):
        """
            Первый параметр:
                0 – нет кода регистрации сети
                1 – есть код регистрации сети
                2 – есть код регистрации сети + доп параметры
            Второй параметр:
                0 – не зарегистрирован, поиска сети нет
                1 – зарегистрирован, домашняя сеть
                2 – не зарегистрирован, идёт поиск новой сети
                3 – регистрация отклонена
                4 – неизвестно
                5 – роуминг
        :return: String Вывод регистрации сети
        """

        AT_COMMAND = "AT+CREG?"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "").replace("+CREG:", "")
        else:
            return False

    # Уровень сигнала
    def get_signal_level(self):
        """
            Уровень сигнала:
                0 -115 дБл и меньше
                1 -112 дБл
                2-30 -110..-54 дБл
                31 -52 дБл и сильнее
                99 – нет сигнала.
        :return: String Вывод уровня сигнала
        """

        AT_COMMAND = "AT+CSQ"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "").replace("+CSQ:", "")
        else:
            return False

    # Текущая дата и время модуля
    def get_date_time(self):

        AT_COMMAND = "AT+CCLK?"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "").replace("+CCLK:", "").replace('"', "")
        else:
            return False

    # Напряжение модуя
    def get_supply_voltage(self):
        """
        Монитор напряжения питания модуля
            Первый параметр:
                0 – не заряжается
                1 – заряжается
                2 – зарядка окончена
            Второй параметр:
                1-100 % — уровень заряда батареи
            Третий параметр:
                Напряжение питание модуля (VBAT), мВ
        :return: String
        """
        AT_COMMAND = "AT+CBC"
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "").replace("OK", "").replace(AT_COMMAND, "").replace("+CBC:", "").replace('"', "")
        else:
            return False

    # Отправка команд
    def send_command_at(self, at_command):

        AT_COMMAND = at_command
        err, im = str_send(self._com, AT_COMMAND + '\n')

        if err:
            return im.replace("\n", "")
        else:
            return False

    def close(self):
        self._com.close()
