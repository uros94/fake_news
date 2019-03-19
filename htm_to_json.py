from html.parser import HTMLParser
from typing import Any
import json
import scraper_comments
import scraper_reactions
import os
import urllib.parse as urllib

#post + comments
real = 'C:\\Users\\Win 10\\Desktop\\real\\'
fake = 'C:\\Users\\Win 10\\Desktop\\fake\\'
real_data = 'C:\\Users\\Win 10\\Desktop\\real_json\\'
fake_data = 'C:\\Users\\Win 10\\Desktop\\fake_json\\'

#scrape post + comments
def get_post_data():
    for filename in os.listdir(real):
        scraper_comments.scrape_post(real+filename, real_data+filename)
    for filename in os.listdir(fake):
        scraper_comments.scrape_post(fake+filename, fake_data+filename)

#reactions
reactions_html = 'C:\\Users\\Win 10\\Desktop\\reactions_html\\'
reactions_data = 'C:\\Users\\Win 10\\Desktop\\reactions_data\\'

#scrape reactions
def get_reactions_data():
    for filename in os.listdir(reactions_html):
        scraper_reactions.scrape_reactions(reactions_html+filename, reactions_data+filename)

#replace 'reaction_link' with actual list of reactions
def add_reactions_to_post_data():
    for post_file in os.listdir(real_data):
        with open(real_data+post_file, encoding='utf-8') as f:
            post = json.load(f)
            if post["reactions_link"] != "":
                for reactions_file in os.listdir(reactions_data):
                    with open(reactions_data+reactions_file, encoding='utf-8') as f1:
                        reactions = json.load(f1)
                        a = post["reactions_link"][-35:]
                        b = reactions["reactions_link"][-35:]
                        if post["reactions_link"][-35:] == reactions["reactions_link"][-35:]:
                            with open(real_data+post_file, 'a', encoding='utf8') as outfile:
                                json.dump({"reactions": reactions["reactions"]}, outfile, indent=4, sort_keys=True, ensure_ascii=False)
                            print("OKE", a, b)

    for post_file in os.listdir(fake_data):
        with open(fake_data+post_file, encoding='utf-8') as f:
            post = json.load(f)
            if post["reactions_link"] != "":
                for reactions_file in os.listdir(reactions_data):
                    with open(reactions_data+reactions_file, encoding='utf-8') as f1:
                        reactions = json.load(f1)
                        a = post["reactions_link"][-35:]
                        b = reactions["reactions_link"][-35:]
                        if post["reactions_link"][-35:] == reactions["reactions_link"][-35:]:
                            with open(fake_data+post_file, 'a', encoding='utf8') as outfile:
                                json.dump({"reactions": reactions["reactions"]}, outfile, indent=4, sort_keys=True, ensure_ascii=False)
                            print("OKE", a, b)

#START
get_post_data()
get_reactions_data()
add_reactions_to_post_data()