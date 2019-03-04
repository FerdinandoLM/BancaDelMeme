#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import html
import json
import logging
import os
import sqlite3
import time
from collections import namedtuple
from threading import Thread

import praw
import telegram
from telegram.ext import CommandHandler, Updater

import config
import utils
import message

logging.basicConfig(level=logging.INFO)


class TBot():
    def __init__(self):
        logging.info("Starting main")
        with open(os.path.join('..', 'cfg-tlgrm.json'), 'r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)
            token = config_data['TOKEN']
            subreddit = config_data['SUBREDDIT']
            self.tchannel = config_data['CHANNEL']
            self.dbfile = config_data['DBFILE']
            dbmaster = config_data['DBMASTER']
        self.conn = None
        self.mconn = None
        self._init_reddit(subreddit)
        self._init_mconn(dbmaster)
        self._init_tbot(token)
        self.halt = False

    def _init_reddit(self, subreddit):
        logging.info("Setting up Reddit connection")
        reddit = praw.Reddit(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            user_agent=config.USER_AGENT)
        reddit.read_only = True
        # We will test our reddit connection here
        if not utils.test_reddit_connection(reddit):
            exit()
        self.subreddit = reddit.subreddit(subreddit)

    def _init_conn(self):
        logging.info("Setting up local database")
        if self.conn:
            self.conn.close()
        conn = sqlite3.connect(self.dbfile)
        conn.execute('CREATE TABLE IF NOT EXISTS posts (id)')
        conn.commit()
        self.conn = conn

    def _init_mconn(self, dbfile):
        logging.info("Setting up master database")
        if self.mconn:
            self.mconn.close()
        conn = sqlite3.connect(dbfile, check_same_thread=False)
        conn.execute('PRAGMA query_only = 1')
        self.mconn = conn

    def _init_tbot(self, token):
        logging.info("Setting up Telegram connection")
        updater = Updater(token=token)
        try:
            updater.bot.get_me()
        except telegram.error.TelegramError as e_teleg:
            logging.error(e_teleg)
            logging.critical("Telegram error!")
            exit()
        self.tbot = updater.bot
        self.tupdater = updater

    def check_reddit(self):
        while True:
            try:
                self._init_conn()
                logging.info("Starting monitoring subreddit")
                for submission in self.subreddit.stream.submissions(pause_after=6):
                    if submission:
                        c = self.conn.cursor()
                        c.execute('SELECT * FROM posts WHERE id=?', (submission.id, ))
                        if not c.fetchone():
                            link = 'https://redd.it/{id}'.format(id=submission.id)
                            title = html.escape(submission.title or '')
                            message_template = '<a href=\'{}\'>{}</a>'.format(link, title)
                            logging.info('Posting %s', link)
                            self.tbot.sendMessage(
                                chat_id=self.tchannel,
                                parse_mode=telegram.ParseMode.HTML,
                                text=message_template)
                            self.conn.execute('INSERT INTO posts (id) values (?)', (submission.id, ))
                            self.conn.commit()
                        c.close()
                    if self.halt:
                        logging.info("Stopped subreddit monitoring")
                        return
            except Exception:
                logging.exception('Error during check_reddit')

    def handler_start(self, _, update):
        """ (Telegram command)
        Send a message when the command /start is issued.
        @:param bot: an object that represents a Telegram Bot.
        @:param update: an object that represents an incoming update.
        """
        update.message.reply_markdown("""Comprendo i seguenti comandi:

`/saldo` _user_
`/attivi` _user_
`/mercato`
`/top`""")

    def _get_user(self, update):
        args = update.message.text_markdown.split(" ")[1:]
        if not args or not args[0]:
            update.message.reply_text("Dopo il comando devi specificare l\'utente")
            return None
        return args[0].strip()

    def handler_saldo(self, _, update):
        """ (Telegram command)
        Send a message when the command /start is issued.
        @:param bot: an object that represents a Telegram Bot.
        @:param update: an object that represents an incoming update.
        """
        user = self._get_user(update)
        if not user:
            return
        c = self.mconn.cursor()
        c.execute('SELECT name, balance from Investors where UPPER(name) = ?', (user.upper(), ))
        row = c.fetchone()
        if not row:
            c.close()
            update.message.reply_text("Utente non trovato")
            return
        update.message.reply_markdown("L'investitore {} possiete {:d} Mem€".format(row[0], row[1]))
        c.close()

    def handler_attivi(self, _, update):
        """ (Telegram command)
        Send a message when the command /start is issued.
        @:param bot: an object that represents a Telegram Bot.
        @:param update: an object that represents an incoming update.
        """
        user = self._get_user(update)
        if not user:
            return
        c = self.mconn.cursor()
        c.execute(
            'SELECT time, post, amount, upvotes from Investments where UPPER(name) = ? and done == 0 order by time',
            (user.upper(), ))
        rows = c.fetchall()
        if not rows:
            update.message.reply_text("Nessun investimento trovato")
            c.close()
            return
        text = "Trovati {:d} investimenti attivi:\n\n".format(len(rows))
        for i, row in enumerate(rows):
            seconds_remaining = row[0] + config.INVESTMENT_DURATION - time.time()
            if seconds_remaining > 0:
                td = datetime.timedelta(seconds=seconds_remaining)
                remaining_string = str(td).split(".")[0] + " rimanenti"
            else:
                remaining_string = "in elaborazione"
            text += "[#{i:d}](https://www.reddit.com/r/BancaDelMeme/comments/{post}): {amount:,d} Mem€ @ {upvotes:d} upvotes ({remaining})\n\n".format(
                i=i, post=row[1], amount=row[2], remaining=remaining_string, upvotes=row[3])
        update.message.reply_markdown(text.strip())
        c.close()

    def handler_mercato(self, _, update):
        """ (Telegram command)
        Send a message when the command /start is issued.
        @:param bot: an object that represents a Telegram Bot.
        @:param update: an object that represents an incoming update.
        """
        c = self.mconn.cursor()
        c.execute('select COALESCE(sum(balance), 0) from Investors')
        row = c.fetchone()
        total = row[0]
        c.close()
        c = self.mconn.cursor()
        c.execute('select COALESCE(sum(amount), 0), count(id) from Investments where done != 1')
        row = c.fetchone()
        invested, active = row[0], row[1]
        c.close()
        update.message.reply_markdown(message.modify_market(active, total, invested))

    def handler_top(self, _, update):
        """ (Telegram command)
        Send a message when the command /start is issued.
        @:param bot: an object that represents a Telegram Bot.
        @:param update: an object that represents an incoming update.
        """
        c = self.mconn.cursor()
        c.execute("""
                with tops as (
                    select Investors.name, balance + COALESCE(sum(amount), 0) as networth
                    from Investors
                    left OUTER join Investments on Investors.name = Investments.name and done == 0
                    group by Investors.name)
                select * from tops order by networth desc limit 10""")
        leaders = []
        Investors = namedtuple('Investors', ['name', 'networth'])
        for row in c.fetchall():
            leaders.append(Investors(row[0], row[1]))
        update.message.reply_text(message.modify_top(leaders).replace('\n\n', '\n'))

    def main(self):
        dp = self.tupdater.dispatcher
        dp.add_handler(CommandHandler("start", self.handler_start))
        dp.add_handler(CommandHandler("saldo", self.handler_saldo))
        dp.add_handler(CommandHandler("attivi", self.handler_attivi))
        dp.add_handler(CommandHandler("mercato", self.handler_mercato))
        dp.add_handler(CommandHandler("top", self.handler_top))

        check_reddit_thread = Thread(target=self.check_reddit, args=[])
        check_reddit_thread.start()
        logging.info("Starting Telegram bot interface")
        self.tupdater.start_polling()
        self.tupdater.idle()
        logging.info("Halting subreddit monitoring, please wait...")
        self.halt = True


if __name__ == "__main__":
    TBOT = TBot()
    utils.keep_up(TBOT.main)
