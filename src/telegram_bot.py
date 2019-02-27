#!/usr/bin/env python
# -*- coding: utf-8 -*-
import html
import json
import logging
import sqlite3
from datetime import datetime
from time import sleep
import os

import praw
import telegram

import config
import utils
from kill_handler import KillHandler

logging.basicConfig(level=logging.INFO)


# Read the file with latest submissions
def main():
    logging.info("Starting main")
    with open(os.path.join('..', 'cfg-tlgrm.json'), 'r', encoding='utf-8') as config_file:
        config_data = json.load(config_file)
        TOKEN = config_data['TOKEN']
        SUBREDDIT = config_data['SUBREDDIT']
        CHANNEL = config_data['CHANNEL']
        DBFILE = config_data['DBFILE']

    logging.info("Setting up Reddit connection")
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT)
    reddit.read_only = True
    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()
    subreddit = reddit.subreddit(SUBREDDIT)

    killhandler = KillHandler()

    logging.info("Setting up database")
    conn = sqlite3.connect(DBFILE)
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id)')
    conn.commit()

    logging.info("Setting up Telegram connection")
    tbot = telegram.Bot(token=TOKEN)
    try:
        tbot.get_me()
    except telegram.error.TelegramError as e_teleg:
        logging.error(e_teleg)
        logging.critical("Telegram error!")
        exit()

    for submission in subreddit.stream.submissions(pause_after=6):
        if submission:
            c = conn.cursor()
            c.execute('SELECT * FROM posts WHERE id=?', (submission.id, ))
            if not c.fetchone():
                link = 'https://redd.it/{id}'.format(id=submission.id)
                title = html.escape(submission.title or '')
                message_template = '<a href=\'{}\'>{}</a>'.format(link, title)
                logging.info('Posting %s', link)
                tbot.sendMessage(
                    chat_id=CHANNEL, parse_mode=telegram.ParseMode.HTML, text=message_template)
                conn.execute('INSERT INTO posts (id) values (?)', (submission.id, ))
                conn.commit()
            c.close()
        if killhandler.killed:
            logging.info("Termination signal received - exiting")
            break
    conn.close()

if __name__ == "__main__":
    utils.keep_up(main)
