import numpy as np
import random
import unittest
from user import User
from post import Post
import json
import utils
from random import randrange

#addresses of datasets - posts + comments
datasets = utils.datasets

class VotingGraph(object):
    """This class represents a bipartite graph of users and items.  Users and items are connected via
    edges that can be labeled either +1 (True) or -1 (False) according to whether the user thinks
    the item is true or false.  We could use booleans as edge labels, but we would lose the ability to
    represent levels of certainty later on, so for now, we use integers.
    It is possible to label items as +1 (True) or -1 (False), in which case the items have a known truth
    value; alternatively, the item label can be left to None, and it can be later inferred."""

    def __init__(self, start_pos_weight=5.01, start_neg_weight=5.0, post_inertia=5.0):
        """Initializes the graph.
        The user initially has a value of
        (start_pos_weight - start_neg_weight) / (start_pos_weight + start_neg_weight),
        and start_pos_weight and start_neg_weight essentially give the inertia with which
        we modify the opinion about a user as new evidence accrues.
        :param start_pos_weight: Initial positive weight on a user.
        :param start_neg_weight: Initial negative weight on a user.
        :param item_inertia: Inertia on an item.
        """
        # Dictionary from items to users.
        self.posts = {} # Dictionary from id to item
        self.users = {} # Dictionary from id to user
        self.edges = [] # To sample.
        self.start_pos_weight = start_pos_weight
        self.start_neg_weight = start_neg_weight
        self.post_inertia = post_inertia

    def get_hoax(self):
        return [it.id for it in self.iter_posts() if it.true_value == -1.0]

    def get_real(self):
        return [it.id for it in self.iter_posts() if it.true_value == 1.0]

    def get_user_ids(self):
        return self.users.keys()

    def get_post_ids(self):
        return self.posts.keys()

    def iter_posts(self):
        return self.posts.values()

    def iter_users(self):
        return self.users.values()

    def get_user(self, user_id):
        return self.users.get(user_id)

    def get_post(self, post_id):
        return self.posts.get(post_id)

    def perform_inference(self, num_iterations=5):
        """Performs inference on the graph."""
        for u in self.users.values():
            u.initialize()
        for it in self.posts.values():
            it.initialize()
        for _ in range(num_iterations):
            [u.compute_user_value() for u in self.users.values()]
            [it.compute_post_value() for it in self.posts.values()]

    def print_stats(self):
        """Prints graph statistics, mainly for testing purposes"""
        num_posts_truth_known = len([it for it in self.iter_posts() if it.true_value is not None])
        num_posts_inferred_known = len([it for it in self.iter_posts() if it.inferred_value is not None])
        num_posts_testing = len([it for it in self.iter_posts() if it.is_testing])
        print ("Num items:", len(self.posts))
        print ("Num items with truth known:", num_posts_truth_known)
        print ("Num items with inferred known:", num_posts_inferred_known)
        print ("Num items testing:", num_posts_testing)
        print ("Min degree:", min([it.degree() for it in self.iter_posts()]))
        print ("Num users:", len(self.users))
        print ("Num likes:", sum([len(u.posts) for u in self.users.values()]))

    def evaluate_inference(self, fraction=100, num_runs=50):
        """
        Evaluation function we use.
        :param num_chunks: In how many chunks we split the data.
        :param num_eval_chunks: number of chunks used for evaluation, if different from num_chunks.
        :param learn_from_most: If True, we learn from all but one chunk (on which we test).
                If False, we learn from one chunk, test on all others.
        :return: A dictionary of values for creating plots and displaying performance.
        """
        post_ids = list(self.get_post_ids())
        num_posts = len(post_ids)
        chunk_len = num_posts / fraction
        correct = 0.0
        tot = 0.0
        ratios = []
        # We split the items into k portions, and we cycle, considering each
        # of these portions the testing items.
        for run_idx in range(num_runs):
            self.perform_inference()
            # vg.print_stats()
            # print("Performed inference for chunk %d" % chunk_idx)
            # Measures the accuracy.
            run_correct = 0.0
            run_total = 0.0
            for it_id in post_ids[int(chunk_len):]:
                it = self.get_post(it_id)
                tot_cor = it.is_correctly_classified()
                tot += tot_cor[0]
                correct += tot_cor[1]
                run_total += tot_cor[0]
                run_correct += tot_cor[1]
            run_ratio = run_correct / run_total
            ratios.append(run_ratio)
            print ("One run result:", run_ratio)
        # Computes the averages.
        ratio_correct = correct / tot
        return dict(
            ratio_correct=ratio_correct,
            stdev=np.std(ratios),
        )


    def evaluate_inference_given_learning(self, fun_learning):
        """
        :param: A function fun_learning, which tells us if we have to learn from an item
            with a given id yes or no.
        :return: The ratio of correctly classified items.
        """
        post_ids = self.get_post_ids()
        # We want to measure the accuracy for posts that have at least 1, 2, ..., LIKES_MEASURED likes.
        correct = 0.0
        tot = 0.0
        # Sets which items are learning, and which are testing.
        test_posts = []
        for it_id in post_ids:
            is_testing = not fun_learning(it_id)
            self.get_post(it_id).set_is_testing(is_testing)
            if is_testing:
                test_posts.append(it_id)
        # Performs the inference.
        self.perform_inference()
        # vg.print_stats()
        # print("Performed inference for chunk %d" % chunk_idx)
        # Measures the accuracy.
        for it_id in test_posts:
            it = self.get_post(it_id)
            tot_cor = it.is_correctly_classified()
            tot += tot_cor[0]
            correct += tot_cor[1]
        return correct / tot if tot > 0 else 1

    def evaluate_inference_selecting_prop_likes(self, frac=0.1):
        """
        Evaluates the accuracy over ONE run, selecting a fraction frac of items, where each item
        is selected with probability proportional to the number of links.
        :param frac: Fraction of items considered.
        :return: The ratio of correct items. 
        """
        learn_posts = set()
        post_ids = self.get_post_ids()
        # How many items do we have to pick?
        num_posts = max(1, int(0.5 + frac * len(post_ids)))
        # How many we have picked already?
        num_picked = 0
        while num_picked < num_posts:
            it_id, _ = random.choice(self.edges)
            if it_id not in learn_posts:
                num_picked += 1
                learn_posts.add(it_id)
        # Ok, now we do the learning.
        for it_id in post_ids:
            self.get_post(it_id).set_is_testing(it_id not in learn_posts)
        self.perform_inference()
        correct = 0.0
        tot = 0.0
        for it_id in post_ids:
            it = self.get_post(it_id)
            tot_cor = it.is_correctly_classified()
            tot += tot_cor[0]
            correct += tot_cor[1]
        return correct / tot if tot > 0 else 1.0

    #Create graph
    def create_graph(self, datasets=utils.datasets, mode=0):
        """

    """
        posts_out = []
        size = len(datasets)
        if mode == 1:
            posts_out.append(randrange(size))

        for post_file in datasets:
            with open(post_file, encoding='utf-8') as f:
                post = json.load(f)
                pid = utils.post2pid(post["page"] + post["post_udate"])  # ZA SADA TO JE PAGE_NAME + UDATE
                if pid: #cant identify?? - skip
                    if mode ==1 and posts_out[0]==pid:
                        p = Post(pid, post["page"], post["post_content"], post["post_udate"], None, True)
                        p.compute_post_value()
                    else:
                        p = Post(pid, post["page"], post["post_content"], post["post_udate"], utils.t_vector[pid], False)
                    self.posts[pid] = p
                    if "reactions" in post:
                        for reaction in post["reactions"]:
                            uid = utils.user2uid(reaction["user_link"])
                            if uid:
                                u = self.users.get(uid)
                                if u is None:
                                    u = User(uid, pos_weight=self.start_pos_weight, neg_weight=self.start_neg_weight)
                                    self.users[uid] = u
                                u.add_post(p, utils.classify_reaction(reaction["reaction"]))
                                p.add_user(u, utils.classify_reaction(reaction["reaction"])) #PROMENI POLARITY
                                self.edges.append((pid, uid))
                    if "comments" in post:
                        for comment in post["comments"]:
                            uid = utils.user2uid(comment["user_link"])
                            if uid:
                                u = self.users.get(uid)
                                if u is None:
                                    u = User(uid, pos_weight=self.start_pos_weight, neg_weight=self.start_neg_weight)
                                    self.users[uid] = u
                                u.add_post(p, 1)
                                p.add_user(u, 1) #PROMENI POLARITY
                                self.edges.append((pid, uid))
        print ("graph built")
        return posts_out

