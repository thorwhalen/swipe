
# swipe

Swipe through data once, with a comb that will pick up the points you're looking for.

Think single pass search.

Think k nearest neighbors, but brute force, but with multiple targets.

# Example

```pydocstring
>>> import swipe
>>> swipe.highest_score_swipe([5,3,7,2,9,7], k=2)
[(7, 7), (9, 9)]
>>> swipe.highest_score_swipe(iter([5,3,7,2,9,7]), score_of=lambda x: x % 3, k=2)
[(2, 2), (2, 5)]
```

That, but multidimensional and meant to be used with big data iterators.