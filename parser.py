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


class Log_Event_Interface:
    #TBI
    pass


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
