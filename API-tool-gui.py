import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import requests
import json

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("API Data Fetcher")

        self.get_ip_button = tk.Button(self, text="Get My IP", command=self.get_ip)
        self.get_ip_button.pack()

        self.reverse_zip_button = tk.Button(self, text="Reverse ZipCode Lookup", command=self.get_zip)
        self.reverse_zip_button.pack()

        self.domain_name_check_button = tk.Button(self, text="Domain Name Check", command=self.check_domain)
        self.domain_name_check_button.pack()

        self.lyrics_lookup_button = tk.Button(self, text="Lyrics Lookup", command=self.lyrics_lookup)
        self.lyrics_lookup_button.pack()

        self.help_button = tk.Button(self, text="Help", command=self.show_help)
        self.help_button.pack()

    def get_ip(self):
        response = requests.get('https://api.ipify.org/?format=json')
        data = response.json()
        ip_address = data['ip']
        self.display_result(ip_address)

    def get_zip(self):
        zip_code = simpledialog.askstring("Input", "Enter Zip Code")
        if zip_code:
            self.reverse_zip(zip_code)

    def reverse_zip(self, zip_code):
        base_url = 'https://ziptasticapi.com/'
        if '[SSAP]' in base_url:
            url = base_url.replace('[SSAP]', zip_code)
        else:
            url = base_url + zip_code
        response = requests.get(url)
        try:
            data = response.json()
            state = data.get('state', 'N/A')
            city = data.get('city', 'N/A')
            result = f"State: {state}\nCity: {city}"
        except json.decoder.JSONDecodeError:
            result = response.text
        self.display_result(result)

    def check_domain(self):
        domain_name = simpledialog.askstring("Input", "Enter Domain Name")
        if domain_name:
            self.get_domain_info(domain_name)

    def get_domain_info(self, domain_name):
        url = f"https://api.domainsdb.info/v1/domains/search?domain={domain_name}"
        response = requests.get(url)
        try:
            data = response.json()
            domain_list = []
            for item in data['domains']:
                domain = item.get('domain')
                if domain:
                    domain_list.append(domain)
            result = "\n".join(domain_list)
        except json.decoder.JSONDecodeError:
            result = response.text
        self.display_result(result)

    def lyrics_lookup(self):
        artist, song = self.get_artist_and_song()
        if artist and song:
            self.get_lyrics(artist, song)

    def get_artist_and_song(self):
        dialog = tk.Toplevel(self)
        dialog.title("Enter Artist and Song")

        tk.Label(dialog, text="Artist Name:").pack(pady=5)
        artist_entry = tk.Entry(dialog)
        artist_entry.pack(pady=5)

        tk.Label(dialog, text="Song Title:").pack(pady=5)
        song_entry = tk.Entry(dialog)
        song_entry.pack(pady=5)

        def on_ok():
            dialog.artist = artist_entry.get()
            dialog.song = song_entry.get()
            dialog.destroy()

        ok_button = tk.Button(dialog, text="OK", command=on_ok)
        ok_button.pack(pady=5)

        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

        return dialog.artist, dialog.song

    def get_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
        response = requests.get(url)
        try:
            data = response.json()
            lyrics = data.get('lyrics', 'No lyrics found')
        except json.decoder.JSONDecodeError:
            lyrics = "Error fetching lyrics"
        self.display_lyrics(lyrics)

    def display_lyrics(self, lyrics):
        lyrics_window = tk.Toplevel(self)
        lyrics_window.title("Lyrics")

        text_box = scrolledtext.ScrolledText(lyrics_window, wrap=tk.WORD, width=60, height=50, bg='black', fg='lime')
        text_box.insert(tk.END, lyrics)
        text_box.pack()

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(lyrics)
            messagebox.showinfo("Copied", "Lyrics copied to clipboard")

        copy_button = tk.Button(lyrics_window, text="Copy to Clipboard", command=copy_to_clipboard)
        copy_button.pack()

    def show_help(self):
        help_info = "My Simple API Tool. \nMore APIs will be added in the future.\nVisit\n https://github.com/noarche/Multi-API-tool \nfor more information and updates. \n\nGet my IP\nDisplays users public WAN gateway IP address.\n\nZipcode lookup:\nReturns City and state tied to zipcode.\n\nDomain lookup: \nEnter 'facebook' not 'facebook.com' \nReturns every domain with 'facebook' that isnt 'facebook.com' \n\nLyrics Lookup\nDisplays complete lyrics to a artist+song."
        self.display_result(help_info)

    def display_result(self, result):
        result_window = tk.Toplevel(self)
        result_label = tk.Label(result_window, text=result)
        result_label.pack()

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
