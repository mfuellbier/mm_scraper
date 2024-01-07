#!/bin/python

import argparse
import requests
import logging
import sqlite3
import sys
import time


def main(args=None):
    if not args:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Media Markt Scraper",
        # epilog="As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "-s",
        "--search-string",
        help="The search string for the Fundgrube",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--max-price", "-p", help="Max price filter", default="999999999", type=str
    )
    parser.add_argument(
        "--token", help="The token of your Telegram bot", required=True, type=str
    )
    parser.add_argument("-c", "--chat-id", help="Chat_id", required=True, type=str)
    parser.add_argument(
        "--timer",
        "-t",
        help="Number of minutes to wait between requests.",
        default=5,
        type=str,
    )
    parser.add_argument(
        "--verbose", "-v", help="Print more information", action="store_true"
    )
    args = parser.parse_args(args)

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(
        level=loglevel, format="%(asctime)s %(levelname)-8s %(message)s"
    )

    while True:
        routine(args)
        time.sleep(args.timer * 60)


def routine(args):
    table_name = args.search_string.replace(" ", "_")
    # drop_table(table_name)  # Enable for debugging only

    response = query_URL(args.search_string)
    new_entries = update_results(table_name, response.json(), args.max_price)
    for entry_id in new_entries.keys():
        send_to_telegram(new_entries[entry_id], args.chat_id, args.token)


def send_to_telegram(entry, chat_id, token):
    text = entry["name"] + " - " + entry["price"] + "€"
    obj = {"chat_id": "-100" + chat_id, "text": text}
    requests.post("https://api.telegram.org/bot" + token + "/sendMessage", json=obj)


def drop_table(table_name):
    db = sqlite3.connect("mm_scraper.db")
    cursor = db.cursor()
    cursor.execute("DROP TABLE " + table_name)
    db.close()


def update_results(table_name, response_json, max_price):
    db = sqlite3.connect("mm_scraper.db")
    cursor = db.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS "
        + table_name
        + "(POSTING_ID text, TEXT text, PRICE text, NAME text)"
    )
    cursor.execute("SELECT * FROM " + table_name)
    rows = cursor.fetchall()
    db.close()

    # Create dictionary from db entries
    entries = dict()
    for row in rows:
        entries[row[0]] = {"text": row[1], "price": row[2], "name": row[3]}

    # Create dictionary from online postings
    postings = dict()
    for posting in response_json["postings"]:
        postings[posting["posting_id"]] = {
            "text": posting["posting_text"],
            "price": posting["price"],
            "name": posting["name"],
        }

    logging.debug("Number of postings: " + str(len(postings.keys())))

    db = sqlite3.connect("mm_scraper.db")
    cursor = db.cursor()

    new_entries = dict()
    # Add new postings in DB
    for posting_id in postings.keys():
        posting = postings[posting_id]
        # Apply filter
        if float(posting["price"]) <= float(max_price):
            if posting_id not in entries.keys():
                # Add Entry in table
                logging.info("Write " + posting_id)
                cursor.execute(
                    "INSERT INTO "
                    + table_name
                    + "(POSTING_ID, TEXT, PRICE, NAME) VALUES(?,?,?,?)",
                    (posting_id, posting["text"], posting["price"], posting["name"]),
                )
                new_entries[posting_id] = posting
            else:
                logging.debug("Skip " + posting_id)

    # Remove entries from DB which are not online anymore
    for entry_id in entries.keys():
        if entry_id not in postings.keys():
            # Drop entry
            cursor.execute(
                "DELETE FROM " + table_name + " WHERE POSTING_ID = '" + entry_id + "';"
            )
            logging.debug("Remove " + entry_id)

    db.commit()
    db.close()

    return new_entries


def query_URL(search_string):
    url = "https://www.mediamarkt.de/de/data/fundgrube/api/postings"
    params = {
        "limit": 240,
        "offset": 0,
        "orderBy": "new",
        "text": search_string,
        "recentFilter": "text",
    }

    headers = {
        # 'Host': 'www.mediamarkt.de',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36",
    }
    # return "https://www.mediamarkt.de/de/data/fundgrube/api/postings?limit=240&offset=0&orderBy=new&text=" + urllib.parse.quote(search_string) + "&recentFilter=text"
    response = requests.get(url, params=params, headers=headers)
    return response
