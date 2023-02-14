# 2023-02-14

# загрузка библиотек
import numpy as np
import pandas as pd
import os
import datetime
from openmeteo_py import Hourly,Daily,Options,OWmanager

import plotly
import plotly.express as px
from dash import html

import time
import datetime

# отправка на почту
import smtplib
import mimetypes
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication



# Рабочая директория
os.chdir('/home/**********/Weather')

# Сегодня
time0 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# Новогорск 55.905922, 37.329879
latitude = 55.905922
longitude = 37.329879

hourly = Hourly()
daily = Daily()
options = Options(latitude,longitude)

mgr = OWmanager(options,
    hourly.all(),
    daily.all())


# Download data
meteo = mgr.get_data()

# Ornikovo 55.992085, 36.899756

latitude = 55.992085
longitude = 36.899756

hourly = Hourly()
daily = Daily()
options = Options(latitude,longitude)

mgr = OWmanager(options,
    hourly.all(),
    daily.all())


# Download data
meteo1 = mgr.get_data()


# df только по дням и температура в Химках
df = pd.DataFrame(meteo['daily'], columns=['time', 'temperature_2m_max', 'temperature_2m_min'])
df.rename(columns={'time': 'Дата', 'temperature_2m_max': 'Темпер_макс', 'temperature_2m_min': 'Темпер_мин'}, inplace=True)

# df только по дням и температура в Огниково
df1 = pd.DataFrame(meteo1['daily'], columns=['time', 'temperature_2m_max', 'temperature_2m_min'])
df1.rename(columns={'time': 'Дата', 'temperature_2m_max': 'Темпер_макс', 'temperature_2m_min': 'Темпер_мин'}, inplace=True)

# соед два df
mer = pd.merge(df, df1, left_index=True, right_index=True)

# Улучшаю табл.
mer.drop('Дата_y', axis=1, inplace=True)
mer.rename(columns={'Дата_x': 'Дата', 'Темпер_макс_x': 'Темпер_макс_Хмк', 'Темпер_мин_x': 'Темпер_мин_Хмк', 'Темпер_макс_y': 'Темпер_макс_Огн', 'Темпер_мин_y': 'Темпер_мин_Огн'}, inplace=True)


# Переменные
data1 = mer.iloc[0, 0]
temp_Xmk = mer.iloc[0, 1]
temp_Ogn = mer.iloc[0, 3]

# создаю переменную что бы не загружать формулу построения графика
temp = ['Темпер_макс_Хмк', 'Темпер_мин_Хмк', 'Темпер_макс_Огн', 'Темпер_мин_Огн']

# Построение графика:
fig = px.line(mer, x='Дата', y=temp, markers=True, line_shape='spline',
            title=f'Прогноз погоды в Химках (Новогорск) и Огниково. \
                    <br> На {data1} температура в Химках (Новогорск): <b>{temp_Xmk}</b>℃ и в Огниково: <b>{temp_Ogn}</b>℃ \
                    <br>Источник инф.: <a>https://open-meteo.com/</a>')

fig.add_annotation(x='left', y='top',
            text=f'{time0}. Подготовил: Смоленышев Олег, smolenishev@mail.ru',
            showarrow=False,
            arrowhead=0, font=dict(color='grey', size=12))

fig.update_layout(
    autosize=False,
    width=1200,
    height=600,
    margin=dict(
        l=10,
        r=10,
        b=100,
        t=100,
        # pad=0
    ),
    paper_bgcolor="white",
)

# fig.update_traces(textposition="bottom right")
# fig.show()

# созранюя
fig.write_html('Weather_1.html')
fig.write_image('Weather_1.pdf')

# задерждка что бы файлы для отправки создались
time.sleep(5)

# время в письме
time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
print(time)


# Тело письма
text_body = f"This is mail about the weather  has been sent {time}:\n\n - Temperature in Khimki is {temp_Xmk}℃\n - Temperature in Ognikovo is {temp_Ogn}℃\n\n, best wishes from Smolenishev Oleg!!"

# Create a text/plain message
msg = email.mime.multipart.MIMEMultipart()
msg['Subject'] = 'The Weather'
msg['From'] = 'smolenishev@yandex.ru'
msg['To'] = 'smolenishev@mail.ru'

# The main body is just another attachment
body = email.mime.text.MIMEText(text_body)
msg.attach(body)

# PDF attachment
filename='/home/*******************/Weather_1.pdf'
# filename='Weather_1.pdf'
fp=open(filename,'rb')
att = email.mime.application.MIMEApplication(fp.read(),_subtype="pdf")
fp.close()
att.add_header('Content-Disposition','attachment',filename=filename)
msg.attach(att)


s = smtplib.SMTP('smtp.yandex.ru', 587)

s.starttls()
s.login('****************','*********')
s.sendmail('smolenishev@yandex.ru',['smolenishev@mail.ru', '******'], msg.as_string())
s.quit()

