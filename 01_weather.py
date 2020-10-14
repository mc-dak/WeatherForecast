# -*- coding: utf-8 -*-
import re
import threading
import requests
from bs4 import BeautifulSoup
import datetime
import cv2
from model import Weather, Image, database_proxy, database


class ImageMaker:
    def __init__(self):
        self.day_condition = None
        self.day_conditions = []
        self.l_img = cv2.imread('data_for_weather/photos/weather_img/probe.jpg')
        self.s_img = None
        self.x_offset = 412
        self.y_offset = 0
        self.color = None

    def define_small_picture_to_add_and_gradient(self):
        sun_conditions = ['sun', 'clear']
        cloud_conditions = ['cloudy', 'overcast', 'fog']
        snow_conditions = ['snow']
        rain_conditions = ['rain', 'shower', 'drizzle']
        yellow = [0, 255, 255]
        blue = [255, 0, 0]
        gray = [169, 169, 169]
        cyan = [255, 255, 0]
        sun_picture = cv2.imread('data_for_weather/photos/weather_img/sun.jpg')
        cloud_picture = cv2.imread('data_for_weather/photos/weather_img/cloud.jpg')
        snow_picture = cv2.imread('data_for_weather/photos/weather_img/snow.jpg')
        rain_picture = cv2.imread('data_for_weather/photos/weather_img/rain.jpg')
        if (self.day_condition in sun_conditions) or (
                list(set(self.day_conditions) & set(sun_conditions))):
            self.s_img = sun_picture
            self.color = yellow
        elif (self.day_condition in cloud_conditions) or (
                list(set(self.day_conditions) & set(cloud_conditions))):
            self.s_img = cloud_picture
            self.color = gray
        elif (self.day_condition in snow_conditions) or (
                list(set(self.day_conditions) & set(snow_conditions))):
            self.s_img = snow_picture
            self.color = cyan
        elif (self.day_condition in rain_conditions) or (
                list(set(self.day_conditions) & set(rain_conditions))):
            self.s_img = rain_picture
            self.color = blue

    def make_gradient(self):
        if self.color == [169, 169, 169]:
            k = 3
        else:
            k = 1
        line_thickness = k * 3
        for i in range(0, 255, k):
            r = self.color[0] + i
            g = self.color[1] + i
            b = self.color[2] + i
            cv2.line(self.l_img, (i * k, 0), (i * k, 256), (r, g, b), thickness=line_thickness)

    def put_text(self, weather):
        black = (0, 0, 0)
        cv2.putText(self.l_img, f"temperature : {weather.avgtempC} C", (20, 40),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7,
                    color=black)
        cv2.putText(self.l_img, f" date : {weather.date}", (20, 80), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5, color=black)
        cv2.putText(self.l_img, f" wind speed Kmph : {weather.windspeedKmph}", (20, 100),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5, color=black)
        cv2.putText(self.l_img, f" weather Desc : {weather.weatherDesc}", (20, 120),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                    color=black)
        cv2.putText(self.l_img, f" precipitation MM : {weather.precipMM}", (20, 140),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                    color=black)
        cv2.putText(self.l_img, f" humidity : {weather.humidity} %", (20, 160),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,
                    color=black)
        cv2.putText(self.l_img, f" pressure : {weather.pressure}", (20, 180), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=black)

    @staticmethod
    def view_image(image, name_of_window):
        cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
        cv2.imshow(name_of_window, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self, request):
        downloaded_result = []
        for weather in request:
            re_whitespace = re.compile(r'\s')
            whitespace = re.findall(re_whitespace, weather.weatherDesc)

            if whitespace:
                self.day_conditions = weather.weatherDesc.lower().split(' ')
            else:
                self.day_condition = weather.weatherDesc.lower()

            self.define_small_picture_to_add_and_gradient()
            self.make_gradient()

            self.l_img[self.y_offset:self.y_offset + self.s_img.shape[0],
            self.x_offset:self.x_offset + self.s_img.shape[1]] = self.s_img

            self.put_text(weather)

            weather.filename = f'data_for_weather/photos/weather_img/{weather.date}.jpg'
            cv2.imwrite(weather.filename, self.l_img)

            result = f"date={weather.date}," \
                     f"filename={weather.filename}"

            res_dict = dict(item.split('=') for item in result.split(','))
            downloaded_result.append(res_dict)
        return downloaded_result


