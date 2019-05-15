import getpass
import calendar
import os
import platform
import sys
import urllib.request
import codecs
import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

# -------------------------------------------------------------
# -------------------------------------------------------------

# Global Variables
driver = None
driverTemp=None

list=[]
# -------------------------------------------------------------
# -------------------------------------------------------------
def get_post(driver):
    p = get_page_neme(driver)
    c = get_post_content(driver)
    t = get_post_timestamp(driver)
    return p,c, t

def get_post_content(driver):
    try:
        content = driver.find_element_by_xpath(".//div[@class='_5pbx userContent _3576']").text
        return content
    except:
        try:
            content = driver.find_element_by_xpath(".//div[contains(@class, '_1rg-')]").text #_5aj7
            return content
        except:
            return " "

def get_page_neme(driver):
    try:
        page_name = driver.find_element_by_xpath(".//span[contains(@class,'fwb fcg')]").text
        return page_name
    except:
        try:
            page_name = driver.find_element_by_xpath(".//a[contains(@class, 'profileLink')]").text
            return page_name
        except:
            return " "

def get_post_timestamp(driver):
    try:
        timestamp = driver.find_element_by_xpath(".//abbr[@class='_5ptz']").get_attribute('data-utime')
        return timestamp
    except:
        try:
            timestamp = driver.find_element_by_xpath(".//abbr[@class='_13db timestamp']").get_attribute('data-utime')
            return timestamp
        except:
            return " "

# -------------------------------------------------------------

# --Helper Functions for Reactions
def get_reactions(driver):
    try:
        react = driver.find_element_by_xpath("//*[div[@class='_66lg']]")
        return react
    except:
        try:
            react = driver.find_element_by_xpath("//*[div[@class='_ipp']]")
            return react
        except:
            return " "

def get_reactions_links(divv, tag):
    try:
        return divv.find_element_by_tag_name(tag)
    except:
        return ""

def get_types_of_reactions():
    try:
        names=driverTemp.find_elements_by_xpath(".//div[@class='_3p56']")
        return names
    except:
        return ""

def scroll_reactions(kinds):
    try:
        while kinds.find_element_by_xpath(".//div[@class='clearfix mtm uiMorePager stat_elem _52jv']"):
            kinds.find_element_by_xpath(".//div[@class='clearfix mtm uiMorePager stat_elem _52jv']").click()
            scroll_reactions(kinds)
        return " "
    except:
        return " "

def get_divs_with_reactions():
    try:
        divs = driverTemp.find_elements_by_xpath(".//div[@class='_5i_p']")
        for d in divs:
            scroll_reactions(d)
        return divs
    except:
        return  ""

def get_persons_who_reacted(kinds):
    try:
        scroll_reactions(kinds)
        persons = kinds.find_elements_by_xpath(".//div[@class='_5j0e fsl fwb fcb']")
        return persons
    except:
        return " "

def get_person_link(divv, tag):
    try:
        return divv.find_element_by_tag_name(tag)
    except:
        return ""

# -------------------------------------------------------------
# -------------------------------------------------------------

# --Helper Functions for Comments

def scroll_comments(divv):
    try:
        while (divv.find_element_by_xpath(".//div[@class='_4sxd']")):
            divv.find_element_by_xpath(".//div[@class='_4sxd']").click()
            scroll_comments(divv)
        return " "
    except:
        return " "

def get_comments(driver):
    try:
        comments = driver.find_element_by_xpath("//*[div[@class='_3w53']]")
        scroll_comments(comments)
        coms = comments.find_elements_by_xpath(".//div[contains(@class, '_4eek')]")
        return coms
    except:
        try:
            comments = driver.find_element_by_xpath("//*[div[@class='_3b-9 _j6a']]")
            scroll_comments(comments)
            coms = comments.find_elements_by_xpath(".//div[contains(@class, 'UFICommentContentBlock')]")
            return coms
        except:
            return " "

def get_a_person_who_commented(d):
    try:
        commentator=d.find_element_by_xpath(".//a[@class='_6qw4']")
        tmp = commentator.text
        return commentator.text
    except:
        try:
            commentator = d.find_element_by_xpath(".//a[contains(@class, 'UFICommentActorName')]")
            tmp = commentator.text
            return commentator.text
        except:
            return " "

def get_a_content_of_the_comment(d):
    try:
        content=d.find_element_by_xpath(".//span[@class='_3l3x']/span")
        return content.text
    except:
        try:
            content = d.find_element_by_xpath(".//span[@class='UFICommentBody']/span")
            return content.text
        except:
            return " "

#def get_timestamp_of_the_comment(d):

def get_reactions_on_the_comment(d):
    try:
        reaction_div=d.find_element_by_xpath(".//div[@class='_6cuq']")
        return reaction_div
    except:
        return " "

def get_comments_reactions_link(divv, tag):
    try:
        solution=""
        if (divv.find_element_by_tag_name(tag)):
            solution=divv.find_element_by_tag_name(tag)
        return solution
    except:
        return ""

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def replace(react):
    if react == "Свиђа ми се":
        return "like"
    elif react =="Љут":
        return "angry"
    elif react =="Хаха":
        return "haha"
    elif react =="Тужан":
        return "sad"
    elif react =="Wow":
        return "wow"
    elif react =="Воли":
        return "love"
    else:
        return react

