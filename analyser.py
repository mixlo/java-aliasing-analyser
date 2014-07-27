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
    def add_obj(self, obj_id, queries):
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
    def get_obj_queries(self, obj_id):
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


#TODO: abstract event format
def parse():
    lines = []
    splitline = sys.stdin.readline().strip().split(" ")
    while splitline != [""]:
        lines.append(splitline)
        splitline = sys.stdin.readline().strip().split(" ")
    return lines


#TODO: adjust after abstract event format
def process(model, event, query_factories):
    if event[0] == Opcodes.ALLOC:
        model.add_obj(event[1], [qf.produce() for qf in query_factories])
    elif event[0] == Opcodes.FLOAD:
        pass
    elif event[0] == Opcodes.FSTORE:
        model.add_heap_ref(event[5], event[2])
        model.remove_heap_ref(event[5], event[3])
    elif event[0] == Opcodes.MCALL:
        pass
    elif event[0] == Opcodes.DEALLOC:
        obj_queries = model.get_obj_queries(event[1])
        for query in obj_queries:
            if query.in_accepting_state():
                #WHAT DO WE DO WITH SUCCESSFUL QUERIES???
                #A COUNTER FOR EACH FACTORY, COUNTING 
                #THE SUCCESFFUL QUERIES
        model.remove_obj(event[1])
    elif event[0] == Opcodes.MEXIT:
        pass
    elif event[0] == Opcodes.VSTORE:
        model.add_stack_ref(event[3], event[1])
        model.remove_stack_ref(event[3], event[2])
    else:
        raise Exception("OPCODE {0} NOT RECOGNISED".format(event[0]))
        

def execute(model, logevents, query_factories):
    for event in logevents:
        process(model, event, query_factories)
        #THIS FEELS MESSED UP, DIRECT REFERENCE TO QUERY AND LOUSY 
        #TIME COMPLEXITY IF WE HAVE TO RUN THIS FOR EVERY LOGEVENT
        for obj_id in model.get_obj_ids():
            obj_queries = model.get_obj_queries(obj_id)
            #CONSIDER FILTERING
            map(lambda q: model.remove_query(obj_id, q) if q.failure else pass,
                obj_queries)
            for query in obj_queries:
                if query.failure:
                    model.remove_query(obj_id, query)


#KEEPING A DICTIONARY OF THE OBJECTS WHERE THE VALUES ARE COLLECTIONS OF 
#QUERIES IS NOT VIABLE IF WE ARE NOT RUNNING THE QUERIES IN TERMS OF 
#OBJECTS, BUT RATHER THE WHOLE MODEL, EG HOW MANY WAYS CAN WE TRAVEL THE 
#GRAPH TO GET FROM A POSITION TO ANOTHER? THAT IS, WE MIGHT WANT TO 
#APPLY QUERIES THAT DOES NOT ONLY CONCERN A SINGLE SPECIFIC OBJECT.
def main():
    #Parse the events
    #TODO: fix parsed event format, abstraction
    gc.disable()
    logevents = parse()
    gc.enable()
    #DEBUG
    #sys.stdin = open("/dev/tty", "r")

    #Create model and query factories
    gm = Graph_Model()
    query_factories = {QueryFactory(first_unique_then_aliased_query_function)}

    #Exeute everything
    execute(gm, logevents, query_factories)

    print "FINISHED"


if __name__ == "__main__":
    main()