class GetWeather(threading.Thread):
    def __init__(self, request_date):
        super().__init__()
        self.weather_from_site = None
        self.request_date = request_date
        self.response = None


class GetWeatherViaApi(GetWeather):
    def __init__(self, request_date):
        super().__init__(request_date=request_date)
        self.past_url = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx'
        self.present_url = 'http://api.worldweatheronline.com/premium/v1/weather.ashx'
        self.params = {'key': 'cb1161dab42a438f89581423201906',
                       'q': 'Moscow',
                       'format': 'json',
                       'date': self.request_date,
                       'lang': 'ru'}

    def run(self):
        try:
            today = datetime.date.today()
            two_weeks_after = today + datetime.timedelta(days=14)
            if self.request_date < today:
                self.response = requests.get(self.past_url, params=self.params)
                self.weather_from_site = self.response.json()
            elif today <= self.request_date <= two_weeks_after:
                self.response = requests.get(self.present_url, params=self.params)
                self.weather_from_site = self.response.json()
            else:
                print(f'{self.request_date} вне диапазона')
        except AttributeError:
            print('Данные не скачаны')

    def define_dict_to_db(self):
        if self.weather_from_site:
            result = f"date={self.weather_from_site['data']['weather'][0]['date']}," \
                     f"avgtempC={self.weather_from_site['data']['weather'][0]['avgtempC']}," \
                     f"windspeedKmph={self.weather_from_site['data']['weather'][0]['hourly'][0]['windspeedKmph']}," \
                     f"weatherDesc={self.weather_from_site['data']['weather'][0]['hourly'][0]['weatherDesc'][0]['value']}," \
                     f"precipMM={self.weather_from_site['data']['weather'][0]['hourly'][0]['precipMM']}," \
                     f"humidity={self.weather_from_site['data']['weather'][0]['hourly'][0]['humidity']}," \
                     f"pressure={self.weather_from_site['data']['weather'][0]['hourly'][0]['pressure']}"
            res_dict = dict(item.split('=') for item in result.split(','))
            return res_dict


class GetWeatherViaParsing(GetWeather):
    def run(self):
        try:
            today = datetime.date.today()
            one_week_after = today + datetime.timedelta(days=7)
            if self.request_date <= one_week_after:
                self.response = requests.get(f'https://darksky.net/details/55.7415,37.6156/{self.request_date}/ca12/en')
                self.weather_from_site = BeautifulSoup(self.response.text, features='html.parser')
            else:
                print(f'{self.request_date} вне диапазона')
        except (AttributeError, TypeError):
            print('Данные не скачаны')

    def define_dict_to_db(self):
        if self.weather_from_site:
            avgtempc = self.weather_from_site.find_all('span', {'class': 'num'})
            other_meanings = self.weather_from_site.find_all('span', {'class': 'num swip'})
            weather_desc = self.weather_from_site.find_all('p', {'id': 'summary'})

            result = f"date={self.request_date}," \
                     f"avgtempC={avgtempc[1].text}," \
                     f"windspeedKmph={other_meanings[2].text}," \
                     f"weatherDesc={weather_desc[0].text}," \
                     f"precipMM={other_meanings[0].text}," \
                     f"humidity={other_meanings[4].text}," \
                     f"pressure={other_meanings[3].text}"
            res_dict = dict(item.split('=') for item in result.split(','))
            return res_dict


class Poll:
    def __init__(self):
        self.result = None

    def print_from_result(self, result):
        self.result = result
        for weather in self.result:
            print(weather.date, weather.avgtempC, weather.windspeedKmph, weather.weatherDesc,
                  weather.precipMM,
                  weather.humidity, weather.pressure)

    @staticmethod
    def print_everything_from_db():
        print('---------------Weather---------------')
        for weather in Weather.select():
            print(weather.date, weather.avgtempC, weather.windspeedKmph, weather.weatherDesc,
                  weather.precipMM,
                  weather.humidity, weather.pressure)
        print('---------------Image---------------')
        for image in Image.select():
            print(image.date, image.filename)
        print('-----------------------------------')


