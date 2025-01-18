import pandas as pd
import re
import requests
from dotenv import load_dotenv
import os

# Define the path to the subfolder
folder_path = './100Hits2021'
base_url = 'https://api.musixmatch.com/ws/1.1/'

# Load environment variables from the .env file
load_dotenv()
api_key = os.getenv('API_KEY')

# Function to search for a track by artist and song title
def search_track(artist, song_title):
    endpoint = 'track.search'
    url = f'{base_url}{endpoint}'
    params = {
        'apikey': api_key,
        'q_artist': artist,
        'q_track': song_title,
        'page_size': 1,
        'page': 1,
        's_track_rating': 'desc'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            track_list = data['message']['body']['track_list']
            if track_list:
                track = track_list[0]['track']
                track_id = track['track_id']
                if track['primary_genres']['music_genre_list']:
                    music_genre_name = track['primary_genres']['music_genre_list'][0]['music_genre']['music_genre_name_extended']
                else:
                    music_genre_name = 'Unknown'
                return track_id, music_genre_name
            else:
                print(f"No tracks found for {artist} - {song_title}.")
                return None, 'Unknown'
        except (KeyError, TypeError) as e:
            print(f"Error extracting track information: {e}")
            return None, 'Unknown'
    else:
        print(f'Error: {response.status_code} for {artist} - {song_title}')
        return None, 'Unknown'

# Function to get lyrics for a track ID
def get_lyrics(track_id):
    endpoint = 'track.lyrics.get'
    url = f'{base_url}{endpoint}'
    params = {
        'apikey': api_key,
        'track_id': track_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            lyrics = data['message']['body']['lyrics']['lyrics_body']
            # Remove the last four lines
            lyrics_lines = lyrics.split('\n')
            if len(lyrics_lines) >= 4:
                lyrics = '\n'.join(lyrics_lines[:-4])
            return lyrics
        except (KeyError, TypeError) as e:
            print(f"Error extracting lyrics: {e}")
            return None
    else:
        print(f'Error: {response.status_code}')
        return None

# List to hold the song information
songs_info = []

# Iterate over the files in the folder
for filename in os.listdir(folder_path):
    match = re.match(r'(\d+)\. (.+) - (.+)\.mp3', filename)
    if match:
        number = match.group(1)
        artist = match.group(2)
        song_name = match.group(3)
        track_id, genre = search_track(artist, song_name)
        if track_id:
            lyrics = get_lyrics(track_id)
            if lyrics:
                lyrics_filename = "100Hits2021_lyrics30percent/"+(f"{number}_{artist}_{song_name}.txt").replace(" ", "_").replace("/", "-")
                with open(lyrics_filename, 'w', encoding='utf-8') as f:
                    f.write(lyrics)
        songs_info.append((number, artist, song_name, track_id, genre))

# Create a DataFrame
df = pd.DataFrame(songs_info, columns=['Number', 'Artist', 'Song Name', 'Track ID', 'Genre'])

# Save the DataFrame to a CSV file
df.to_csv('songs_info_with_ids_and_genres.csv', index=False)

print("Data saved to songs_info_with_ids_and_genres.csv")