import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import re
from datetime import datetime
import json, random

f = open('config.json')
config = json.load(f)

def randomize_passes():
    return random.choice(config)

http_client = requests.Session()  # init script: create requests session

login_data = randomize_passes() # init script: randomize passes
username = login_data[0]
password = login_data[1]

def login(username, password):
    head = {'Content-Type' : 'application/x-www-form-urlencoded'}
    auth_info = {'login_ref': 'https://www.qrz.com/', 'username': username, 'password': password, '2fcode' : '', 'target': '/', 'flush': '1'} # use account without set location otherwise it crashes XDD, EFTEJEDEN, EFTEDWA, EFTETRZY, EFTECZTERY, EFTEOSIEM
    login_req = http_client.post('https://www.qrz.com/login', auth_info, head)

    return http_client

def logout():
    req = http_client.get('https://www.qrz.com/logout')
    soup = BeautifulSoup(req.text, 'html.parser')
    link = soup.find_all('a', {'class': 'btn btn-primary'})[0]['href']
    req = http_client.get(f'https://www.qrz.com{link}')
login(username, password) # init script: login into qrzcom

def prettify(text):
    return text.lower().replace(" ", "_").replace("?", "").replace("#", "")

def format_date(date, format):
    date = datetime.strptime(date, format)
    return date.isoformat()

def get_data(callsign):
    request = http_client.get(f'https://qrz.com/db/{callsign}')
    soup = BeautifulSoup(request.text, 'html.parser')

    try:
        name = " ".join(soup.find_all('span', {'style': 'color: black; font-weight: bold'})[0].getText().split())
    except:
        if 'Too many lookups' in request.text:
            return 418
        else:
            print('error')
            return 404
    
    data = {'name': name, 'callsign': callsign.upper()}

    table = soup.find('table', id="detbox")
    rows = []
    for i, row in enumerate(table.find_all('tr')):
        rows.append([el.text.strip() for el in row.find_all('td')])
    table_data = [x for x in rows if not isinstance(x, str)]    
    table_data.pop(0)
    table_data = [ele for ele in table_data if ele != []]

    geo = {}
    for el in table_data:
        if el[0].lower() in ("longitude", "latitude", "geo source", "grid_square"):
            geo[prettify(el[0])] = el[1]
        elif el[0].lower() == "othercallsigns":
            continue
        else:
            data[prettify(el[0])] = el[1]
    geo['longitude'] = float(geo['longitude'].split()[0])
    geo['latitude'] = float(geo['latitude'].split()[0])
    if data.get('nickname'):
        address = list(soup.find_all('p', {'class': 'm0'})[0].stripped_strings)[4:]
    else:
        address = list(soup.find_all('p', {'class': 'm0'})[0].stripped_strings)[2:]
    address = ', '.join(address)
    geo['address'] = address
    data['geo'] = geo

    for key in ("qsl_by_mail", "qsl_by_eqsl", "uses_lotw"):
        if key in data:
            data[key] = data[key][:3].strip()

    new_data = {}
    for i, (k, v) in enumerate(data.items()):
        try:
            if re.search("[a-zA-Z0-9]{1,3}[0-9][a-zA-Z0-9]{0,3}[a-zA-Z]", k):
                continue
            else:
                new_data[k] = v
        except:
            print("err")
    new_data['date_joined'] = format_date(new_data['date_joined'], '%Y-%m-%d %H:%M:%S')
    new_data['last_update'] = format_date(new_data['last_update'], '%Y-%m-%d %H:%M:%S')
    
    return new_data

app = Flask(__name__)

@app.route("/get_data")
def callsign_data():
    call = request.args.get('call', '')
    data = get_data(call)
    if data == 404:
        return {'code': 404, 'message': 'Callsign Not Found'}, 404
    elif data == 418:
        logout()
        login_data = randomize_passes()
        login(login_data[0], login_data[1])
        data = get_data(call)
        data['api_username'] = login_data[0]
        return data
    else:
        return get_data(call)