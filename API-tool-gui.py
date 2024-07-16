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

layout = [
    [sg.Button('Get My IP', size=(19, 1), key='-GET_IP-')],
    [sg.Button('Reverse ZipCode Lookup', size=(19, 1), key='-REVERSE_ZIP-')],
    [sg.Button('Domain Name Check', size=(19, 1), key='-DOMAIN_CHECK-')],
    [sg.Button('Lyrics Lookup', size=(19, 1), key='-LYRICS_LOOKUP-')],
    [sg.Button('Query LLM', size=(19, 1), key='-QUERY_OOGA-')],
    [sg.Button('Help', size=(19, 1), key='-HELP-')],
    [sg.Multiline(size=(80, 30), key='-TEXTBOX-', autoscroll=True, disabled=True, enable_events=True)],
    [sg.InputText('', size=(80, 1), key='-USER_INPUT-')]
]

window = sg.Window('API Data Fetcher', layout, finalize=True, resizable=False, alpha_channel=0.9)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:  
        break
    elif event == '-GET_IP-':
        get_ip()
    elif event == '-REVERSE_ZIP-':
        zip_code = sg.popup_get_text('Enter Zip Code')
        if zip_code:
            reverse_zip(zip_code)
    elif event == '-DOMAIN_CHECK-':
        domain_name = sg.popup_get_text('Enter Domain Name')
        if domain_name:
            get_domain_info(domain_name)
    elif event == '-LYRICS_LOOKUP-':
        artist = sg.popup_get_text('Enter Artist Name')
        song = sg.popup_get_text('Enter Song Title')
        if artist and song:
            get_lyrics(artist, song)
    elif event == '-QUERY_OOGA-':
        user_message = values['-USER_INPUT-']
        if user_message:
            query_oogabooga_api(user_message)
            window['-USER_INPUT-'].update('')  # Clear the input box after querying the API
    elif event == '-HELP-':
        help_info = """

                 +-+-+ +-+-+-+-+-+-+ +-+-+-+ +-+-+-+-+-+-+-+-+-+
                 | My Simple API Multi Tool - Alpha Alpha v0.0 |
                 +-+-+ +-+-+-+-+-+-+ +-+-+-+ +-+-+-+-+-+-+-+-+-+
                     _        
                    [|\|oarche 
          
        

        Get my IP:
        Displays user's public WAN gateway IP address.

        Zipcode lookup:
        Returns City and state tied to zipcode.

        Domain lookup: 
        Enter 'facebook' not 'facebook.com'
        Returns every domain with 'facebook' that isn't 'facebook.com' 

        Lyrics Lookup:
        Displays complete lyrics to an artist+song.
        
        Query LLM:
        Ask LLM using oogabooga api. Uses localhost by default. 
        
         More APIs will be added in the future.
         For Updates & Information visit
         
         https://github.com/noarche/Multi-API-tool 
        
        """
        display_result(help_info)

window.close()

