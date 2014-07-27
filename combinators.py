class Query(object):
    def apply(self, evt):
        raise NotImplementedError()
    def isAccepting(self):
        raise NotImplementedError()
    def isFrozen(self):
        raise NotImplementedError()
    def clone(self):
        raise NotImplementedError()


class Observe(Query):
    def __init__(self, tst):
        self.tst = tst
        # State initial value?
        self.state = None
    def apply(self, evt):
        self.state = self.tst(evt)
    def isAccepting(self):
        return self.state
    def isFrozen(self):
        return False
    def clone(self):
        c = Observe(self.tst)
        c.state = self.state
        return c


class Not(Query):
    def __init__(self, q):
        self.q = q
    def apply(self, evt):
        self.q.apply(evt)
    def isAccepting(self):
        return not self.q.isAccepting()
    def isFrozen(self):
        return self.q.isFrozen()
    def clone(self):
        return Not(self.q.clone())


class Ever(Query):
    def __init__(self, q):
        self.q = q
        self.success = False
    def apply(self, evt):
        if self.success: return
        self.q.apply(evt)
        if self.q.isAccepting(): self.success = True
    def isAccepting(self):
        return self.success
    def isFrozen(self):
        return self.success
    def clone(self):
        c = Ever(self.q.clone())
        c.success = self.success
        return c


#Always(q) == Not(Ever(Not(q))) ???


class Always(Query):
    def __init__(self, q):
        self.q = q
        self.failure = False
    def apply(self, evt):
        if self.failure: return
        self.q.apply(evt)
        if not self.q.isAccepting(): self.failure = True
    def isAccepting(self):
        return not self.failure
    def isFrozen(self):
        return self.failure
    def clone(self):
        c = Always(self.q.clone())
        c.failure = self.failure
        return c


#I'm torn between the beauty of one-liners and the 80 cpl (/ 72 cpl) rule...
class Any(Query):
    def __init__(self, qs):
        self.qs = qs
    def apply(self, evt):
        if self.isFrozen(): return
        map(lambda q: q.apply(evt), self.qs)
        #removing any query frozen in a non-accepting state
        self.qs = filter(lambda q: q.isAccepting() or not q.isFrozen(), self.qs)
    def isAccepting(self):
        return any(map(lambda q: q.isAccepting(), self.qs))
    def isFrozen(self):
        any_succ = any(map(lambda q: q.isFrozen() and q.isAccepting(), self.qs))
        all_fail = all(map(lambda q: q.isFrozen() and not q.isAccepting(), self.qs))
        return any_succ or all_fail
    def clone(self):
        return Any(map(lambda q: q.clone(), self.qs))


class All(Query):
    def __init__(self, qs):
        self.qs = qs
    def apply(self, evt):
        if self.isFrozen(): return
        map(lambda q: q.apply(evt), self.qs)
        #removing any query frozen in an accepting state
        self.qs = filter(lambda q: not q.isAccepting() or not q.isFrozen(), self.qs)
    def isAccepting(self):
        return all(map(lambda q: q.isAccepting(), self.qs))
    def isFrozen(self):
        any_fail = any(map(lambda q: q.isFrozen() and not q.isAccepting(), self.qs))
        all_succ = all(map(lambda q: q.isFrozen() and q.isAccepting(), self.qs))
        return any_fail or all_succ
    def clone(self):
        return All(map(lambda q: q.clone(), self.qs))
