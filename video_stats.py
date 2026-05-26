import requests
import json
import os
from dotenv import load_dotenv
from datetime import date
load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
MaxResults = 50

def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        channel_playlistId = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        print(channel_playlistId)
        return channel_playlistId

    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(playlistId):
    video_ids = []
    pageToken = None
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlistId}&maxResults={MaxResults}&key={API_KEY}"

    try:
        while True:
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_ids.append(item['contentDetails']['videoId'])

            pageToken = data.get('nextPageToken')
            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e
    

def batch_video_ids(video_id_lst, batch_size):
    for vedio_id in range(0, len(video_id_lst), batch_size):
        yield video_id_lst[vedio_id:vedio_id + batch_size]


def extract_video_data(vedio_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for vedio_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[vedio_id:vedio_id + batch_size]

    try:
        for batch in batch_list(vedio_ids, MaxResults):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video_id": video_id,
                    "title": snippet.get('title'),
                    "publishedAt": snippet.get('publishedAt'),
                    "duration": contentDetails.get('duration'),
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None)
                }
                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"
    os.makedirs("./data", exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    vedio_data = extract_video_data(video_ids)
    save_to_json(vedio_data)
