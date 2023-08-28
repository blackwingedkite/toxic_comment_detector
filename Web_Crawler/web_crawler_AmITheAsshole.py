import requests
import pandas as pd
import os

auth = requests.auth.HTTPBasicAuth(
    'dC0Sw4B11zAslC_80akklw', 'XOfH0HrCPGASRYJNH9zryEusZOh86w')

data = {'grant_type': 'password',
        'username': 'christinahatespeople',
        'password': 'ilovepeople'}

headers = {'User-Agent': 'MyBot/0.0.1'}

res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

# convert response to JSON and pull access_token value
TOKEN = res.json()['access_token']

# add authorization to our headers dictionary
headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# while the token is valid (~2 hours) we just add headers=headers to our requests
requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

df = pd.DataFrame()  # initialize dataframe

# loop through 50 pages of trending posts in /r/AmITheAsshole
for page in range(1):
    # make a request for the trending posts in /r/AmITheAsshole
    url = f"https://oauth.reddit.com/r/AmITheAsshole/hot?page={page+1}"
    res = requests.get(url, headers=headers)

    postList = res.json()['data']['children']
    # loop through each post retrieved from GET request
    for post in postList:
        new_row = pd.DataFrame({
            'subreddit': ['AmITheAsshole'],
            'title': [post['data']['title']],
            'selftext': [post['data']['selftext']],
            'upvote_ratio': [post['data']['upvote_ratio']],
            'ups': [post['data']['ups']],
            'downs': [post['data']['downs']],
            'score': [post['data']['score']]
        })
        df = pd.concat([df, new_row], ignore_index=True)

        postId = post['data']['id']
        sort = "old"
        threaded = "false"
        res = requests.get(
            f"https://oauth.reddit.com/comments/{postId}?sort={sort}&threaded={threaded}", headers=headers)
        commentList = res.json()[1]['data']['children']

        # loop through each comment retrieved from GET request
        for comment in commentList:
            # append relevant data to dataframe
            new_comment_row = pd.DataFrame({
                'comment_author': [comment['data'].get('author', None)],
                'comment_body': [comment['data'].get('body', None)]
            })
            df = pd.concat([df, new_comment_row], ignore_index=True)

# save dataframe to Excel
df.to_excel(os.path.join(os.getcwd(), 'reddit_comments_AmITheAsshole.xlsx'), index=False)
