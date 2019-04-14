from html.parser import HTMLParser
from typing import Any
import json

class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(MyHTMLParser, self).__init__(*args, **kwargs)
        #data regarding post
        self.page_name = ""
        self.post_content = ""
        self.post_udate = ""
        self.post_reactions_link = ""
        self.post_shares_link = ""
        #data regarding comments
        self.comments = []
        self.temp_link = ""
        self.temp_name = ""
        self.temp_comment = ""
        self.temp_udate = ""
        self.temp_comment_reactions_link = ""

    #NAPISATI FUNKCIJU KOJA PREVOIDI CIRILICU U LATINICU I IYBACUJE YNAKE S 'KVACICAMA'

    data_mode = 0 #data print mode> 0-do not print
    # 1-it's users name,
    # 2-its a comment,
    # 3-finished with current tag - add it to comments list
    # 4-it's post content

    def handle_starttag(self, tag, attrs):
        if tag == "div" and attrs:
            if attrs[0][1] == "_5pbx userContent _3576":  # post content is represented using div part of '_5pbx userContent _3576' class
                self.data_mode = 4  # letting data handler know that it should expect post content

            if attrs[0][1] == "_10lo _10lp": # if comment has reactions they are inside div part of '_10lo _10lp' class
                self.data_mode = 5  # in next iteration following section will catch element with link to reactions
                pass

        elif self.data_mode == 5 and tag == "a": # catching reactions link
            self.temp_comment_reactions_link = "https://www.facebook.com"+attrs[5][1]
            self.data_mode = 0

        elif tag=="a" and attrs: #looking for links
            if attrs[0][1] == "_2x4v": #links representing list of reactions are part of '_2x4v' class
                self.post_reactions_link = "https://www.facebook.com"+attrs[1][1]
                print("REACTIONS", self.post_reactions_link) #link to reactions

            elif attrs[0][1] == "_ipm _2x0m": #links representing list of shares are part of '_ipm _2x0m' class
                self.post_shares_link = "https://www.facebook.com"+attrs[2][1]

            elif len(attrs)>2:
                if attrs[2][1] == " UFICommentActorName": #links representing user are part of ' UFICommentActorName' class
                    self.temp_link = attrs[5][1][0:-14]
                    print("USER LINK", self.temp_link) #link to user profile
                    self.data_mode= 1 #letting data handler know that it should expect a users name

        elif tag == "img" and attrs:  # looking for link to users profile
            if attrs[0][1] == "_s0 _4ooo _5xib _5sq7 _44ma _rw img":  # are part of '_s0 _4ooo _5xib _5sq7 _44ma _rw img' class
                self.page_name = attrs[3][1]
                print("PAGE NAME", self.page_name)  # page name

        elif tag == "span" and attrs:  # looking for link to users profile
            if attrs[0][1] == "UFICommentBody":  # links representing users comment are part of 'UFICommentBody' class
                self.data_mode = 2 #letting data handler know that it should expect a comment text

        elif tag == "abbr" and attrs:  # looking for timestamp
            if attrs[0][1] == "UFISutroCommentTimestamp livetimestamp":  # elements with timetamp of comment are part of "UFISutroCommentTimestamp livetimestamp" class
                self.temp_udate = attrs[2][1]
                print("UDATE", self.temp_udate)  # timestamp

            elif attrs[3][1] == "_5ptz": # elements with timetamp of comment are part of "_5ptz" class
                self.post_udate = attrs[1][1]
                print("POST UDATE", self.post_udate)


    def handle_endtag(self, tag):
        if self.data_mode == 3:
            self.comments.append({'user': self.temp_name, 'user_link':self.temp_link, 'udate':self.temp_udate, 'comment':self.temp_comment, 'reactions_link':self.temp_comment_reactions_link})
            self.temp_comment_reactions_link=""
            self.data_mode = 0
        elif self.data_mode == 4:
            if tag=="div":
                print ("POST CONTENT", self.post_content)
                self.data_mode = 0
        else:
            pass
        #print("Encountered an end tag :", tag)

    def handle_data(self, data):
        if self.data_mode==1:
            #return data
            self.temp_name = data
            print("USER NAME", self.temp_name)
            self.data_mode=0
        elif self.data_mode==2:
            self.temp_comment = data
            print("COMMENT", self.temp_comment)
            self.data_mode=3
        elif self.data_mode==4:
            self.post_content += data
            #print("POST CONTENT", data)
        else:
            pass

def scrape_post(html_file, json_file): #html_file - location of file containing html, json_file - destinantion where json data will be saved
    parser = MyHTMLParser()
    f = open(html_file, "r", encoding="utf-8")
    if f.mode == 'r':
        f1 = f.read()
        #print(f1)
        parser.feed(f1)

    post_data = {'page': parser.page_name,'post_content': parser.post_content, 'post_udate': parser.post_udate,'reactions_link': parser.post_reactions_link, 'shares_link': parser.post_shares_link, 'comments': parser.comments}
    with open(json_file, 'w', encoding='utf8') as outfile:
        json.dump(post_data, outfile, indent=4, sort_keys=True, ensure_ascii=False)
    print ("saved data to:", json_file)

    #POMOCNI DEO
    #f = open("C:\\Users\\Win 10\\Desktop\\reactions.txt", "a")
    #f.write(parser.post_reactions_link+'\n')
