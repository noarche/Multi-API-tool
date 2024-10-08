import PySimpleGUI as sg
import requests
import json

sg.theme('DarkBlack')
sg.theme_background_color('black')
sg.theme_text_color('Red')
sg.theme_button_color(('Black', 'silver'))
sg.theme_element_background_color('black')
sg.theme_input_background_color('black')
sg.theme_input_text_color('limegreen')
sg.theme_text_element_background_color('black')

def get_ip():
    response = requests.get('https://api.ipify.org/?format=json')
    data = response.json()
    ip_address = data['ip']
    display_result(ip_address)

def reverse_zip(zip_code):
    base_url = 'https://ziptasticapi.com/'
    url = base_url + zip_code
    response = requests.get(url)
    try:
        data = response.json()
        state = data.get('state', 'N/A')
        city = data.get('city', 'N/A')
        result = f"State: {state}\nCity: {city}"
    except json.decoder.JSONDecodeError:
        result = response.text
    display_result(result)

def get_domain_info(domain_name):
    url = f"https://api.domainsdb.info/v1/domains/search?domain={domain_name}"
    response = requests.get(url)
    try:
        data = response.json()
        domain_list = []
        for item in data['domains']:
            domain = item.get('domain')
            if domain:
                domain_list.append(domain)
        if not domain_list:
            result = "No results found"
        else:
            result = "\n".join(domain_list)
    except json.decoder.JSONDecodeError:
        result = "No results found"
    display_result(result)

def get_lyrics(artist, song):
    url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
    response = requests.get(url)
    try:
        data = response.json()
        lyrics = data.get('lyrics', 'No lyrics found')
        lyrics = "\n".join([line for line in lyrics.split('\n') if line.strip()])
    except json.decoder.JSONDecodeError:
        lyrics = "Error fetching lyrics"
    display_result(lyrics)

def query_oogabooga_api(user_message):
    base_url = 'http://127.0.0.1:5000'
    api = OogaBoogaAPI(base_url)
    try:
        response_data = api.get_chat_completion(user_message)
        results = []
        for message in response_data.get("choices", []):
            results.append(message["message"]["content"])
        result = "\n".join(results)
    except Exception as e:
        result = f'Error: {e}'
    display_result(result)

class OogaBoogaAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def get_chat_completion(self, user_message, mode="instruct", instruction_template="Alpaca"):
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "mode": mode,
            "instruction_template": instruction_template
        }
        url = f'{self.base_url}/v1/chat/completions'
        response = requests.post(url, headers=self.headers, json=data, verify=False)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

def display_result(result):
    window['-TEXTBOX-'].update(result)

def get_worldbank_data(country_code):
    country_url = f'https://api.worldbank.org/v2/country/{country_code}'
    country_response = requests.get(country_url)
    if '<wb:message id="120" key="Invalid value">' in country_response.text:
        display_result('The provided parameter value is not valid.')
        return

    country_data = country_response.text
    name = extract_tag_value(country_data, 'wb:name')
    region = extract_tag_value(country_data, 'wb:region')
    income_level = extract_tag_value(country_data, 'wb:incomeLevel')
    lending_type = extract_tag_value(country_data, 'wb:lendingType')
    capital_city = extract_tag_value(country_data, 'wb:capitalCity')
    longitude = extract_tag_value(country_data, 'wb:longitude')
    latitude = extract_tag_value(country_data, 'wb:latitude')

    country_info = (
        f"Name: {name}\n"
        f"Region: {region}\n"
        f"Income Level: {income_level}\n"
        f"Lending Type: {lending_type}\n"
        f"Capital City: {capital_city}\n"
        f"Longitude: {longitude}\n"
        f"Latitude: {latitude}\n"
    )

    gdp_url = f'https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD'
    gdp_response = requests.get(gdp_url)
    gdp_data = gdp_response.text
    gdp_entries = extract_gdp_entries(gdp_data)

    result = country_info + '\nGDP\n' + gdp_entries
    display_result(result)

def extract_tag_value(data, tag):
    start_tag = f'<{tag}>'
    end_tag = f'</{tag}>'
    start = data.find(start_tag) + len(start_tag)
    end = data.find(end_tag)
    return data[start:end].strip()

def extract_gdp_entries(data):
    entries = []
    while True:
        entry = extract_next_gdp_entry(data)
        if not entry:
            break
        entries.append(entry)
        data = data[data.find('</wb:data>') + len('</wb:data>'):]
    return '\n'.join(entries)

def extract_next_gdp_entry(data):
    if '<wb:data>' not in data:
        return None
    start = data.find('<wb:data>') + len('<wb:data>')
    end = data.find('</wb:data>') + len('</wb:data>')
    entry_data = data[start:end]

    date = extract_tag_value(entry_data, 'wb:date')
    value = extract_tag_value(entry_data, 'wb:value')
    formatted_value, summary = format_gdp_value(value)

    return f'{date} | ${formatted_value} | {summary}'

def format_gdp_value(value):
    value = int(value)
    formatted_value = f'{value:,}'
    if value >= 1_000_000_000_000:
        summary = f'{value / 1_000_000_000_000:.2f} Trl'
    elif value >= 1_000_000_000:
        summary = f'{value / 1_000_000_000:.2f} Bln'
    else:
        summary = f'{value / 1_000_000:.2f} Mln'
    return formatted_value, summary

layout = [
    [sg.Text('Select API:')],
    [sg.Combo(['Get My IP', 'Reverse ZipCode Lookup', 'Domain Name Check', 'Lyrics Lookup', 'Query LLM', 'WorldBank'], size=(30, 1), key='-API_SELECTION-')],
    [sg.Button('Submit', size=(10, 1))],
    [sg.Multiline(size=(80, 30), key='-TEXTBOX-', autoscroll=True, disabled=True)],
    [sg.InputText('', size=(80, 1), key='-USER_INPUT-')]
]

window = sg.Window('API Data Fetcher', layout, finalize=True, resizable=False, alpha_channel=0.9)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:  
        break
    elif event == 'Submit':
        selected_api = values['-API_SELECTION-']
        if selected_api == 'Get My IP':
            get_ip()
        elif selected_api == 'Reverse ZipCode Lookup':
            zip_code = sg.popup_get_text('Enter Zip Code')
            if zip_code:
                reverse_zip(zip_code)
        elif selected_api == 'Domain Name Check':
            domain_name = sg.popup_get_text('Enter Domain Name')
            if domain_name:
                get_domain_info(domain_name)
        elif selected_api == 'Lyrics Lookup':
            artist = sg.popup_get_text('Enter Artist Name')
            song = sg.popup_get_text('Enter Song Title')
            if artist and song:
                get_lyrics(artist, song)
        elif selected_api == 'Query LLM':
            user_message = values['-USER_INPUT-']
            if user_message:
                query_oogabooga_api(user_message)
                window['-USER_INPUT-'].update('')  # Clear input after querying API
        elif selected_api == 'WorldBank':
            country_code = sg.popup_get_text('Enter 3-letter Country Code')
            if country_code:
                get_worldbank_data(country_code)

window.close()