def extract_and_write_posts(post_link, post_content, reactions, comments):

    try:
        data = {}
        reaction_json = []
        comments_json=[]

        data['page_name']=post_content[0]
        data['post_content']=post_content[1]
        data['post_utime']= post_content[2]
        data['post_link'] = post_link

        # reactions links
        reactions_link = get_reactions_links(reactions, "a").get_attribute('href')

        driverTemp.get(reactions_link)

        # people who reacted
        types_of_reaction = get_types_of_reactions()
        big_divs = get_divs_with_reactions()


        j = 0
        for reaction_name in types_of_reaction:

            persons = get_persons_who_reacted(big_divs[j])
            number_of_reactions = str(len(persons))


            for person in persons:

                user={}

                person_link = get_person_link(person, "a").get_attribute('href')

                user['reaction']=replace(reaction_name.text)
                user['user']=person.text
                user['user_link']=person_link.split("fref")[0][:-1]
                reaction_json.append(user)
            j += 1

        data['reactions']=reaction_json

        # comments
        #all_comments = get_a_comment_divs(comments)
        all_comments = comments
        number_of_comments = str(len(all_comments))


        for one_comment in all_comments:

            commentator = get_a_person_who_commented(one_comment)
            commentator_link = get_person_link(one_comment, "a").get_attribute('href')
            content = get_a_content_of_the_comment(one_comment)

            comment_reactions_json=[]
            com={}
            com['user']=commentator
            com['user_link'] =commentator_link.split("fref")[0][:-1]
            com['content'] =content

            #comments_json.append(com)
            react_div = get_reactions_on_the_comment(one_comment)
            react_link = get_comments_reactions_link(react_div, "a")
            if (react_link != ""):
                react_link = react_link.get_attribute('href')

                # reactions on a comment
                driverTemp.get(react_link)
                # people who reacted
                types_of_react = get_types_of_reactions()
                b_d = get_divs_with_reactions()

                l = 0
                for react_name in types_of_react:

                    per = get_persons_who_reacted(b_d[l])
                    num_of_react = str(len(per))

                    for p in per:

                        u={}
                        p_link = get_person_link(p, "a").get_attribute('href')

                        u['reaction']=replace(react_name.text)
                        u['user'] =p.text
                        u['user_link'] =p_link.split("fref")[0][:-1]
                        comment_reactions_json.append(u)

                    l += 1
                com['reactions']=comment_reactions_json
            else:
                com['reactions']=[]
            comments_json.append(com)


        data['comments']=comments_json
        #fjson_name = filename + ".json"


    except:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info()[0])

    return data

# -------------------------------------------------------------
# -------------------------------------------------------------

def save_to_file(post_link, post_content, reactions, comments):
    try:
        # dealing with Posts
        data = extract_and_write_posts(post_link, post_content, reactions, comments)
        tmp = post_link.replace(':','').replace('?','').split('/')

        #DESTINATION
        #json_name = "C:\\Users\\Win 10\\Desktop\\fake_news_project\\Data\\real\\" + tmp[3] + tmp[5] + ".json"
        json_name = "C:\\Users\\Win 10\\Desktop\\fake_news_project\\Data\\real\\" + data["page_name"]+ data["post_utime"] + ".json"

        with open(json_name, 'w', encoding='utf8') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True, ensure_ascii=False)
        print ("saved data to:", json_name)
        return
    except:
        print("Exception (save_to_file)", sys.exc_info()[0])

    return


def create_original_link(url):
    if url.find(".php") != -1:
        original_link = "https://en-gb.facebook.com/" + ((url.split("="))[1])

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = "https://en-gb.facebook.com/" + ((url.split("/"))[-1].split("?")[0])
    elif url.find("_tab") != -1:
        original_link = "https://en-gb.facebook.com/" + (url.split("?")[0]).split("/")[-1]
    else:
        original_link = url

    return original_link


def scrap_data():
    """Given some parameters, this function can scrap friends/photos/videos/about/posts(statuses) of a profile"""
    print("Posts:")

    #SOURCE
    file_posts = codecs.open(os.path.join(os.path.dirname(__file__), "real.txt"), "r", "utf-8")

    lines=file_posts.readlines()
    file_posts.close()

    for adr in lines:
        page = adr[:-2]

        try:
            driver.get(page)

            comments=get_comments(driver)
            reactions=get_reactions(driver)
            post_data = get_post(driver)
        except:
            print("Exception (scrap_data)", sys.exc_info()[0])

        save_to_file(page, post_data, reactions, comments)

def login(email, password):
    """ Logging into our own profile """

    try:
        global driver
        global driverTemp

        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        # options.add_argument("headless")

        try:
            platform_ = platform.system().lower()
            if platform_ in ['linux', 'darwin']:
                driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
                driverTemp = webdriver.Chrome(executable_path="./chromedriver", options=options)
            else:
                driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
                driverTemp = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
        except:
            print("Kindly replace the Chrome Web Driver with the latest one from "
                  "http://chromedriver.chromium.org/downloads"
                  "\nYour OS: {}".format(platform_)
                 )
            exit()

        driver.get("https://en-gb.facebook.com")
        driver.maximize_window()
        # filling the form
        driver.find_element_by_name('email').send_keys(email)
        driver.find_element_by_name('pass').send_keys(password)

        # clicking on login button
        driver.find_element_by_id('loginbutton').click()

        #the same for driverTemp
        driverTemp.get("https://en-gb.facebook.com")
        driverTemp.find_element_by_name('email').send_keys(email)
        driverTemp.find_element_by_name('pass').send_keys(password)
        driverTemp.find_element_by_id('loginbutton').click()

    except Exception as e:
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit()


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def main():
    # Getting email and password from user to login into his/her profile
    email = "uros.ng@gmail.com"
    # password = getpass.getpass()
    password = ""

    print("\nStarting Scraping...")

    login(email, password)
    scrap_data()
    driver.close()
    driverTemp.close()

# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

if __name__ == '__main__':
    # get things rolling
    main()
