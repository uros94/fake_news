import numpy as np
import random
import unittest

class User(object):
    """Class representing a user.  See VotingGraph for general comments."""

    def __init__(self, id, known_value=None, neg_weight=1.0, pos_weight=1.5):
        """Initializes a user.
        :param known_value: None if we don't know the goodness of the user, otherwise, the goodness of the
        user as a number between 0 and 1.
        :param pos_weight: Initial positive weight of a user.
        :param neg_weight: Initial (offset) negative weight of a user.  These two weights correspond to how many
            correct and wrong likes we have seen the user do in the past, and is used to initialize the algorithm
            so we need automatically some evidence before we believe a user is right or wrong, with a weak
            initial positive bias.
        """
        self.id = id
        self.initial_pos_weight = pos_weight
        self.initial_neg_weight = neg_weight
        self.known_value = known_value
        self.inferred_value = known_value
        self.posts = []

    def __repr__(self):
        return repr(dict(
            id=self.id,
            known_value=self.known_value,
            inferred_value=self.inferred_value,
            posts=[post.id for _, post in self.posts]
        ))

    def add_post(self, post, pol):
        """ Adds an item it with polarity pol to the user. """
        self.posts.append((pol, post))

    def initialize(self):
        self.inferred_value = None

    def compute_user_value(self):
        """Performs one step of inference on the user."""
        pos_w = float(self.initial_pos_weight)
        neg_w = float(self.initial_neg_weight)
        # Iterates over the items.
        for pol, post in self.posts:
            if post.inferred_value is not None:
                delta = pol * post.inferred_value
                # print "  User", self.id, "from item", it.id, "polarity", pol, "delta:", delta # debug
                if delta > 0:
                    pos_w += delta
                else:
                    neg_w -= delta
        self.inferred_value = (pos_w - neg_w) / (pos_w + neg_w)
        #print ("User", self.id, "inferred value:", pos_w, neg_w, self.inferred_value)
