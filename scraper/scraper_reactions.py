from html.parser import HTMLParser
from typing import Any
import json

class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(MyHTMLParser, self).__init__(*args, **kwargs)
        #data regarding user reactions
        self.reactions = []
        self.reactions_link = ""
        self.temp_reaction = ""
        self.temp_name = ""
        self.temp_user_link = ""


    def detect_reaction(self, icon):
        if icon == "_2p78 _2p7a _9-- img sp_Erm1GyxvO7I sx_72c12d":
            return 'like'
        if icon == "_2p78 _2p7a _9-- img sp_Erm1GyxvO7I sx_52e699":
            return 'angry'
        if icon == "_2p78 _2p7a _9-- img sp_Erm1GyxvO7I sx_aef885":
            return 'sad'
        if icon == "_2p78 _2p7a _9-- img sp_Erm1GyxvO7I sx_c3c538":
            return 'haha'
        if icon == "_2p78 _2p7a _9-- img sp_Erm1GyxvO7I sx_19d7b0":
            return 'wow'
        if icon == "_2p78 _2p7a _9-- img sp_Erm1GyxvO7I sx_2c6fed":
            return 'love'
        return ''

    def handle_starttag(self, tag, attrs):
        if tag=="a" and attrs: #looking for link to users profile
            if attrs[0][1] == "_5i_s _8o _8r lfloat _ohe": #links representing user are part of '_5i_s _8o _8r lfloat _ohe' class
                self.temp_user_link=attrs[1][1][0:-36]
                #print("USER LINK", self.temp_user_link) #link to user profile

        elif tag == "img" and attrs:  # looking for users name, which could be find among attrs of img
            if attrs[0][1] == "_s0 _4ooo img":  # img with user name is part of "_s0 _4ooo img" class
                self.temp_name = attrs[3][1]
                #print("USER NAME", self.temp_name)  # users name

        elif tag == "i":  # looking for users reaction, which could be detected by emoji (icon)
            icon = self.detect_reaction(attrs[0][1])
            if icon != '':
                self.temp_reaction = icon
                self.reactions.append({'user': self.temp_name, 'user_link': self.temp_user_link, 'reaction': self.temp_reaction})
                #print("USER REACTION", icon)  # reaction

    def handle_endtag(self, tag):
        pass
        #print("Encountered an end tag :", tag)

    def handle_data(self, data):
        pass
        #print("Encountered some data  :", data)

def scrape_reactions(html_file, json_file): #html_file - location of file containing html, json_file - destinantion where json data will be saved
    parser = MyHTMLParser()
    f = open(html_file, "r", encoding="utf-8")
    if f.mode == 'r':
        parser.reactions_link = f.readline()[0:-1] #last sign is '\n' for new row, we dont need that
        f1 = f.read()
        print(parser.reactions_link)
        parser.feed(f1)

    post_data = {'reactions_link': parser.reactions_link, 'reactions': parser.reactions}
    with open(json_file, 'w', encoding='utf8') as outfile:
        json.dump(post_data, outfile, indent=4, sort_keys=True, ensure_ascii=False)
    print ("saved data to:", json_file)
