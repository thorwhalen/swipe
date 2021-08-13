"""
Swipe through data once, with a comb that will pick up the points you're looking for.

Think single pass search.

Think k nearest neighbors, but brute force, but with multiple targets.

"""
from heapq import heappushpop, heappush


class KeepMaxK(list):
    def __init__(self, k):
        super(self.__class__, self).__init__()
        self.k = k

    def push(self, item):
        if len(self) >= self.k:
            heappushpop(self, item)
        else:
            heappush(self, item)


class KeepMaxUnikK(object):
    def __init__(self, k):
        self.min_val_items = KeepMaxK(k)
        self.item_set = set()

    def push(self, item, val):
        if item not in self.item_set:
            self.item_set.add(item)
            self.min_val_items.push((val, item))

    def items_sorted(self):
        return [x[1] for x in sorted(self.min_val_items, key=lambda x: x[0])]


class KeepMinK(list):
    """
    Does what KeepMaxK does, but with min.
    NOTE: Only works with items that are pairs. This is because handling the more general case makes the push two
    times slower (overhead due to handling various cases).
    If you try to push items that are not list-like, it will raise a TypeError.
    If you push items that have only one element, it will raise an IndexError.
    If you push items that have more than 2 elements, only the first two will be taken into account.
    """

    def __init__(self, k):
        super(self.__class__, self).__init__()
        self.k = k

    def push(self, item):
        # try:
        #     item = [-item[0]] + list(item[1:])
        # except TypeError:
        #     item = -item

        if len(self) >= self.k:
            heappushpop(self, (-item[0], item[1]))
        else:
            heappush(self, (-item[0], item[1]))

    def get_list(self):
        return [(-item[0], item[1]) for item in self]


class HighestScoreSwipe(object):
    def __init__(self, score_of, chk_size, chk_step=1):
        self.score_of = score_of
        self.chk_size = chk_size
        self.chk_step = chk_step

    def __call__(self, it):
        pass


def highest_score_swipe(it, score_of=None, k=1, output=None):
    """Get the k items from the iterable `it` who score the highest with `score_of`.
    (think of `score_of` an inverse of `key` argument of the `sorted` python function).

    As far as the output is concerned, you can acheive something about the same with

    ```
    highest_score_swipe(it, score_of, k, output)
    ```

    as with

    ```
    output(sorted(it, key=score_of, reverse=True)[:k])
    ```

    (With slightly different output functions)

    The difference is that in the last one,
    - you have to fit all of the data in memory
    - you have to sort all of the data

    But to get the top `k` elements you don't have to. You just have to scan though
    the data once while maintaining a list of the top items.
    So when there's a lot of data, `highest_score_swipe` will save you both memory and
    computation.

    >>> from swipe import highest_score_swipe
    >>>
    >>> data = [('Christian', 12), ('Seb', 88), ('Thor', 27), ('Sylvain', 42)]

    Let's see what you get out of the box (i.e. only specifying what's required,
    using defaults for all the rest).
    We'll `iter(data)` just to this once to show that data only has to be iterable.

    >>> highest_score_swipe(iter(data))
    [(('Thor', 27), ('Thor', 27))]

    Now, out of the box, you don't get much, and looks a bit strange.
    Reason is if you don't specify `k` you just get the
    top item, and if you don't specify what score should be used to measure the "top",
    it'll just use python's default comparison operator which here brings
    `('Thor', 27)` on the top because it's lexicographically the last.

    And why is `('Thor', 27)` repeated twice?
    Because it acts both as a score (the first) and a data item (the second).

    Where it becomes interesting (and useful) is when you specify what score function
    it should use. So let's.

    >>> length_of_name = lambda x: len(x[0])
    >>> by_age = lambda x: x[1]
    >>> highest_score_swipe(data, by_age)
    [(88, ('Seb', 88))]
    >>> highest_score_swipe(data, length_of_name)
    [(9, ('Christian', 12))]
    >>> highest_score_swipe(data, length_of_name, k=2)
    [(7, ('Sylvain', 42)), (9, ('Christian', 12))]

    Now let's see about that `output` argument.
    It's used to specify how you want the result to be processed before returning.

    >>> highest_score_swipe(data, length_of_name, k=2, output='top_tuples')
    [(9, ('Christian', 12)), (7, ('Sylvain', 42))]
    >>> highest_score_swipe(data, length_of_name, k=2, output='items')
    [('Sylvain', 42), ('Christian', 12)]
    >>> highest_score_swipe(data, length_of_name, k=2, output='scores')
    [7, 9]
    >>> highest_score_swipe(data, length_of_name, k=2, output='top_score_items')
    [('Christian', 12), ('Sylvain', 42)]

    You can also specify a custom function:

    >>> highest_score_swipe(
    ...     data, length_of_name, k=2,
    ...     output=lambda km: [f"{name} (whose name has {score} letters), is {age}" for score, (name, age) in km]
    ... )
    ['Sylvain (whose name has 7 letters), is 42', 'Christian (whose name has 9 letters), is 12']

    What if you wanted the indices (that is, the integer indexing the data) of the top 2
    as your output? Here's a recipe for that:

    >>> highest_score_swipe(
    ...     enumerate(data),  # enumerate the data to get a (i, item) iterator
    ...     lambda x: length_of_name(x[1]),  # apply your scoring function to the item
    ...     k=2,
    ...     output=lambda km: [x[1][0] for x in km]  # extract the indices
    ... )

    :param it: An iterable of data items
    :param score_of: The function that will be applied to the items to get a score
    :param k: The number of highest score items to return
    :param output: How to prostprocess what's returned.
    By default it will be a KeepMaxK instance, which is a list/heap that keeps only top
    (score, item) pairs. But you can ask for
        - output == "top_tuples": Get the same, but as a (descending order) sorted list
        (a KeepMaxK maintains a list of top items, but not in sorted order!)
        - output == "items": Only the items
        - output == "scores": Only the scores
        - output == "top_score_items": Only items, sorted by descending score order
        - if not, output is a callable that will be called on your output
    :return:


    """
    if score_of is None:
        score_of = lambda x: x

    if output is None:
        output = lambda km: km
    elif isinstance(output, str):
        if output == "top_tuples":
            output = lambda km: sorted(km, reverse=True)
        elif output == "items":
            output = lambda km: [x[1] for x in km]
        elif output == "scores":
            output = lambda km: [x[0] for x in km]
        elif output == "top_score_items":
            output = lambda km: [
                x[1] for x in sorted(km, key=lambda x: x[0], reverse=True)
            ]

    if not callable(output):
        raise ValueError("Unrecognized output: ".format(output))

    km = KeepMaxK(k=k)

    for x in it:
        km.push((score_of(x), x))

    return output(km)
