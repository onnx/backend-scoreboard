import sys
import smtplib
import os
from email.mime.text import MIMEText
from dateutil import parser
from datetime import datetime, timedelta

if parser.parse(sys.argv[1][:-1]) < datetime.now() - timedelta(days=2):
    fp = open('out_of_date_msg.txt', 'rb')
    msg = MIMEText(fp.read())
    fp.close()

    msg['Subject'] = 'Docker Image for ONNX Scoreboard Out of Date'
    msg['From'] = 'onnxscoreboard@gmail.com'
    msg['To'] = 'lufang@fb.com'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login('onnxscoreboard@gmail.com', os.environ.get('GMAIL_PWD'))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

