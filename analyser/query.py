#!/usr/bin/env python

#TODO: Documentation

class Query(object):

    def __init__(self):
        raise NotImplementedError()

    def apply(self):
        raise NotImplementedError()

    def isAccepting(self):
        raise NotImplementedError()

    def isFrozen(self):
        raise NotImplementedError()

    def clone(self):
        raise NotImplementedError()

    def toString(self):
        raise NotImplementedError()
