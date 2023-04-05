import requests
import configparser

config = configparser.ConfigParser()
config.read('config_local.ini')

url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['AUTH-ROUTES']['login']

r = requests.post(url, json={
    'username': config['CREDENTIALS']['username'],
    'password': config['CREDENTIALS']['password']
})

if r.status_code == 200:
    # Save token to config file 
    config['CREDENTIALS']['authentication_token'] = r.json()['jwt']
    with open('config_local.ini', 'w') as configfile:
        config.write(configfile)
    print("process succeeds, jwt is written in the config file")
else:
    print('Error: ' + str(r.status_code))