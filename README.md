# swipe

Swipe through data once, with a comb that will pick up the points you're looking for.

Think single pass search.

Think k nearest neighbors, but brute force, but with multiple targets.

Extremely light weight: Pure python -- no other dependencies.

# Example

The main function of `swipe` is `highest_score_swipe`. 
The other objects are there to support you in making your own kind of
swiping function. 

What `highest_score_swipe` does is 
get the k items from the iterable `it` who score the highest with `score_of`.
(think of `score_of` an inverse of `key` argument of the `sorted` python 
function).

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

```python
>>> from swipe import highest_score_swipe
>>>
>>> data = [('Christian', 12), ('Seb', 88), ('Thor', 27), ('Sylvain', 42)]
```

Let's see what you get out of the box (i.e. only specifying what's required, 
using defaults for all the rest).
We'll `iter(data)` just to this once to show that data only has to be iterable.

```python
>>> highest_score_swipe(iter(data))
[(('Thor', 27), ('Thor', 27))]
```

Now, out of the box, you don't get much, and looks a bit strange. 
Reason is if you don't specify `k` you just get the
top item, and if you don't specify what score should be used to measure the "top",
it'll just use python's default comparison operator which here brings
`('Thor', 27)` on the top because it's lexicographically the last. 

And why is `('Thor', 27)` repeated twice? 
Because it acts both as a score (the first) and a data item (the second).

Where it becomes interesting (and useful) is when you specify what score function 
it should use. So let's.

```python
>>> length_of_name = lambda x: len(x[0])
>>> by_age = lambda x: x[1]
>>> highest_score_swipe(data, by_age)
[(88, ('Seb', 88))]
>>> highest_score_swipe(data, length_of_name)
[(9, ('Christian', 12))]
>>> highest_score_swipe(data, length_of_name, k=2)
[(7, ('Sylvain', 42)), (9, ('Christian', 12))]
```

Now let's see about that `output` argument. 
It's used to specify how you want the result to be processed before returning.

```python
>>> highest_score_swipe(data, length_of_name, k=2, output='top_tuples')
[(9, ('Christian', 12)), (7, ('Sylvain', 42))]
>>> highest_score_swipe(data, length_of_name, k=2, output='items')
[('Sylvain', 42), ('Christian', 12)]
>>> highest_score_swipe(data, length_of_name, k=2, output='scores')
[7, 9]
>>> highest_score_swipe(data, length_of_name, k=2, output='top_score_items')
[('Christian', 12), ('Sylvain', 42)]
```

You can also specify a custom function:

```python
>>> highest_score_swipe(
...     data, length_of_name, k=2,
...     output=lambda km: [f"{name} (whose name has {score} letters), is {age}" for score, (name, age) in km]
... )
['Sylvain (whose name has 7 letters), is 42', 'Christian (whose name has 9 letters), is 12']
```

What if you wanted the indices (that is, the integer indexing the data) of the top 2
as your output? Here's a recipe for that:

```python
>>> highest_score_swipe(
...     enumerate(data),  # enumerate the data to get a (i, item) iterator
...     lambda x: length_of_name(x[1]),  # apply your scoring function to the item
...     k=2,
...     output=lambda km: [x[1][0] for x in km]  # extract the indices
... )
```