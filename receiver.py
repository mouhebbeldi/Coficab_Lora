from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD

from Adafruit_IO import RequestError, Client, Feed

import random
from time import time, sleep
import smtplib
import ssl
aio_username = 'mouhebbeldi'
aio_key = 'aio_gbEZ797bT9OYpw3K2uaCB6OqeZ4y'
aio = Client(aio_username, aio_key)

def send_mail(mysubject, mytext):
    context = ssl.create_default_context()
    gmail_user = 'mouhebbeldi@gmail.com'
    gmail_password = 'coolerAsMoolerStrongEnough'
    send_to = 'mouhebbeldi77@gmail.com'
    message = 'Subject: {}\n\n{}'.format(mysubject, mytext)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, send_to, message)

        server.quit()
    except:
        print('Error sending email')




BOARD.setup()
class LoRaRcvCont(LoRa):
    global hum
    global temp
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 10)

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()


    def on_rx_done(self):
        print("\nReceived: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        finalData= bytes(payload).decode("utf-8",'ignore')
        hum = finalData[2:6]
        temp = finalData[7:11]
        print(hum,temp)

        #######################Email Alerts############################
        if (float(temp) > 90):
            send_mail("Temperature OVER:90",
                      "Temperature is under it's maximum level 20: \nThe current temperature is: {} degrees.".format(temp))
            print("TEMPERATURE email ALERT sent to mouhebbeldi77@gmail.com\n")

        if (temp < -20):
        send_mail("Temperature UNDER -20:",
                  "Temperature is under it's minimum level -20: \n The current temperature is: {}°.".format(temp))
        print("TEMPERATURE email ALERT sent to mouhebbeldi77@gmail.com\n")

        if (float(hum) > 80):
            send_mail("Humidity OVER:80",
                  "Humidity is over its maximum level\n The current humidity is: {}%.".format(hum))
            print("HUMIDITY email ALERT sent to mouhebbeldi77@gmail.com\n")
        #######################Email Alerts############################

        try:
            temperature = aio.feeds('temperature')
        except RequestError:
            temperature_feed = Feed(name='temperature')
            temperature_feed = aio.create_feed(temperature_feed)
        aio.send_data(temperature.key, temp)
        print("temperature value sent to Adafruit.io\n")


        try:
            humidity = aio.feeds('humidity')
        except RequestError:
            humidity_feed = Feed(name='humidity')
            humidity_feed = aio.create_feed(humidity_feed)
        aio.send_data(humidity.key, hum)
        print("humidity value sent to Adafruit.io\n")





        ###################################################
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)

#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm

lora.set_pa_config(pa_select=1)



try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()

