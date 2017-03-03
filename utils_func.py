# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Various functional-paradigm helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from collections import deque
from functools import reduce

from .utils import areinstances, args2sgpl, tuplist

# Non-lazy (materialized at one point) variant of map
# (http://stackoverflow.com/a/18433519).
foreach = lambda *args: deque(map(*args), maxlen=0)

apply_preserving_depth = \
    lambda action: \
        lambda item: \
            type(item)(apply_preserving_depth(action)(i) for i in item) \
            if tuplist(item) else action(item)
apply_aggregation_preserving_depth = \
    lambda agg_fn: \
        lambda item: \
            agg_fn(type(item)(apply_aggregation_preserving_depth(agg_fn)(i)
                              for i in item)) \
            if tuplist(item) else item
apply_aggregation_preserving_passing_depth = \
    lambda agg_fn, d=0: \
        lambda item: \
            agg_fn(type(item)(
                apply_aggregation_preserving_passing_depth(agg_fn, d+1)(i)
                for i in item),
                d+1
            ) \
            if tuplist(item) else item
# name comes from Haskell
# note: always returns list even for input tuple
# note: when returning from recursion, should always observe scalar or list(?)
apply_intercalate = apply_aggregation_preserving_depth(
    lambda i:
        reduce(lambda a, b: a + (b if isinstance(b, list) else [b]),
               i, [])
)

add_item = lambda seq, i: \
    seq + (i if areinstances(seq, i) else type(seq)(args2sgpl(i)))

# something like str.partition, but repeatable and applicable to sequences
# in general (can be used as a one-level only inverse function to
# apply_aggregation_preserving_depth (or, in special case, apply_intercalate),
# which itself can loose granularity while this one provide a finer view);
# note that special care was taken to make this function
# uniformly handle both strings and generic iterables (unlike the other
# functions)
apply_partition = \
    lambda i, partitioner: \
        (lambda result: result[:-1] if result[-1] == type(i)() else result)(
            reduce(
                lambda acc, (ee, ii):
                    acc[:-1] + [add_item(acc[-1], ii)]
                    if not partitioner(ii, ee, acc) else (acc if ee else [])
                        + [add_item(type(i)(), ii)] + [type(i)()],
                enumerate(i),
                [type(i)()]
            )
        )

# ...and also something like str.split (unlimited variant)
apply_split = \
    lambda i, splitter: \
        (lambda result: result[:-1] if result[-1] == type(i)() else result)(
            reduce(
                lambda acc, (ee, ii):
                    acc[:-1] + [add_item(acc[-1], ii)]
                    if not splitter(ii, ee, acc) else acc + [type(i)()],
                enumerate(i),
                [type(i)()]
            )
        )

# Haskell: partition
bifilter = \
    lambda fnc, seq: \
        reduce(lambda acc, x: acc[int(not fnc(x))].append(x) or acc,
               seq, ([], []))

# Given the partitioning function, do the recursive refinement in a way
# the parts reaching the bottom line in more steps are continually "shaked"
# towards the end (with a stable relative order, though).
# Default partitioning function just distinguishes between tuples/lists
# and other values (presumably scalars) so when passed a tuple/list encoding
# a graph (tree/forest) in a DFS manner using unrestricted nesting, it will
# return serialized BFS walk of the same.
# NOTE if there are scalars already at the start-level depth, use
#      `tail_shake_safe` (not that it provides much more guarantee :-p)
tailshake = \
    lambda src, partitioner=(lambda x: not tuplist(x)): \
        reduce(lambda a, b: a + (tailshake(b, partitioner) if b else b),
               reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]),
                      tuple(bifilter(partitioner, i) if tuplist(i) else (i, [])
                      for i in src), ([], [])))

tailshake_safe = \
    lambda src, partitioner=(lambda x: not tuplist(x)): \
        tailshake(src if all(tuplist(i) for i in src) else (src, ),
                  partitioner)


zipped_outlier = type('zipped_outlier', (tuple, ), {})
zip_empty = type('zip_filler', (str, ), {})("EMPTY")
loose_zip = lambda a, b: zip(
    list(a) + (max(len(a), len(b)) - len(a)) * [zip_empty],
    list(b) + (max(len(a), len(b)) - len(b)) * [zip_empty]
)
apply_loose_zip_preserving_depth = \
    lambda a, b: \
        type(a)(
            [apply_loose_zip_preserving_depth(*p) for p in loose_zip(a, b)]
        ) if tuplist(a) == tuplist(b) == True else zipped_outlier([a, b])
# as previous, but with length checking of some sort
# NOTE: automatically shortens the longer counterpart in the pair
#       to the length of the bigger one
apply_strict_zip_preserving_depth = \
    lambda a, b: \
        type(a)(
            [apply_strict_zip_preserving_depth(*p) for p in zip(a, b)]
        ) if tuplist(a) == tuplist(b) == True and len(a) == len(b) \
        else zipped_outlier([a, b])
