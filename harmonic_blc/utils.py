from html.parser import HTMLParser
from typing import Any
import json
import os
import requests
import numpy as np
from scipy.sparse import dok_matrix, csr_matrix
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import cross_val_score
import csv
import random
from random import randrange

#addresses of datasets - posts + comments
real_data = 'C:\\Users\\Win 10\\Desktop\\dataset\\real_json\\'
fake_data = 'C:\\Users\\Win 10\\Desktop\\dataset\\fake_json\\'
datasets = []
for dir in [real_data, fake_data]:
    for post_file in os.listdir(dir):
        datasets.append(dir+post_file)

#create vectors of posts, users, t_vector
def create_vectors(datasets=datasets, mode=0):
    """ mode is used to split dataset in different ways (used for testing accuraccy)
    0 - normal (all posts used)
    1 - one out (all posts except one random are used, and the skiped one is returned as posts_out)
    2 - half out (half of the posts are used, and the skiped ones are returned as posts_out)"""

    users = []
    posts = []
    t_vector = []  # vector of truthfulness for posts
    all = []

    posts_out = []
    size = len(datasets)
    if mode == 1:
        posts_out.append(randrange(size))
    elif mode == 2:
        #MODIFIKOVATI TAKO DA SE IYBACUJE FAKE/2 I REAL/2 A NE (REAL+FAKE)/2
        posts_out = random.sample(range(size), int(size/2))
        posts_out.sort()

    for post_file, cnt in zip(datasets, range(size)):
        with open(post_file, encoding='utf-8') as f:
            post = json.load(f)
            post_id = post["page"]+post["post_udate"] #ZA SADA TO JE PAGE_NAME + UDATE

            if posts_out and posts_out[0]==cnt:
                posts_out.remove(cnt)
                posts_out.append(post_file)
                continue

            if post_id!= '' and not post_id in posts:
                posts.append(post_id)
                t_vector.append(post_file[0:len(real_data)] == real_data)

            if "reactions" in post:
                for reaction in post["reactions"]:
                    user = reaction["user_link"]
                    all.append(user)
                    if not user in users:
                        users.append(user)
            if "comments" in post:
                for comment in post["comments"]:
                    user = comment["user_link"]
                    all.append(user)
                    if not user in users:
                        users.append(user)
    ### VISAK
    print(len(users),"USERS")
    print(len(all),"ALL")
    print(len(posts),"POSTS")
    #for i in range(len(posts)):
    #    print(t_vector[i], posts[i])

    return posts, users, t_vector, posts_out


def create_cut_vectors(datasets, min_post_like=10, min_user_like=30, print_results=False):
    posts = []
    t_vector = []
    users = []
    all = []  # temporary
    """returns the dataset filtered with these parameters:
    min_post_like: post with at least n likes
    min_user_like: users that have given at least n likes
    print_results: if True, prints the filtering effect
    output: sparse like_matrix and page/hoax label columns
    """
    for dir in datasets:  # going through data directories
        for post_file in os.listdir(dir):
            with open(dir + post_file, encoding='utf-8') as f:
                post = json.load(f)

                # posts filtering
                if ((len(post["comments"]) + len(post["comments"])) >= min_post_like):
                    post_id = post["page"] + post["post_udate"]  # ZA SADA TO JE PAGE_NAME + UDATE
                    if post_id != '' and not post_id in posts:
                        posts.append(post_id)
                        t_vector.append(dir == real_data)

                        if "reactions" in post:
                            for reaction in post["reactions"]:
                                user = reaction["user_link"]
                                all.append(user)
                                if not user in users:
                                    users.append(user)
                        if "comments" in post:
                            for comment in post["comments"]:
                                user = comment["user_link"]
                                all.append(user)
                                if not user in users:
                                    users.append(user)
    ### VISAK
    print(len(users))
    print(len(all))
    # users filtering
    for u in users:
        if (all.count(u) < min_user_like):
            users.remove(u)
    print(len(users))

    return posts, users, t_vector

#get user id based on its user_link
def user2uid(user_link):
    try:
        return int(users.index(user_link))
    except:
        return False

#get post id based on its data
def post2pid(post):
    try:
        return int(posts.index(post))
    except:
        return False

def classify_reaction(reaction):
    if reaction == "like":
        return 1
    elif reaction == "love":
        return 1
    elif reaction == "haha":
        return -1
    elif reaction == "wow":
        return 1
    elif reaction == "angry":
        return 1
    elif reaction == "sad":
        return -1

posts, users, t_vector, posts_out = create_vectors()