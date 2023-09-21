import requests
import configparser
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('config.ini')

url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['AUTH-ROUTES']['login']

with requests.Session() as s:
    res = s.get("https://durel.ims.uni-stuttgart.de/login")
    login = BeautifulSoup(res._content, 'html.parser')
    p = s.post("https://durel.ims.uni-stuttgart.de/login", data={'username': 'PaulineSander', 'password': 'Ju7pZgmSwCzFjUv'})
    r = s.post(url, json={
        'username': config['CREDENTIALS']['username'],
        'password': config['CREDENTIALS']['password']})
    print(r.content)

if r.status_code == 200:
    # Save token to config file 
    config['CREDENTIALS']['authentication_token'] = r.json()['jwt']
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print("process succeeds, jwt is written in the config file")
else:
    print('Error: ' + str(r.status_code))

