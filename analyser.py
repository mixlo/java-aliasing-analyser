#!/usr/bin/env python
import sys, gc
import networkx as nx
import matplotlib.pyplot as plt
import operator
from combinators import *


#simulating enum
class Opcodes:
    ALLOC = "1"
    FLOAD = "2"
    FSTORE = "3"
    MCALL = "4"
    DEALLOC = "5"
    MEXIT = "6"
    VSTORE = "7"


#INTERFACE
class LogEventInterface:
    #TBI
    pass


#REMEMBER NOT TO CONFUSE INTERFACE COMPONENTS WITH IMPLEMENTATION 
#SPECIFIC COMPONENTS

#THE INTERFACE MAYBE ONLY NEEDS THE METHODS THAT ARE ACTUALLY USED BY 
#EXTERNAL ACTIVITIES SUCH AS THE PROCESS AND EXECUTE METHODS ?

# An interface describing the base properties of the model.
# The model describes the state of the execution at a certain time.
# During initiation, it should be provided with some kind of query 
# templates/factories. These will be used to create a fresh set of the 
# queries for new objects added to the model.
class Model(object):
    # add_obj(obj_id)
    # TYPE: string * string -> void
    # Adds an object with ID obj_id to the model, then generates new 
    # queries and associates them with the object.
    def add_obj(self, obj_id, obj_type):
        raise NotImplementedError()
    def set_obj_type(self, obj_id, obj_type):
        raise NotImplementedError()
    def get_obj_type(self, obj_id):
        raise NotImplementedError();
    def add_stack_ref(self):
        raise NotImplementedError()
    def add_heap_ref(self):
        raise NotImplementedError()
    # remove_obj(obj_id)
    # TYPE: string -> void
    # Removes the object with ID obj_id from the model after saving 
    # its associated queries for the final measurements.
    def remove_obj(self, obj_id):
        raise NotImplementedError()
    def remove_stack_ref(self):
        raise NotImplementedError()
    def remove_heap_ref(self):
        raise NotImplementedError()
    def has_obj(self):
        raise NotImplementedError()
    def has_stack_ref(self):
        raise NotImplementedError()
    def has_heap_ref(self):
        raise NotImplementedError()
    def get_obj_ids(self):
        raise NotImplementedError()
    def get_obj_queries(self):
        raise NotImplementedError()
    def in_stack_refs(self):
        raise NotImplementedError()
    def in_heap_refs(self):
        raise NotImplementedError()
    def get_results(self):
        raise NotImplementedError()



