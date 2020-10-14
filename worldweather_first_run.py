import requests


'''для регистрации устройства в worldweatheronline.com, чтобы потом можно было стягивать данные '''


login_url = 'https://www.worldweatheronline.com/developer/login.aspx'
data = {'__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': 'Hr026Uq6lm/VGK2c1OhOTDeO43CBu7RFhrmC9yJODXfDZtBpwa8c+7UvrWsI0JM8m19T6r/VCQE3QEMlfLNJAToUOL'
                       'p2faCtZrSGdhNWo23zLaJfEep+vUD4cMCtHlf+5CbnGxlnLeWjuHB8I7LJ2tUr0GLRIdbDa5RfbonEVHR/lif+Q5Oz'
                       'MDGrohTV20nTgYH508KKjhYpZre1q3SLgey3GiWmf9digKoB6guhitWu4xew6MXlBM5qxAmX5OzV+vJmSToCUosYT0'
                       '2Ngy31LyrJ04tv+3o/tYoEVa8ovichDlTVk7IhIht7yUqEbyckS62V0xOCpZXXI2qSolt7ie5+EPszDlqhTG6zBKb5'
                       'DeiqQmowGwRmb0IAwmni+FRRlL36ELGUaAKVOEjtvVPfJlF9vFu5FaEtq9ezfK/SEJfOESbfSNd/zmQgX66hU7aV/U'
                       'V4rtt9h81p6B2WYy6TvxWKUhN6t1RJMzpOWwvjanbc9N7w',
        '__VIEWSTATEGENERATOR': '1B284CD2',
        'ctl00$MainContentHolder$Login1$UserName': 'your_email',
        'ctl00$MainContentHolder$Login1$Password': 'your_password',
        'ctl00$MainContentHolder$Login1$RememberMe': 'on',
        'ctl00$MainContentHolder$Login1$LoginButton': 'Log'
        }

s = requests.post(login_url, data=data)
print(s.text)
