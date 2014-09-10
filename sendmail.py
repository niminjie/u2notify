#coding: utf-8  
import smtplib  
from email.mime.text import MIMEText  
from email.header import Header  
from email.MIMEMultipart import MIMEMultipart

def send_mail(receiver, subject, text):
    sender = 'niminjiecide@163.com'
    smtpserver = 'smtp.163.com'  
    username = 'niminjiecide@163.com'  
    password = 'a19900826'  

    msg = MIMEText(text)
    msg.set_charset("utf-8")
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    smtp = smtplib.SMTP()  
    smtp.connect('smtp.163.com')  
    smtp.login(username, password)  
    smtp.sendmail(sender, receiver, msg.as_string())  
    smtp.quit()

# if __name__ == "__main__":
#     send_mail('niminjiecide@gmail.com', 'HELLO U2', 'osidfnoiasdfsdfp[s]dfp[aebk oajfiboarepgjvaioejvioadb')
