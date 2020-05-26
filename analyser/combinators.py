#!/usr/bin/env python
import query

#TODO: Documentation

class Observe(query.Query):
    """ 
    Observe(comp_func, getter_1, getter_2, ..., getter_n)

    To avoid having direct references to functions and objects of the 
    graph, we use lambdas as closures that runs the functions on the 
    objects to get the necessary information. The returned value of each 
    closure represents an argument of the compare function. These 
    closures can therefore be (rather poorly) called "argument getters", 
    hence the names of the parameters used as input to the Observe class.

    EXAMPLE OF USE IN PROGRAM (PSEUDOCODE):
    -> m = <model instance>
    -> qf = lambda obj: Observe(comp_func = lambda x, y: x > y, 
                                getter_1 = lambda: m.count_stack_refs(obj),
                                getter_2 = lambda: m.count_heap_refs(obj))
    -> q = qf(<obj_id>)
    -> q.apply()
    -> q.state = comp_func(getter_1(), getter_2())
    -> q.state = comp_func(count_stack_refs(obj1), count_heap_refs(obj1))
    -> q.state = comp_func(3, 5) e.g.
    -> q.state = 3 > 5
    -> q.state = False
    """
    
    """
    def __init__(self, tst_str, *arg_getters):
        self.tst_str = tst_str[tst_str.index(":")+1:].strip(" ")
        self.tst = eval(tst_str)
        self.getters = arg_getters
        # State initial value?
        self.state = None
    """
    def __init__(self, name, tst):
        self.name = name
        self.tst = tst
        self.state = None

    """
    def apply(self):
        self.state = self.tst(*[get() for get in self.getters])
    """
    def apply(self):
        self.state = self.tst()
        
    def isAccepting(self):
        return self.state
    def isFrozen(self):
        return False
    
    """
    def clone(self):
        c = Observe(self.tst, *self.getters)
        c.state = self.state
        return c
    """
    def clone(self):
        c = Observe(self.name, self.tst)
        c.state = self.state
        return c
    
    """
    def toString(self):
        return self.tst_str
    """
    def toString(self):
        return self.name


class Not(query.Query):
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


class Ever(query.Query):
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
class Always(query.Query):
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


class Any(query.Query):
    def __init__(self, qs):
        self.qs = qs
        self.str_repr = "Any([{0}])" \
            .format(", ".join([q.toString() for q in qs]))
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
        return self.str_repr


class All(query.Query):
    def __init__(self, qs):
        self.qs = qs
        self.str_repr = "All([{0}])" \
            .format(", ".join([q.toString() for q in qs]))
    def apply(self):
        if self.isFrozen(): return
        map(lambda q: q.apply(), self.qs)
        # Removing any query frozen in an accepting state
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
        return self.str_repr


class Immediately(query.Query):
    def __init__(self, q):
        self.q = q
        self.done = False
    def apply(self):
        if self.done: return
        self.q.apply()
        self.done = True
    def isAccepting(self):
        return self.q.isAccepting()
    def isFrozen(self):
        return self.done
    def clone(self):
        c = Immediately(self.q.clone())
        c.done = self.done
        return c
    def toString(self):
        return "Immediately({0})".format(self.q.toString())
