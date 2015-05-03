class Query(object):
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


#TOSTRING METHOD? isAccepting and isFrozen
#Observe(comp_func, getter_1, getter_2, ..., getter_n)
# To avoid having direct references to functions and objects of the 
# graph, we use closures(?) (lambdas) that runs the functions on the 
# objects to get the necessary information. The returned value of each 
# closure represents an argument of the compare function. These 
# closures can therefore be (rather poorly) called "argument getters", 
# hence the names of the parameters used as input to the Observe class.
#EXAMPLE:
# q = Observe(comp_func = lambda n, m: n > m, 
#             getter_1 = lambda: count_stack_refs(obj1), 
#             getter_2 = lambda: count_heap_refs(obj1))
# -> q.apply()
# Step-by-step showing the value of self.state:
# -> comp_func(getter_1(), getter_2())
# -> comp_func(count_stack_refs(obj1), count_heap_refs(obj1))
# -> comp_func(3, 5) e.g.
# -> 3 > 5
# -> False
class Observe(Query):
    def __init__(self, tst, *arg_getters):
        self.tst = tst
        self.getters = arg_getters
        # State initial value?
        self.state = None
    def apply(self):
        self.state = self.tst(*[get() for get in self.getters])
    def isAccepting(self):
        return self.state
    def isFrozen(self):
        return False
    def clone(self):
        c = Observe(self.tst, *self.getters)
        c.state = self.state
        return c
    def toString(self):
        return "Observe(tst)"


class Not(Query):
    def __init__(self, q):
        self.q = q
    def apply(self):
        self.q.apply()
    def isAccepting(self):
        return not self.q.isAccepting()
    def isFrozen(self):
        return self.q.isFrozen()
    def clone(self):
        return Not(self.q.clone())
    def toString(self):
        return "Not({0})".format(self.q.toString())


class Ever(Query):
    def __init__(self, q):
        self.q = q
        self.success = False
    def apply(self):
        if self.success: return
        self.q.apply()
        if self.q.isAccepting(): self.success = True
    def isAccepting(self):
        return self.success
    def isFrozen(self):
        return self.success
    def clone(self):
        c = Ever(self.q.clone())
        c.success = self.success
        return c
    def toString(self):
        return "Ever({0})".format(self.q.toString())


#Always(q) == Not(Ever(Not(q)))
class Always(Query):
    def __init__(self, q):
        self.q = q
        self.failure = False
    def apply(self):
        if self.failure: return
        self.q.apply()
        if not self.q.isAccepting(): self.failure = True
    def isAccepting(self):
        return not self.failure
    def isFrozen(self):
        return self.failure
    def clone(self):
        c = Always(self.q.clone())
        c.failure = self.failure
        return c
    def toString(self):
        return "Always({0})".format(self.q.toString())


class Any(Query):
    def __init__(self, qs):
        self.qs = qs
    def apply(self):
        if self.isFrozen(): return
        map(lambda q: q.apply(), self.qs)
        #removing any query frozen in a non-accepting state
        self.qs = filter(lambda q: q.isAccepting() or 
                                   not q.isFrozen(), 
                         self.qs)
    def isAccepting(self):
        return any(map(lambda q: q.isAccepting(), self.qs))
    def isFrozen(self):
        any_succ = any(map(lambda q: q.isFrozen() and 
                                     q.isAccepting(), 
                           self.qs))
        all_fail = all(map(lambda q: q.isFrozen() and 
                                     not q.isAccepting(), 
                           self.qs))
        return any_succ or all_fail
    def clone(self):
        return Any(map(lambda q: q.clone(), self.qs))
    def toString(self):
        return "Any([{0}])" \
               .format(", ".join([q.toString() for q in self.qs]))


class All(Query):
    def __init__(self, qs):
        self.qs = qs
    def apply(self):
        if self.isFrozen(): return
        map(lambda q: q.apply(), self.qs)
        #removing any query frozen in an accepting state
        self.qs = filter(lambda q: not q.isAccepting() or \
                                   not q.isFrozen(), 
                         self.qs)
    def isAccepting(self):
        return all(map(lambda q: q.isAccepting(), self.qs))
    def isFrozen(self):
        any_fail = any(map(lambda q: q.isFrozen() and 
                                     not q.isAccepting(), 
                           self.qs))
        all_succ = all(map(lambda q: q.isFrozen() 
                                     and q.isAccepting(), 
                           self.qs))
        return any_fail or all_succ
    def clone(self):
        return All(map(lambda q: q.clone(), self.qs))
    def toString(self):
        return "All([{0}])" \
               .format(", ".join([q.toString() for q in self.qs]))