# Implementation of model using a DiGraph from the networkx library
class GraphModel(Model):
    def __init__(self, qry_fs):
        self._g = nx.DiGraph()
        self.qry_fs = qry_fs
        self.results = {}

    def add_obj(self, obj_id, obj_type="(unknown)"):
        if self._g.has_node(obj_id): 
            raise Exception("add_obj: " \
                "Object {0} already exists".format(obj_id))
        self._g.add_node(obj_id, 
                         type=obj_type,
                         queries=[qf(obj_id) for qf in self.qry_fs])

    def set_obj_type(self, obj_id, obj_type):
        if not self._g.has_node(obj_id):
            raise Exception("set_obj_type: " \
                "Object {0} doesn't exist".format(obj_id))
        self._g.node[obj_id]["type"] = obj_type

    def get_obj_type(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("get_obj_type: " \
                "Object {0} doesn't exist".format(obj_id))
        return self._g.node[obj_id]["type"]

    def add_stack_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("add_stack_ref: " \
                "Referrer object {0} doesn't exist".format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("add_stack_ref: " \
                "Referee object {0} doesn't exist".format(referee_id))
        #if there aren't any edges yet
        if not self._g.has_edge(referrer_id, referee_id):
            self._g.add_edge(referrer_id, referee_id, stack=0, heap=0)
        self._g.edge[referrer_id][referee_id]["stack"] += 1

    def add_heap_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("add_heap_ref: " \
                "Referrer object {0} doesn't exist".format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("add_heap_ref: " \
                "Referee object {0} doesn't exist".format(referee_id))
        #if there aren't any edges yet
        if not self._g.has_edge(referrer_id, referee_id):        
            self._g.add_edge(referrer_id, referee_id, stack=0, heap=0)
        self._g.edge[referrer_id][referee_id]["heap"] += 1

    def remove_obj(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("remove_obj: " \
                "Object {0} doesn't exist".format(obj_id))
        if self.in_total_refs(obj_id) > 0:
            raise Exception("remove_obj: " \
                "Object {0} has incoming references".format(obj_id))
        if self.out_total_refs(obj_id) > 0:
            raise Exception("remove_obj: " \
                "Object {0} has outgoing references".format(obj_id))
        #Save queries and remove object
        self.results[obj_id] = \
            {"type" : self._g.node[obj_id]["type"], 
             "queries" : self._g.node[obj_id]["queries"]}
        self._g.remove_node(obj_id)

    def remove_stack_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("remove_stack_ref: " \
                "Referrer object {0} doesn't exist".format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("remove_stack_ref: " \
                "Referee object {0} doesn't exist".format(referee_id))
        if not self._g.has_edge(referrer_id, referee_id):
            raise Exception("remove_stack_ref: " \
                "Referrer {0} and referee {1} have no connection" \
                .format(referrer_id, referee_id))
        if self._g.edge[referrer_id][referee_id]["stack"] == 0:
            raise Exception("remove_stack_ref: " \
                "No references between referrer {0} and referee {1}" \
                .format(referrer_id, referee_id))
        self._g.edge[referrer_id][referee_id]["stack"] -= 1

    def remove_heap_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("remove_heap_ref: " \
                "Referrer object {0} doesn't exist".format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("remove_heap_ref: " \
                "Referee object {0} doesn't exist".format(referee_id))
        if not self._g.has_edge(referrer_id, referee_id):
            raise Exception("remove_heap_ref: " \
                "Referrer {0} and referee {1} have no connection" \
                .format(referrer_id, referee_id))
        if self._g.edge[referrer_id][referee_id]["heap"] == 0:
            raise Exception("remove_heap_ref: " \
                "No references between referrer {0} and referee {1}" \
                .format(referrer_id, referee_id))
        self._g.edge[referrer_id][referee_id]["heap"] -= 1

    def has_obj(self, obj_id):
        return self._g.has_node(obj_id)

    def has_stack_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("has_stack_ref: " \
                "Referrer object {0} doesn't exist".format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("has_stack_ref: " \
                "Referee object {0} doesn't exist".format(referee_id))
        return self._g.has_edge(referrer_id, referee_id) and \
               self._g.edge[referrer_id][referee_id]["stack"] > 0

    def has_heap_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("has_heap_ref: " \
                "Referrer object {0} doesn't exist".format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("has_heap_ref: " \
                "Referee object {0} doesn't exist".format(referee_id))
        return self._g.has_edge(referrer_id, referee_id) and \
               self._g.edge[referrer_id][referee_id]["heap"] > 0

    #Returns node array by value, not by reference
    def get_obj_ids(self):
        return self._g.nodes()

    #Returns queries by reference, to be able to apply them
    def get_obj_queries(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("get_obj_queries: " \
                "Object {0} doesn't exist".format(obj_id))
        return self._g.node[obj_id]["queries"]

    def in_stack_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("in_stack_refs: " \
                "Object {0} doesn't exist".format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"], 
                      self._g.in_edges(obj_id, data=True), 0)

    def in_heap_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("in_heap_refs: " \
                "Object {0} doesn't exist".format(obj_id))
        return reduce(lambda x,y: x + y[2]["heap"], 
                      self._g.in_edges(obj_id, data=True), 0)

    def in_total_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("in_total_refs: " \
                "Object {0} doesn't exist".format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"] + y[2]["heap"], 
                      self._g.in_edges(obj_id, data=True), 0)

    def out_stack_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("out_stack_refs: " \
                "Object {0} doesn't exist".format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"], 
                      self._g.out_edges(obj_id, data=True), 0)

    def out_heap_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("out_heap_refs: " \
                "Object {0} doesn't exist".format(obj_id))
        return reduce(lambda x,y: x + y[2]["heap"], 
                      self._g.out_edges(obj_id, data=True), 0)

    def out_total_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("out_total_refs: " \
                "Object {0} doesn't exist".format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"] + y[2]["heap"], 
                      self._g.out_edges(obj_id, data=True), 0)

    def get_results(self):
        return self.results.copy()


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
        if not model.has_obj(event[1]):
            model.add_obj(event[1], event[2])
        else:
            model.set_obj_type(event[1], event[2])
    elif event[0] == Opcodes.FLOAD:
        pass
    elif event[0] == Opcodes.FSTORE:
        if not model.has_obj(event[5]):
            model.add_obj(event[5])
        if event[3] != "0":
            model.remove_heap_ref(event[5], event[3])
        if event[2] != "0":
            model.add_heap_ref(event[5], event[2])
    elif event[0] == Opcodes.MCALL:
        # If methodOwner doesn't exist 
        # (e.g. when methodName is <init>)
        if not model.has_obj(event[3]):
            model.add_obj(event[3])
        for arg in event[4:]:
            # If passed argument doesn't exist 
            # (e.g. unallocated string object)
            if not model.has_obj(arg):
                model.add_obj(arg)
            model.add_stack_ref(event[3], arg)
    elif event[0] == Opcodes.DEALLOC:
        model.remove_obj(event[1])
    elif event[0] == Opcodes.MEXIT:
        for arg in event[5:]:
            if model.has_stack_ref(event[4], arg):
                model.remove_stack_ref(event[4], arg)
    elif event[0] == Opcodes.VSTORE:
        if event[2] != "0":
            model.remove_stack_ref(event[3], event[2])
        if event[1] != "0":
            model.add_stack_ref(event[3], event[1])
    else:
        raise Exception("OPCODE {0} NOT RECOGNISED".format(event[0]))
        

def execute(model, logevents):
    for event in logevents:
        process(model, event)
        for obj in model.get_obj_ids():
            for qry in model.get_obj_queries(obj):
                qry.apply()


#Theoretically, after all events are processed, no objects should 
#remain in the model, but it has to be taken into account that 
#deallocation doesn't work as expected. Also, due to the anomalies 
#in Erik's program, a set of incorrect queries is collected
#Returns: set of incorrect queries
def save_remaining_objs(model):
    #Get IDs of remaining objects
    remaining = model.get_obj_ids()
    incorrect_results = {}
    #TEST IF model.get_obj_ids RETURNS A NEW COPY EVERY ITERATION
    for obj in remaining:
        #Save queries and remove object
        if model.in_total_refs(obj) == 0 and \
           model.out_total_refs(obj) == 0:
            model.remove_obj(obj)
        else:
            incorrect_results[obj] = \
                {"type" : model.get_obj_type(obj),
                 "queries" : model.get_obj_queries(obj)}
    return incorrect_results


def print_results(results):
    zipped = zip(results.keys(), results.values())
    print "-"*50
    for obj_id, data in zipped:
        print "Object: {0}, Type: {1}".format(obj_id, data["type"])
        for qry in data["queries"]:
            print "\t[{0}] [{1}]  {2}".format(
                "A" if qry.isAccepting() else " ", 
                "F" if qry.isFrozen() else " ",
                qry.toString())
        print "-"*50


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

    print "Finished reading output file"

    #Create model and query factories

    #lambdas only take one argument, because right now, graph model 
    #only accepts queries that are run on each object by itself, not 
    #e.g. two objects in relation to each other
    qb = lambda o: Observe(lambda n: n <= 1, lambda: gm.in_total_refs(o))
    q1 = lambda o: Always(qb(o))
    q2 = lambda o: Not(Ever(Not(qb(o))))
    q3 = lambda o: Not(q1(o))
    q4 = lambda o: Any([q1(o), q3(o)])
    q5 = lambda o: All([q1(o), q3(o)])

    query_factories = [q1, q3, q5]
                       
    gm = GraphModel(query_factories)

    #Exeute everything
    execute(gm, logevents)
    #Save non-DEALLOCed objects and get incorrect queries
    incorrect_results = save_remaining_objs(gm)
    #Get correct queries
    correct_results = gm.get_results()
    
    print "FINISHED"

    print "\nCORRECT RESULTS"
    print_results(correct_results)
    print "\nINCORRECT RESULTS"
    print_results(incorrect_results)


if __name__ == "__main__":
    main()
