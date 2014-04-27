#!/usr/bin/env python
import sys, gc
import networkx as nx
import matplotlib.pyplot as plt
import operator


#simulating enum
class Opcodes(object):
    ALLOC = "1"
    FLOAD = "2"
    FSTORE = "3"
    MCALL = "4"
    DEALLOC = "5"
    MEXIT = "6"
    VSTORE = "7"


#INTERFACE
class LogEventInterface(object):
    #TBI
    pass


#INTERFACE
class Model(object):
    def add_obj(self, obj_id):
        raise NotImplementedError()
    def add_stack_ref(self, referrer_id, referee_id):
        raise NotImplementedError()
    def add_heap_ref(self, referrer_id, referee_id):
        raise NotImplementedError()
    def remove_obj(self, obj_id):
        raise NotImplementedError()
    def remove_stack_ref(self, referrer_id, referee_id):
        raise NotImplementedError()
    def remove_heap_ref(self, referrer_id, referee_id):
        raise NotImplementedError()
    def get_obj_ids(self):
        raise NotImplementedError()
    def count_stack_refs(self, obj_id):
        raise NotImplementedError()
    def count_heap_refs(self, obj_id):
        raise NotImplementedError()


#IMPLEMENTATION
class GraphModel(Model):
    def __init__(self):
        self._g = nx.MultiDiGraph()
    def add_obj(self, obj_id):
        self._g.add_node(obj_id)
    def add_stack_ref(self, referrer_id, referee_id):
        self._g.add_edge(referrer_id, referee_id, "stack")
        #TBI
    def add_heap_ref(self, referrer_id, referee_id):
        self._g.add_edge(referrer_id, referee_id, "heap")
        #TBI
    def remove_obj(self, obj_id):
        self._g.remove_node(obj_id)
    def remove_stack_ref(self, referrer_id, referee_id):
        #TBI
        pass
    def remove_heap_ref(self, referrer_id, referee_id):
        #TBI
        pass
    def get_obj_ids(self):
        #TBI
        pass
    def count_stack_refs(self, obj_id):
        #TBI
        pass
    def count_heap_refs(self, obj_id):
        #TBI
        pass


class State(object):
    def __init__(self, accepting, *transitions):
        self.accepting = accepting
        self.transitions = transitions


#INTERFACE
class Transition(object):
    def apply(self, model, obj):
        raise NotImplementedError()


#IMPLEMENTATION
class InDegree(Transition):
    def __init__(self, target_state, comp_func, comp_val):
        self.comp_func = comp_func
        self.comp_val = comp_val
        self.target_state = target_state
    def apply(self, model, obj_id):
        return self.comp_func(self.model.count_stack_refs(obj_id) + 
                              self.model.count_heap_refs(obj_id), 
                              self.comp_val)


#IMPLEMENTATION
class StackInDegree(Transition):
    def __init__(self, target_state, comp_func, comp_val):
        self.comp_func = comp_func
        self.comp_val = comp_val
        self.target_state = target_state
    def apply(self, model, obj_id):
        return self.comp_func(self.model.count_stack_refs(obj_id), 
                              self.comp_val)


#IMPLEMENTATION
class HeapInDegree(Transition):
    def __init__(self, target_state, comp_func, comp_val):
        self.comp_func = comp_func
        self.comp_val = comp_val
        self.target_state = target_state
    def apply(self, model, obj_id):
        return self.comp_func(self.model.count_heap_refs(obj_id), 
                              self.comp_val)


#IMPLEMENTATION
class Unique(Transition):
    def __init__(self, target_state):
        self.target_state = target_state
    def apply(self, model, obj_id):
        return InDegree(operator.le, 1).apply(model, obj_id)


#IS THIS A GOOD IMPLEMENTATION OF A QUERY?
class Query(object):
    def __init__(self, states):
        self.current_state = states[0]
        self.failure = False
    def apply(self, model, obj):
        for t in self.current_state.transitions:
            transition_found = False
            if t.apply(model, obj):
                self.current_state = t.target_state
                transition_found = True
                break
        if not transition_found:
            self.failure = True


#TODO: abstract event format
def parse():
    lines = []
    splitline = sys.stdin.readline().strip().split(" ")
    while splitline != [""]:
        lines.append(splitline)
        splitline = sys.stdin.readline().strip().split(" ")
    return lines


#TODO: adjust after abstract event format
def process(model, event, queries):
    if event[0] == Opcodes.ALLOC:
        model.add_obj(event[1])
    elif event[0] == Opcodes.FLOAD:
        pass
    elif event[0] == Opcodes.FSTORE:
        model.add_heap_ref(event[5], event[2])
        model.remove_heap_ref(event[5], event[3])
    elif event[0] == Opcodes.MCALL:
        pass
    elif event[0] == Opcodes.DEALLOC:
        model.remove_obj(event[1])
    elif event[0] == Opcodes.MEXIT:
        pass
    elif event[0] == Opcodes.VSTORE:
        model.add_stack_ref(event[3], event[1])
        model.remove_stack_ref(event[3], event[2])
    else:
        raise Exception("OPCODE " + event[0] + " NOT RECOGNISED")
        

#WHEN OBJECT IS DEALLOCATED, NEED TO SIGNAL QUERY 
#END OF INPUT, TO CHECK IF IN ACCEPTING STATE
def execute(model, logevents, queries):
    for event in logevents:
        process(model, event)
        #APPLY ALL QUERIES TO ALL OBJECTS?
        #IF SO, DOES EACH OBJECT NEED ITS OWN STATE/SET OF QUERIES?
        for obj_id in model.get_obj_ids():
            ...

def main():
    #Parse the events
    #TODO: fix parsed event format, abstraction
    gc.disable()
    logevents = parse()
    gc.enable()
    #DEBUG
    #sys.stdin = open("/dev/tty", "r")

    #Create model and queries
    gm = Graph_Model()
    s1 = State( False, InDegree(0, operator.le, 1), InDegree(1, operator.gt, 1) )
    s2 = State( True, InDegree(1, operator.gt, 1) )
    queries = [Query(s1, s2)]

    #Exeute everything
    execute(gm, logevents, queries)

    print "FINISHED"


if __name__ == "__main__":
    main()