class DatabaseUpdater:
    def __init__(self):
        self.dates_in_db = set()
        database_proxy.initialize(database)
        Weather.create_table()
        Image.create_table()

    @staticmethod
    def get_weather_or_none_from_duration(first_date_from_duration, second_date_from_duration):
        return Weather.get_or_none(
            (Weather.date >= first_date_from_duration) & (Weather.date <= second_date_from_duration))

    @staticmethod
    def get_weather_from_duration(first_date_from_duration, second_date_from_duration):
        return Weather.select().where(
            (Weather.date >= first_date_from_duration) & (Weather.date <= second_date_from_duration))

    @staticmethod
    def get_images_or_none_from_duration(first_date_from_duration, second_date_from_duration):
        return Image.get_or_none(
            (Image.date >= first_date_from_duration) & (Image.date <= second_date_from_duration))

    @staticmethod
    def get_images_or_none_for_one_day(first_date_from_duration):
        return Image.select().where(Image.date == first_date_from_duration)

    @staticmethod
    def get_images_from_duration(first_date_from_duration, second_date_from_duration):
        return Image.select().where(
            (Image.date >= first_date_from_duration) & (Image.date <= second_date_from_duration))

    def get_dates_from_db(self):
        for the_weather in Weather.select():
            self.dates_in_db.add(the_weather.date)
        return self.dates_in_db

    @staticmethod
    def save_dict_to_db(downloaded_result):
        Weather.insert_many(downloaded_result).execute()

    @staticmethod
    def save_data_to_db(data):
        Image.create(date=data['date'], filename=data['filename'])


