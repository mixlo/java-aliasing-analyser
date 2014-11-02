#!/usr/bin/env python
import sys, gc
import networkx as nx
import matplotlib.pyplot as plt
import operator
from combinators_new import *


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
    def add_obj(self):
        raise NotImplementedError()
    def add_stack_ref(self):
        raise NotImplementedError()
    def add_heap_ref(self):
        raise NotImplementedError()
    def remove_obj(self):
        """store finished queries and remove object"""
        raise NotImplementedError()
    def remove_stack_ref(self):
        raise NotImplementedError()
    def remove_heap_ref(self):
        raise NotImplementedError()
    def has_obj(self):
        raise NotImplementedError()
    def get_obj_ids(self):
        raise NotImplementedError()
    def get_obj_queries(self):
        raise NotImplementedError()
    def count_stack_refs(self):
        raise NotImplementedError()
    def count_heap_refs(self):
        raise NotImplementedError()
    def get_finished_queries(self):
        raise NotImplementedError()


#IMPLEMENTATION
class GraphModel(Model):
    def __init__(self, qry_fs):
        self._g = nx.DiGraph()
        self.qry_fs = qry_fs
        self.finished_queries = {}

    def add_obj(self, obj_id):
        #static objects are only detected when adding refs
        self._g.add_node(obj_id, queries=[qf(obj_id) for qf in self.qry_fs])

    def add_stack_ref(self, referrer_id, referee_id):
        #if referee_id == 0, it's a primitive type and shouldn't be in model
        if referee_id == "0": return
        #referrer might be a static class that hasn't been added
        if referrer_id not in self._g.nodes():
            self._g.add_node(referrer_id, 
                             queries=[qf(referrer_id) for qf in self.qry_fs])
        #if there aren't any edges yet
        if referee_id not in self._g.edge[referrer_id]:
            self._g.add_edge(referrer_id, referee_id, stack=0, heap=0)
        self._g.edge[referrer_id][referee_id]["stack"] += 1

    def add_heap_ref(self, referrer_id, referee_id):
        #if referee_id == 0, it's a primitive type and shouldn't be in model
        if referee_id == "0": return
        #referrer might be a static class that hasn't been added
        if referrer_id not in self._g.nodes():
            self._g.add_node(referrer_id, 
                             queries=[qf(referrer_id) for qf in self.qry_fs])
        #if there aren't any edges yet
        if referee_id not in self._g.edge[referrer_id]:
            self._g.add_edge(referrer_id, referee_id, stack=0, heap=0)
        self._g.edge[referrer_id][referee_id]["heap"] += 1

    def remove_obj(self, obj_id):
        self.finished_queries[obj_id] = self._g.node[obj_id]["queries"]
        self._g.remove_node(obj_id)

    def remove_stack_ref(self, referrer_id, referee_id):
        #referee_id might be 0 or name of a static class ???
        if referee_id in self._g.nodes():
            #no need to check below 0, logically impossible
            self._g.edge[referrer_id][referee_id]["stack"] -= 1
            #"deallocation" work-around
            if self.count_stack_refs(referee_id) == 0 and \
               self.count_heap_refs(referee_id) == 0:
                self.remove_obj(referee_id)

    def remove_heap_ref(self, referrer_id, referee_id):
        #referee_id might be 0 or name of a static class ???
        if referee_id in self._g.nodes():
            #no need to check below 0, logically impossible
            self._g.edge[referrer_id][referee_id]["heap"] -= 1
            #"deallocation" work-around
            if self.count_stack_refs(referee_id) == 0 and \
               self.count_heap_refs(referee_id) == 0:
                self.remove_obj(referee_id)

    def has_obj(self, obj_id):
        return self._g.has_node(obj_id);

    def get_obj_ids(self):
        return self._g.nodes()

    def get_obj_queries(self, obj_id):
        return self._g.node[obj_id]["queries"]

    def count_stack_refs(self, obj_id):
        return reduce(lambda x,y: x + y[2]["stack"], 
                      self._g.in_edges(nbunch=obj_id, data=True), 0)

    def count_heap_refs(self, obj_id):
        return reduce(lambda x,y: x + y[2]["heap"], 
                      self._g.in_edges(nbunch=obj_id, data=True), 0)

    def get_finished_queries(self):
        return self.finished_queries


#TODO: abstract event format
def parse():
    lines = []
    splitline = sys.stdin.readline().strip().split(" ")
    while splitline != [""]:
        lines.append(splitline)
        splitline = sys.stdin.readline().strip().split(" ")
    return lines


#TODO: adjust after abstract event format
def process(model, event):
    print "obj_ids",
    print model.get_obj_ids()
    print "event",
    print event
    if event[0] == Opcodes.ALLOC:
        model.add_obj(event[1])
    elif event[0] == Opcodes.FLOAD:
        pass
    elif event[0] == Opcodes.FSTORE:
        model.remove_heap_ref(event[5], event[3])
        model.add_heap_ref(event[5], event[2])
    elif event[0] == Opcodes.MCALL:
        #Strings should be treated as primitive objects, see notes
        for arg in event[4:]:
            if model.has_obj(arg):
                model.add_stack_ref(event[3], arg);
    elif event[0] == Opcodes.DEALLOC:
        #model.remove_obj(event[1])
        #see notes
        pass
    elif event[0] == Opcodes.MEXIT:
        map(lambda obj_id: model.remove_stack_ref(event[4], obj_id), event[5:])
    elif event[0] == Opcodes.VSTORE:
        model.remove_stack_ref(event[3], event[2])
        model.add_stack_ref(event[3], event[1])
    else:
        raise Exception("OPCODE {0} NOT RECOGNISED".format(event[0]))
        

def execute(model, logevents):
    for event in logevents:
        process(model, event)
        for obj in model.get_obj_ids():
            for qry in model.get_obj_queries(obj):
                qry.apply()
            

# sed -n "47, 71p" output | python analyser.py

#KEEPING A DICTIONARY OF THE OBJECTS WHERE THE VALUES ARE COLLECTIONS OF 
#QUERIES IS NOT VIABLE IF WE ARE NOT RUNNING THE QUERIES IN TERMS OF 
#OBJECTS, BUT RATHER THE WHOLE MODEL, EG HOW MANY WAYS CAN WE TRAVEL THE 
#GRAPH TO GET FROM A POSITION TO ANOTHER? THAT IS, WE MIGHT WANT TO 
#APPLY QUERIES THAT DO NOT ONLY CONCERN A SINGLE SPECIFIC OBJECT.
def main():
    #Parse the events
    #TODO: fix parsed event format, abstraction
    gc.disable()
    logevents = parse()
    gc.enable()
    #DEBUG
    #sys.stdin = open("/dev/tty", "r")

    #Create model and query factories
    query_factories = [lambda o: Always(Observe(lambda n: n <= 1, 
                                                lambda: gm.count_heap_refs(o)))]
    gm = GraphModel(query_factories)

    #Exeute everything
    execute(gm, logevents)
    
    #WE REACH END OF EXECUTION WITH SUCCESS(?)!! EXAMINE RESULTS!
    print "FINISHED"
    print gm.get_finished_queries()


if __name__ == "__main__":
    main()
