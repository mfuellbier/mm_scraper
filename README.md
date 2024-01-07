# Media Markt Fundgrube Scraper
This tool scans Media Markt Fundgrube for a string on a regular basis. If a new product has been founda message will be send to Telegram.

## Install
`git clone https://github.com/mfuellbier/mm_scraper`
`pip install .`

## Description
`mm_scraper -s "meta quest 3" -p 500 -c <channel_id> --token <API_token> ` will start a job which sends a request to Media Markt Fundgrube searching for "meta quest 3". It will filter for prices less or equal 500€. It will save the findings in a database for reference. If a product is not in the database yet a message will be send to telegram. This request will be repeated every 5 minutes.

```
usage: mm_scraper [-h] -s SEARCH_STRING [--max-price MAX_PRICE] --token TOKEN -c
                  CHAT_ID [--timer TIMER] [--verbose]

Media Markt Scraper

options:
  -h, --help            show this help message and exit
  -s SEARCH_STRING, --search-string SEARCH_STRING
                        The search string for the Fundgrube
  --max-price MAX_PRICE, -p MAX_PRICE
                        Max price filter
  --token TOKEN         The token of your Telegram bot
  -c CHAT_ID, --chat-id CHAT_ID
                        Chat_id in the format -100xxxxxxxx
  --timer TIMER, -t TIMER
                        Number of minutes to wait between requests.
  --verbose, -v         Print more information

```