class WeatherMaker:
    def __init__(self, database_updater, poller, image_maker):
        self.image_maker = image_maker
        self.poller = poller
        self.database_updater = database_updater
        self.list_of_options = ['1', '2', '3', '4', '5', '6']
        self.first_date_from_duration = None
        self.second_date_from_duration = None
        self.last_day = None
        self.length_of_input = None
        self.re_one_date = re.compile(r"[\d]{2}/[\d]{2}/[\d]{4}")
        self.re_two_dates = re.compile(r"[\d]{2}/[\d]{2}/[\d]{4}-[\d]{2}/[\d]{2}/[\d]{4}")

    @staticmethod
    def define_dates_to_download(dates_in_db, date, first_day, last_day):
        dates_to_download = []
        for day in range(first_day, last_day):
            date_to_append_in_db = date - datetime.timedelta(days=day)
            if date_to_append_in_db not in dates_in_db:
                dates_to_download.append(date_to_append_in_db)
            # else:
            #     print(f'{date_to_append_in_db} уже находится в БД')
        return dates_to_download

    @staticmethod
    def define_dates_to_make_card(dates_in_db, date, first_day, last_day):
        dates_to_make_card = []
        for day in range(first_day, last_day):
            date_to_make_card = date - datetime.timedelta(days=day)
            if date_to_make_card in dates_in_db:
                dates_to_make_card.append(date_to_make_card)
        return dates_to_make_card

    def check_input_number(self):
        while True:
            number = input("1.Добавление прогнозов за диапазон дат в базу данных\n"
                           "2.Получение прогнозов за диапазон дат из базы\n"
                           "3.Создание открыток из полученных прогнозов\n"
                           "4.Выведение полученных прогнозов на консоль\n"
                           "5.Выведение всех записей из всех таблиц\n"
                           "6.Выход\n"
                           "Введите желаемую цифру:")
            try:
                if number not in self.list_of_options:
                    print(f"Вы ввели цифру вне допустимого диапазона")
                else:
                    break
            except ValueError:
                print("Вы ввели некорректный номер")
        return number

    def check_date(self):
        while True:
            date_from_user = input(
                "Введите желаемую дату в формате 'dd/MM/YYYY' или диапазон дат в формате 'dd/MM/YYYY-dd/MM/YYYY':")
            try:

                if len(date_from_user) == 10:
                    re_date = self.re_one_date
                else:
                    re_date = self.re_two_dates
                date = re.findall(re_date, date_from_user)
                if date:
                    self.length_of_input = len(date[0])
                    if self.length_of_input == 10:
                        self.second_date_from_duration = datetime.datetime.strptime(date[0], '%d/%m/%Y').date()
                        self.last_day = 1
                        return
                    else:
                        self.first_date_from_duration = datetime.datetime.strptime(date[0].split('-')[0],
                                                                                   '%d/%m/%Y').date()
                        self.second_date_from_duration = datetime.datetime.strptime(
                            date[0].split('-')[1],
                            '%d/%m/%Y').date()
                        duration = self.second_date_from_duration - self.first_date_from_duration
                        if duration.days < 0:
                            raise ValueError("Вы ввели дату в некорректном формате, второе число не может быть меньше "
                                             "первого")
                        else:
                            self.last_day = duration.days + 1
                            return
                else:
                    raise ValueError("Вы ввели дату в некорректном формате")
            except ValueError as exc:
                print(exc)

    @staticmethod
    def download(dates_to_download):
        downloaded_result = []
        # full_weather = [GetWeatherViaParsing(day) for day in dates_to_download]
        full_weather = [GetWeatherViaApi(day) for day in dates_to_download]
        for one_weather in full_weather:
            one_weather.start()
        for one_weather in full_weather:
            one_weather.join()
            res_dict = one_weather.define_dict_to_db()
            downloaded_result.append(res_dict)
        return downloaded_result

    def make_cards(self):
        dates_in_db = self.database_updater.get_dates_from_db()
        dates_to_make_card = self.define_dates_to_make_card(dates_in_db,
                                                            date=self.second_date_from_duration,
                                                            first_day=0,
                                                            last_day=self.last_day)
        if dates_to_make_card:
            request = self.database_updater.get_weather_from_duration(self.first_date_from_duration,
                                                                      self.second_date_from_duration)
            result = self.image_maker.run(request)
            for data in result:
                request = self.database_updater.get_images_or_none_for_one_day(data['date'])
                if request:
                    print('данные уже есть в базе, повторно запись произведена не будет')
                else:
                    self.database_updater.save_data_to_db(data)
        else:
            print('В базе нет запрашиваемых данных')

    def get_weather(self, date, first_day, last_day):
        try:
            dates_in_db = self.database_updater.get_dates_from_db()
            dates_to_download = self.define_dates_to_download(dates_in_db, date=date, first_day=first_day,
                                                              last_day=last_day)
            downloaded_result = self.download(dates_to_download)
            self.database_updater.save_dict_to_db(downloaded_result)
        except TypeError:
            print('Данных для записи в БД нет')

    def get_existing_weather_from_db(self):
        if self.length_of_input == 10:
            self.first_date_from_duration = self.second_date_from_duration
        result = self.database_updater.get_weather_or_none_from_duration(self.first_date_from_duration,
                                                                         self.second_date_from_duration)
        if result:
            result = self.database_updater.get_weather_from_duration(self.first_date_from_duration,
                                                                     self.second_date_from_duration)
            self.poller.print_from_result(result)
        else:
            print('Данных для вывода нет')

    def show_existing_images_from_db(self):
        if self.length_of_input == 10:
            self.first_date_from_duration = self.second_date_from_duration
        result = self.database_updater.get_images_or_none_from_duration(self.first_date_from_duration,
                                                                        self.second_date_from_duration)
        if result:
            result = self.database_updater.get_images_from_duration(self.first_date_from_duration,
                                                                    self.second_date_from_duration)
            for image in result:
                photo_to_view = cv2.imread(image.filename)
                self.image_maker.view_image(photo_to_view, 'image')
        else:
            print('Картинок для вывода нет')

    def run(self):
        self.get_weather(date=datetime.date.today(), first_day=1, last_day=8)
        while True:
            number = self.check_input_number()
            if number == '1':
                self.check_date()
                self.get_weather(date=self.second_date_from_duration, first_day=0,
                                 last_day=self.last_day)
            if number == '2':
                self.check_date()
                self.get_existing_weather_from_db()
            if number == '3':
                self.check_date()
                self.make_cards()
            if number == '4':
                self.check_date()
                self.show_existing_images_from_db()
            if number == '5':
                self.poller.print_everything_from_db()
            if number == '6':
                break


if __name__ == '__main__':
    db = DatabaseUpdater()
    poll = Poll()
    im_maker = ImageMaker()
    weather_maker = WeatherMaker(db, poll, im_maker)
    weather_maker.run()
