import requests, json, csv, re
from bs4 import BeautifulSoup
from secrets import access_token
from collections import Counter
import os

api_root = 'https://api.genius.com/'
root = 'https://genius.com'
headers = {"Authorization": "Bearer " + access_token, 
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}

def scrapeLyrics(url):
    for i in range(10): # loop needed as sometimes the result is not found
        source = requests.get(url, headers=headers)
        soup = BeautifulSoup(source.text, 'lxml')
        result = soup.find("div", class_="lyrics")
        if result:
            break
    try:
        lyrics = result.get_text()
        print('Info Found')
        return lyrics.strip("\n")
    except AttributeError as e:
        print('****Info Not Found****')

def saveLyrics(artist, title, lyrics, word_count):
    if os.path.isdir(os.getcwd() + '\\' + 'saved_lyrics' + '\\' + artist.replace(' ', '')):
        pass
    elif os.path.isdir(os.getcwd() + '\\' + 'saved_lyrics'):
        path = os.getcwd() + '\\' + 'saved_lyrics'
        os.mkdir(path  + '\\' + artist.replace(' ', ''))
    else:
        path = os.getcwd() + '\\' 'saved_lyrics'
        os.mkdir(path)
        path = os.getcwd() + '\\' 'saved_lyrics' + '\\' + artist.replace(' ', '')
        os.mkdir(path)
    txtfile = open(os.getcwd() + '\\' + 'saved_lyrics' + '\\' + artist.replace(' ', '') + '\\' + title.replace(' ', '') + '.txt', 'w')
    txtfile.write(title + ' by ' + artist + '\n')
    txtfile.write('Word Count: ' + str(word_count) + '\n')
    txtfile.write(lyrics)
    txtfile.close()

def geniusSearch(query, save_lyrics=True):
    search_url = api_root + 'search?q=' + query
    response = requests.get(search_url, headers=headers)
    all_words = {}
    json_data = json.loads(response.content)['response']
    artist = json_data['hits'][0]['result']['primary_artist']['name']
    csvfile = open(artist.replace(' ', '') + '.csv', 'w', newline='')
    csv.writer(csvfile).writerow(['Artist', 'Title', 'Word Count'])
    for i in range(5):
        song_name = json_data['hits'][i]['result']['title']
        song_path = json_data['hits'][i]['result']['api_path']
        print(f'Getting Info for {song_name} by {artist}')

        lyrics = scrapeLyrics(root + song_path)
        lyrics = re.sub('(\[.*?\])*', '', lyrics)           # Remove Verse Titles
        # lyrics = re.sub('\n{2}', '\n', lyrics)            # Remove gaps between verses
        lyrics = re.sub('[^\w\s]', '', lyrics)              # Remove any non-alphanumeric items

        for word in lyrics.split():
            if word in all_words.keys():
                all_words[word] += 1
            else:
                all_words[word] = 1

        if save_lyrics == True:                             # Writes lyrics to text file
            saveLyrics(artist, song_name, lyrics, len(all_words))

        # count = Counter(all_words)                        # May be useful
        # for key, value in count.most_common(5):  
        #     print(f'{key}: {value}')
        
        csv.writer(csvfile).writerow([artist, song_name, len(all_words)])
        all_words.clear()

    csvfile.close()
    print('Search Complete')

query = input('Enter Artist: ')
geniusSearch(query)