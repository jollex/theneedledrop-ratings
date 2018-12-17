import csv
import re

from googleapiclient.discovery import build

import config


client = build('theneedledrop_ratings', 'v3', developerKey=config.API_KEY)


def get_video_ids():
    next_page_token = None

    video_ids = []
    while True:
        kwargs = dict(
            part='snippet',
            channelId='UCt7fwAhXDy3oNFTAzF2o8Pw',
            type='video',
            maxResults=50
        )
        if next_page_token is not None:
            kwargs['pageToken'] = next_page_token

        response = client.search().list(**kwargs).execute()

        for video in response['items']:
            video_ids.append(video['id']['videoId'])

        if 'nextPageToken' not in response:
            break
        else:
            next_page_token = response['nextPageToken']

    with open('video_ids.txt', 'w') as f:
        f.write('\n'.join(video_ids))
    print(len(video_ids))


def get_ratings():
    with open('video_ids.txt', 'r') as f:
        video_ids = f.read().splitlines()
    groups = chunks(video_ids, 10)

    videos = []
    for group in groups:
        kwargs = dict(
            part='snippet',
            id=','.join(group)
        )
        response = client.videos().list(**kwargs).execute()

        for video in response['items']:
            snippet = video['snippet']
            result = re.search('\s(\d{1,2})/10(\s|$)', snippet['description'])
            if result is not None:
                print(snippet['title'])
                print(result.group(1))
                videos.append({
                    'title': snippet['title'],
                    'dt': snippet['publishedAt'],
                    'rating': result.group(1)
                })

    with open('ratings.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=videos[0].keys())
        writer.writerows(videos)
    print(len(videos))


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == '__main__':
    get_ratings()
