#!/usr/bin/env python
import sys, gc, time
import graphmodel
from combinators import *

#TODO: Documentation

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
        

def execute(model, logevents, fetch_rate = None):
    data = []
    for i, event in enumerate(logevents):
        if i % 1000 == 0:
            print "Processing line", i
        process(model, event)
        objs = model.get_obj_ids()
        if fetch_rate and i % fetch_rate == 0:
            data.append([model.in_total_refs(o) for o in objs])
        for obj in objs:
            for qry in model.get_obj_queries(obj):
                qry.apply()
    return data


#Theoretically, after all events are processed, no objects should 
#remain in the model, but it has to be taken into account that 
#deallocation doesn't work as expected.
def get_remaining_results(model, results):
    remaining = model.get_obj_ids()
    for obj in remaining:
        results[obj] = \
            {"type" : model.get_obj_type(obj),
             "queries" : model.get_obj_queries(obj)}


def print_results(results, ali_data, verbose = False):
    print "\n", "-"*50
    print "\nRESULTS"

    if verbose:
        print "\nA = Accepting, F = Frozen"
        print "-"*50

    zipped = zip(results.keys(), results.values())
    query_stats = {}
    for obj_id, data in zipped:
        if verbose:
            print "OBJECT: {0}, TYPE: {1}".format(obj_id, data["type"])
        for qry in data["queries"]:
            query_stats[qry.toString()] = \
                query_stats.get(qry.toString(), 0) + qry.isAccepting()
            if verbose:
                print "\t[{0}] [{1}]  {2}".format(
                    "A" if qry.isAccepting() else " ", 
                    "F" if qry.isFrozen() else " ",
                    qry.toString())
        if verbose:
            print "-"*50

    print "\nQueries in accepting state:"
    res_len = len(results)
    for qry in query_stats:
        print "{0}/{1} ~= {2}%\t{3}".format(
            query_stats[qry], 
            res_len, 
            round((float(query_stats[qry]) / float(res_len)) * 100, 2),
            qry)

    if ali_data:
        print "\nAliasing data:"
        max_ir = max(map(lambda x: max(x), ali_data))
        min_ir = min(map(lambda x: min(x), ali_data))
        avg_ir = sum(map(lambda x: sum(x)/float(len(x)), ali_data))/ \
              float(len(ali_data))
        print "Max incoming references:", max_ir
        print "Min incoming references:", min_ir
        print "Avg incoming references:", avg_ir

    print


def main():
    #Parse the events
    print "\nParsing input..."

    start = int(time.time())
    gc.disable()
    logevents = parse()
    gc.enable()
    end = int(time.time())

    m, s = divmod(end-start, 60)
    h, m = divmod(m, 60)
    print "Input parsing time: {0:02d}:{1:02d}:{2:02d}" \
        .format(h, m, s)

    #Create model and query factories

    #lambdas only take one argument, because right now, graph model 
    #only accepts queries that are run on each object by itself, not 
    #e.g. two objects in relation to each other
    qb = lambda o: Observe("lambda in_total_refs: in_total_refs <= 1", 
                           lambda: gm.in_total_refs(o))

    q1 = lambda o: Always(qb(o))
    q2 = lambda o: Not(Ever(Not(qb(o))))
    q3 = lambda o: Not(q1(o))
    q4 = lambda o: Any([q1(o), q3(o)])
    q5 = lambda o: All([q1(o), q3(o)])

    query_factories = [q1, q3, q5]
                       
    gm = graphmodel.GraphModel(query_factories)

    #Exeute everything
    fetch_rate = 1
    print "\nExecuting with fetch rate {0}\n".format(fetch_rate)
    aliasing_data = execute(gm, logevents, fetch_rate)

    print "\nFinished executing"

    #Write plotting data to file
    f = open("aliasing_data.dat", "w")
    for i,x in enumerate(aliasing_data):
        f.write("{0} {1} {2} {3}\n".format(
            i * fetch_rate, max(x), min(x), sum(x)/float(len(x))))
    f.close()

    #Get results
    results = gm.get_results()
    get_remaining_results(gm, results)    

    #Print results
    print_results(results, aliasing_data)
