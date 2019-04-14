from html.parser import HTMLParser
from typing import Any
import json
import os
import requests
import numpy as np
from scipy.sparse import dok_matrix, csr_matrix
import csv
import random
from random import randrange
from keras.models import Sequential
from keras.layers import Dense

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
def user2uid(users, user_link):
    try:
        return int(users.index(user_link))
    except:
        return False

#get post id based on its data
def post2pid(posts, post):
    try:
        return int(posts.index(post))
    except:
        return False

def classify_reaction(reaction):
    if reaction == "like":
        return 0
    elif reaction == "love":
        return 1
    elif reaction == "haha":
        return 2
    elif reaction == "wow":
        return 3
    elif reaction == "angry":
        return 4
    elif reaction == "sad":
        return 5

#create csv table representing data for linear regression
def create_matrix(datasets, users, posts, t_vector, create_csv=False):
    """we have to increase the dimension of users because we have 6 possible reactions + comment
        [                uid                     ]
        [like][love][haha][wow ][angr][sad ][comm]                  """
    like_matrix = np.zeros((len(users)*7, len(posts)), dtype=bool)

    for post_file in datasets:
        with open(post_file, encoding='utf-8') as f:
            post = json.load(f)
            post_id = post["page"] + post["post_udate"]  # ZA SADA TO JE PAGE_NAME + UDATE
            if post2pid(posts, post_id): #cant identify?? - skip
                j = post2pid(posts, post_id)
                if "reactions" in post:
                    for reaction in post["reactions"]:
                        user = reaction["user_link"]
                        if user2uid(users, user):  # cant identify?? - skip
                            i = user2uid(users, user) * 7 + classify_reaction(reaction["reaction"])
                            like_matrix[i][j] = True
                if "comments" in post:
                    for comment in post["comments"]:
                        user = comment["user_link"]
                        if user2uid(users, user):  # cant identify?? - skip
                            i = user2uid(users, user) * 7 + 6
                            like_matrix[i][j] = True
    if create_csv:
        with open('C:\\Users\\Win 10\\Desktop\\dataset\\logreg.csv', 'w') as csvfile:
            wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            wr.writerows(like_matrix)
            #for row in range(len()):
            #    wr.writerow(like_matrix.getrow(row).toarray())
            csvfile.close()
    return like_matrix

def create_model_1(X, Y):
    model = Sequential()
    model.add(Dense(12, input_dim=X.shape[1], activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Fit the model
    model.fit(X, Y, epochs=150, batch_size=10)
    # Evaluate model
    scores = model.evaluate(X, Y)
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
    return model

def predict(X, model):
    #create array
    predictions = model.predict(X)
    rounded = [round(x[0]) for x in predictions]
    #print(rounded)
    return rounded

def create_kword(post1, users, datasets=datasets):
    X = np.zeros((len(users)*7, 1), dtype=bool)
    for post_file in datasets:
        with open(post_file, encoding='utf-8') as f:
            post = json.load(f)
            post_id = post["page"] + post["post_udate"]  # ZA SADA TO JE PAGE_NAME + UDATE
            if post_id == post1:
                if "reactions" in post:
                    for reaction in post["reactions"]:
                        user = reaction["user_link"]
                        if user2uid(users, user):  # cant identify?? - skip
                            i = user2uid(users, user) * 7 + classify_reaction(reaction["reaction"])
                            X[i] = True
                if "comments" in post:
                    for comment in post["comments"]:
                        user = comment["user_link"]
                        if user2uid(users, user):  # cant identify?? - skip
                            i = user2uid(users, user) * 7 + 6
                            X[i] = True
                return X

def json2kword(post1, users, datasets=datasets):
    X = np.zeros((len(users)*7, 1), dtype=bool)
    with open(post1, encoding='utf-8') as f:
        post = json.load(f)
        if "reactions" in post:
            for reaction in post["reactions"]:
                user = reaction["user_link"]
                if user2uid(users, user):  # cant identify?? - skip
                    i = user2uid(users, user) * 7 + classify_reaction(reaction["reaction"])
                    X[i] = True
        if "comments" in post:
            for comment in post["comments"]:
                user = comment["user_link"]
                if user2uid(users, user):  # cant identify?? - skip
                    i = user2uid(users, user) * 7 + 6
                    X[i] = True
            return X


#START
posts, users, t_vector, posts_out = create_vectors(datasets, 2)
like_matrix = create_matrix(datasets, users, posts, t_vector)

model = create_model_1(like_matrix.transpose(), t_vector)

for p in posts_out:
    X = json2kword(p, users)
    Y = predict(X.transpose(), model)
    print (p, Y)