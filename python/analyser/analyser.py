#!/usr/bin/env python
import sys, gc
import graphmodel
from combinators import *


class Opcodes:
    ALLOC = "1"
    FLOAD = "2"
    FSTORE = "3"
    MCALL = "4"
    DEALLOC = "5"
    MEXIT = "6"
    VSTORE = "7"


def parse():
    lines = []
    splitline = sys.stdin.readline().strip().split(" ")
    while splitline != [""]:
        lines.append(splitline)
        splitline = sys.stdin.readline().strip().split(" ")
    return lines


def process(model, event):
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
#deallocation doesn't work as expected.
def get_remaining_results(model, results):
    remaining = model.get_obj_ids()
    for obj in remaining:
        results[obj] = \
            {"type" : model.get_obj_type(obj),
             "queries" : model.get_obj_queries(obj)}


def print_results(results):
    print "\nRESULTS\nA = Accepting, F = Frozen"
    zipped = zip(results.keys(), results.values())
    query_stats = {}
    print "-"*50
    for obj_id, data in zipped:
        print "OBJECT: {0}, TYPE: {1}".format(obj_id, data["type"])
        for qry in data["queries"]:
            query_stats[qry.toString()] = \
                query_stats.get(qry.toString(), 0) + qry.isAccepting()
            print "\t[{0}] [{1}]  {2}".format(
                "A" if qry.isAccepting() else " ", 
                "F" if qry.isFrozen() else " ",
                qry.toString())
        print "-"*50
    res_len = len(results)
    print "\nQueries in accepting state:"
    for qry in query_stats:
        print "{0}/{1} ~= {2}%\t{3}".format(
            query_stats[qry], 
            res_len, 
            round((float(query_stats[qry]) / float(res_len)) * 100, 2),
            qry)
    print


def main():
    #Parse the events
    gc.disable()
    logevents = parse()
    gc.enable()

    print "\nFinished reading output file"

    #Create model and query factories

    #lambdas only take one argument, because right now, graph model 
    #only accepts queries that are run on each object by itself, not 
    #e.g. two objects in relation to each other
    qb = lambda o: Observe("lambda in_total_refs: in_total_refs <= 1", lambda: gm.in_total_refs(o))
    q1 = lambda o: Always(qb(o))
    q2 = lambda o: Not(Ever(Not(qb(o))))
    q3 = lambda o: Not(q1(o))
    q4 = lambda o: Any([q1(o), q3(o)])
    q5 = lambda o: All([q1(o), q3(o)])

    query_factories = [q1, q3, q5]
                       
    gm = graphmodel.GraphModel(query_factories)

    #Exeute everything
    execute(gm, logevents)

    print "\nFinished executing"

    #Get results
    results = gm.get_results()
    get_remaining_results(gm, results)    

    #Print results
    print_results(results)