def test_1(g): # First, we do the analysis of leave-one-page-out.
    frac_correct_all = [] # On complete graph
    for pg in g.posts:
        #print ("post:", g.get_post(pg).page, g.get_post(pg).udate)
        # Creates the function that classifies items.
        def is_learning(itid):
            return itid != pg
        fc = g.evaluate_inference_given_learning(is_learning)
        print ("For all, correctness:", fc)
        frac_correct_all.append(fc)
        #frac_correct_w.append(posts_per_page[pg])
    print ("Final average correctness for leave-one-page-out all:", np.average(frac_correct_all))
    print ("Standard deviation:", np.std(frac_correct_all))

def test_2(g):
    # Now, let's try to keep HALF of the pages out.
    # Now, we do the analysis in which we randomly select two
    # pages hoax and two non-hoax, and we learn from those alone.
    frac_correct_all_half = []  # On complete graph
    fraction_pages = 0.5
    hoax_pages = g.get_hoax()
    nonhoax_pages = g.get_real()
    # First, for all.
    num_hoax_in = max(1, int(0.5 + len(hoax_pages) * fraction_pages))
    num_nonhoax_in = max(1, int(0.5 + len(nonhoax_pages) * fraction_pages))
    for _ in range(50):
        # Picks pages in and out.
        random.shuffle(hoax_pages)
        random.shuffle(nonhoax_pages)
        learn_pages = hoax_pages[:num_hoax_in] + nonhoax_pages[:num_nonhoax_in]

        # Defines the function.
        def is_learning(itid):
            return itid in learn_pages

        fc = g.evaluate_inference_given_learning(is_learning)
        print ("Learning from 50% of each kind, all:", fc)
        frac_correct_all_half.append(fc)

    print ("Final average correctness for learning from half of each kind, all:", np.average(frac_correct_all_half))
    print ("avg", np.average(frac_correct_all_half))
    print ("stdev", np.std(frac_correct_all_half))

g = VotingGraph()
out = g.create_graph(datasets)
g.print_stats()

"""TESTS = [10, 20, 40, 100, 200, 400, 1000]
results_all_x = []
results_all_y = []
results_all_err = []
for f in TESTS[:2]:
    d = g.evaluate_inference(fraction=f)
    print (f, d['ratio_correct'])
    results_all_x.append(f)
    results_all_y.append(d['ratio_correct'])
    results_all_err.append(d['stdev'])
print (results_all_x)
print (results_all_y)
print (results_all_err)"""

test_1(g)
test_2(g)
