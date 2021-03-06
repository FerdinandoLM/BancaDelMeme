"""
datetime gives us access to current month
traceback flushes errors
logging is the general stdout for us

prawcore has the list of praw exceptions
"""
import datetime
import traceback
import logging
import time

import prawcore

import config

logging.basicConfig(level=logging.INFO)

DEPLOY_DATE = time.strftime("%c")
BALANCE_CAP = 1000 * 1000 * 1000 * 1000 * 1000 * 1000  # One quintillion MemeCoins


def investment_duration_string(duration):
    """
    We may change the investment duration in the future
    and this function allows us to have agile strings
    depending on the duration from .env
    """
    hours = duration // 3600
    duration %= 3600
    minutes = duration // 60
    duration %= 60

    inv_string = ""
    if hours:
        inv_string += f"{hours} or"
        if hours > 1:
            inv_string += "e"
        else:
            inv_string += "a"
        inv_string += " "
    if minutes:
        inv_string += f"{minutes} minut"
        if minutes > 1:
            inv_string += "i"
        else:
            inv_string += "o"
        inv_string += " "
    if duration:
        inv_string += f"{duration} second"
        if duration > 1:
            inv_string += "i"
        else:
            inv_string += "o"
        inv_string += " "

    return inv_string


def upvote_string():
    """
    We can make some funny replacements of upvotes
    depending on what month it is
    """
    return {
        10: "upvotes",
    }.get(datetime.date.today().month, "upvotes")


def test_reddit_connection(reddit):
    """
    This function just tests connection to reddit
    Many things can happen:
     - Wrong credentials
     - Absolutly garbage credentials
     - No internet

    This function helps us to quickly check if we are online
    Return true on success and false on failure
    """
    try:
        reddit.user.me()
    except prawcore.exceptions.OAuthException as e_creds:
        traceback.print_exc()
        logging.error(e_creds)
        logging.critical("Invalid login credentials. Check your .env!")
        logging.critical("Fatal error. Cannot continue or fix the problem. Bailing out...")
        return False
    except prawcore.exceptions.ResponseException as http_error:
        traceback.print_exc()
        logging.error(http_error)
        logging.critical("Received 401 HTTP response. Try checking your .env!")
        logging.critical("Fatal error. Cannot continue or fix the problem. Bailing out...")
        return False
    return True


def keep_up(function):
    """Log exceptions and execute the function again."""
    while True:
        try:
            return function()
        except Exception:
            logging.exception("Exception, sleeping for 30 secs")
            time.sleep(30)


def formatNumber(n):
    """Format Mem€ in a short format"""
    suffixes = {6: 'M', 9: 'B', 12: 'T', 15: 'Q'}
    digits = len(str(n))
    if digits <= 6:
        return '{:,}'.format(n)
    exponent = (digits - 1) - ((digits - 1) % 3)
    mantissa = n / (10**exponent)
    suffix = suffixes.get(exponent)
    return '{:.2f}{}'.format(mantissa, suffix)


class EmptyResponse():
    """Mock up of reddit message"""

    def __init__(self):
        self.body = "[fake response body]"

    def edit_wrap(self, body):
        """Log to console"""
        logging.info(" -- editing fake response")
        logging.info(body)


def edit_wrap(self, body):
    """Utility method to check configuration before posting to Reddit"""
    logging.info(" -- editing response")

    if config.POST_TO_REDDIT:
        try:
            return self.edit(body)
        # TODO: get rid of this broad except
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return False
    else:
        logging.info(body)
        return False
