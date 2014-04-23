#!/usr/bin/env python
import sys, gc
import networkx as nx
import matplotlib.pyplot as plt


#simulating enum
class Opcodes:
    ALLOC = "1"
    FLOAD = "2"
    FSTORE = "3"
    MCALL = "4"
    DEALLOC = "5"
    MEXIT = "6"
    VSTORE = "7"


class Model_Interface:
    def add_obj(self, obj_id):
        raise NotImplementedError
    def add_stack_ref(self, referrer_id, referee_id):
        raise NotImplementedError
    def add_heap_ref(self, referrer_id, referee_id):
        raise NotImplementedError
    def remove_obj(self, obj_id):
        raise NotImplementedError
    def remove_stack_ref(self, referrer_id, referee_id):
        raise NotImplementedError
    def remove_heap_ref(self, referrer_id, referee_id):
        raise NotImplementedError


class Graph_Model(Model_Interface):
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


class Log_Event_Interface:
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
def process_logevent(event, model):
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


#DEPRECATED
def create_graph(logevent_list):
    graph = nx.MultiDiGraph()
    for num, event in enumerate(logevent_list):
        if event[0] == Opcodes.ALLOC:
            #add allocated object to graph, nodeID == objID
            graph.add_node(event[1])
        elif event[0] == Opcodes.FLOAD:
            pass
        elif event[0] == Opcodes.FSTORE:
            #K (callee), holder of the field
            if event[2] != "0":
                graph.add_edge(event[5], event[2], "stack")
                #TODO: fix constants 5 and 2
                graph.edge[5][2]["stack"]["ref_num"] = graph.edge[5][2]["stack"].get("ref_num", 0) + 1
                graph.add_edge(event[5], event[2]) # K -----> Z
            if event[3] != "0":
                graph.remove_edge(event[5], event[3]) # K --/--> O
        elif event[0] == Opcodes.MCALL:
            pass
        elif event[0] == Opcodes.DEALLOC:
            pass
        elif event[0] == Opcodes.MEXIT:
            #stack references goes out of scope
            #for each reference, remove one edge?
            pass
        elif event[0] == Opcodes.VSTORE:
            #Z (callee), holder of the field
            if event[1] != "0":
                graph.add_edge(event[3], event[1]) # Z -----> X
            if event[2] != "0":
                graph.remove_edge(event[3], event[2]) # Z --/--> Y
        else:
            print "OPCODE NOT RECOGNISED:", event[0]
            raise Exception
        #DEBUG
        #nx.draw(graph)
        #plt.savefig("./img/" + str(num+2) + ".png")
        #plt.close()
        #print "klar med " + str(num)
        #DEBUG
        #print event
        #for n in graph.nodes():
        #    print n, graph.node[n]
        #raw_input()
    return graph


def main():
    gc.disable()
    logevents = parse()
    gc.enable()
    #DEBUG
    #sys.stdin = open("/dev/tty", "r")
    gm = Graph_Model()
    for le in logevents:
        process_logevent(le, gm)
    print "FINISHED"


if __name__ == "__main__":
    main()
