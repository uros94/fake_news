
import numpy as np
import random
import unittest


class Post(object):
    """Class representing an item.  See VotingGraph for general comments."""

    def __init__(self, id, page, content, udate, true_value=None, is_testing=False, inertia=1.0):
        """
        Initializes an item.
        :param known_value: None if we don't know the truth value of the item; +1 for True, -1 for False.
        :param true_value: The true value, if known.
        :param is_testing: If true, then we don't use the true value in the inference.
        """
        self.id = id
        self.page = page
        self.udate = udate
        self.content = content
        self.inferred_value = None # Value computed by the inference.
        # True value (ground truth)
        self.true_value = 0.0 if true_value is None else 1.0 if true_value else -1.0
        self.is_testing = is_testing
        # Inertia for changing the belief.
        self.inertia = inertia
        self.users = [] # List of users who voted on the item.

    def __repr__(self):
        return repr(dict(
            id=self.id,
            inferred_value=self.inferred_value,
            true_value=self.true_value,
            is_testing=self.is_testing,
            correct=self.is_correctly_classified(),
            users=[u.id for _, u in self.users]
        ))

    def add_user(self, u, pol):
        """Add user u with polarity pol to the item."""
        self.users.append((pol, u))

    def set_is_testing(self, is_testing):
        self.is_testing = is_testing

    def set_true_value(self, true_value):
        self.true_value = None if true_value is None else 1.0 if true_value else -1.0

    def is_correctly_classified(self):
        """Returns (t, c), where t is 1 whenever we can measure whether the
        classification is correct, and c is the correctness (0 = wrong, 1 = correct).
        """
        if (not self.is_testing) or self.true_value is None or self.inferred_value is None:
            return (0.0, 0.0)
        else:
            return (1.0, 1.0) if self.inferred_value * self.true_value > 0 else (1.0, 0.0)

    def initialize(self):
        """Initializes the item, setting its inferred_value to the known value
        unless we are testing."""
        self.inferred_value = None if self.is_testing else self.true_value

    def compute_post_value(self):
        """Performs one step of inference for the item."""
        if (self.true_value is None) or self.is_testing:
            # Performs actual inference
            pos_w = neg_w = self.inertia
            for pol, u in self.users:
                if u.inferred_value is not None:
                    delta = pol * u.inferred_value
                    # print "  Item ", self.id, "from user", u.id, "polarity", pol, "delta:", delta # debug
                    if delta > 0:
                        pos_w += delta
                    else:
                        neg_w -= delta
            self.inferred_value = (pos_w - neg_w) / (pos_w + neg_w)
            #print ("Item", self.id, "inferred value", pos_w, neg_w, self.inferred_value) # debug
        else:
            # The value is known, and we are allowed to use it.
            self.inferred_value = self.true_value
            # print "Item", self.id, "inferred = truth", self.inferred_value

    def degree(self):
        return len(self.users)
