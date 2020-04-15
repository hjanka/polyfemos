# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# This file is part of Polyfemos.
#
# Polyfemos is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.
#
# Polyfemos is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License and
# GNU General Public License along with Polyfemos. If not, see
# <https://www.gnu.org/licenses/>.'
#
# Author: Henrik Jänkävaara
# -----------------------------------------------------------------------------
"""
Functions to parse filepaths from strings following the internal function
syntax

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import ast
import operator


def compose(op, f1, f2):
    """
    A function to compose functions

    :type op: func
    :param op: A two argument function
    :type f1,f2: float, int, bool, func
    :param f1,f2: value or function, given function should take one argument,
        if value given, it will be changed in to one-argument function
    :rtype: func
    :return: A one argument function
    """
    # make 'arg' callable if it is not
    wrap = lambda arg: arg if callable(arg) else lambda x: arg
    return lambda x: op(wrap(f1)(x), wrap(f2)(x))


# aliases are used for defining multicharacter operations
# boolean aliases are just for convenience
_aliases = [
    ["<=", "{"],
    [">=", "}"],
    ["!=", "!"],
    ["==", "="],
    ["**", "^"],
    ["False", "F"],
    ["True", "T"],
    ["NaN", "F"],
]
# possible operations with 2 arguments
_operations = {
    "^": operator.pow,
    "*": operator.mul,
    "/": operator.truediv,
    "+": operator.add,
    "-": operator.sub,
    "<": operator.lt,
    "{": operator.le,
    ">": operator.gt,
    "}": operator.ge,
    "=": operator.eq,
    "!": operator.ne,
    "&": operator.and_,
    "|": operator.or_,
    "r": round,
}
# boolean values and identity function to include variable
_vals = {
    "X": lambda x: x,
    "F": lambda x: False,
    "T": lambda x: True,
}
_reserved = set(_operations) | set(_vals)


def function_from_str(functionstr):
    """
    Creates a simple function from given string.

    The ``functionstr`` may or may not be inside parentheses, the
    ``functionstr`` may not contain any other brackets (except curly brackets
    intead of ``<=`` and ``>=`` operations if wanted).

    Available operations in execution order,
    Order of execution of same operations is from left to right.
    Note that all of the operations take two arguments.

    +----------+-------+----------------------------+
    |Operation | Alias | Description                |
    +==========+=======+============================+
    |   ``**`` | ``^`` | power                      |
    +----------+-------+----------------------------+
    |   ``*``  |       | multiplication             |
    +----------+-------+----------------------------+
    |   ``/``  |       | division                   |
    +----------+-------+----------------------------+
    |   ``+``  |       | addition                   |
    +----------+-------+----------------------------+
    |   ``-``  |       | substracion                |
    +----------+-------+----------------------------+
    |   ``<``  |       | lesser than                |
    +----------+-------+----------------------------+
    |   ``<=`` | ``{`` | lesser or equal            |
    +----------+-------+----------------------------+
    |   ``>``  |       | greater than               |
    +----------+-------+----------------------------+
    |   ``>=`` | ``}`` | greater or equal           |
    +----------+-------+----------------------------+
    |   ``==`` | ``=`` | equal                      |
    +----------+-------+----------------------------+
    |   ``!=`` | ``!`` | not equal                  |
    +----------+-------+----------------------------+
    |   ``&``  |       | and                        |
    +----------+-------+----------------------------+
    |   ``|``  |       | or                         |
    +----------+-------+----------------------------+
    |   ``r``  |       | round, <num>r<decimals>    |
    +----------+-------+----------------------------+

    Available values

    +-------------+-------+---------------------------------------------------+
    |  Value      | Alias | Description                                       |
    +=============+=======+===================================================+
    |   ``X``     |       | The variable/argument in the resulting function   |
    +-------------+-------+---------------------------------------------------+
    |   ``False`` | ``F`` | boolean False                                     |
    +-------------+-------+---------------------------------------------------+
    |   ``True``  | ``T`` | boolean False                                     |
    +-------------+-------+---------------------------------------------------+


    Example ``functionstr`` values

    .. code-block:: text

        (False)
        (X<4.0|X>7|X==5)
        (X<4.0|X>7)
        (X<=4.0|X>=7)
        (X*0.001r3)
        (X*10./27.+5.r3)
        (X<=-1)


    :type functionstr: str
    :param functionstr:
    :rtype: func
    :return: A one-argument function which returns either boolean or numeral
        depending on the used operations
    """

    if functionstr[0] != "(" or functionstr[-1] != ")":
        # Should the parentheses be forced?
        pass

    functionstr = functionstr.strip("()")

    # replace aliases
    for alias in _aliases:
        functionstr = functionstr.replace(*alias)

    # distinguish operations from other values
    for k in _operations.keys():
        functionstr = functionstr.replace(k, " {} ".format(k))

    # distinguish unary operation '-' from the subtraction operation
    for k in _operations.keys():
        functionstr = functionstr.replace(
            " {}  - ".format(k), " {} -".format(k))

    # create list containing operations, values and numerals
    functionstr = [s for s in functionstr.split() if s]
    # evaluate numerals
    functionstr = [
        s if s in _reserved else ast.literal_eval(s) for s in functionstr]
    # replace values with their respective functions
    functionstr = [_vals[s] if s in _vals else s for s in functionstr]

    for k, v in _operations.items():
        while k in functionstr:
            i = functionstr.index(k)
            # Apply arguments to the operation and insert the
            # resulting function in place of the operation
            functionstr[i] = compose(v, functionstr[i - 1], functionstr[i + 1])
            # Remove arguments from the list
            functionstr[i - 1] = None
            functionstr[i + 1] = None
            functionstr = [s for s in functionstr if s is not None]

    func = functionstr[0]
    func = func if callable(func) else None
    return func


if __name__ == "__main__":

    fstrs = [
        "(False)",
        "(X<4.0|X>7|X==5)",
        "(X<4.0|X>7)",
        "(X<=4.0|X>=7)",
        "(X*0.001r3)",
        "(X*10./27.+5.r3)",
        "(X<=-1)",
    ]

    for fstr in fstrs:
        f = function_from_str(fstr)
        print()
        print(fstr)
        for i in range(14):
            a = i - 3
            print(a, f(a))
        print(f(float('nan')))
