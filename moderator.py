"""
"""

import os
import praw

from curator import main as curator_main
from vcjc_integration import main as vcjc_integration_main

VERSION = '0.1'
AUTHOR = 'Numerous-Macaroon224'
USER_AGENT = f'python:vcj_mod_bot:v{VERSION} (by /u/{AUTHOR})'

# Create a Reddit instance
reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    password=os.environ.get('REDDIT_PASSWORD'),
    user_agent=USER_AGENT,
    username=os.environ.get('REDDIT_USERNAME'),
)

if __name__ == '__main__':
    curator_main(reddit)
    vcjc_integration_main(reddit)
