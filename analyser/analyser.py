#!/usr/bin/env python
import sys, os, gc, time
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


def parse_file(log_file):
    return [line.strip().split(" ") for line in log_file]


def parse_fn(log_fn):
    if not os.path.isfile(log_fn):
        raise Exception("LOG FILE {} DOESN'T EXIST".format(log_fn))
    with open(log_fn, "r") as log_file:
        return parse_file(log_file)


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
        # If caller doesn't exist
        # (should never happen, but has been observed in JVM startup events)
        if not model.has_obj(event[2]):
            model.add_obj(event[2])
        # If methodOwner doesn't exist 
        # (e.g. when methodName is <init>)
        if not model.has_obj(event[3]):
            model.add_obj(event[3])
        for arg in event[4:]:
            # If passed argument doesn't exist 
            # (e.g. unallocated string object)
            if not model.has_obj(arg):
                model.add_obj(arg)
            # Adding a stack reference from the method owner to the passed
            # object, since the method owner must have had a reference to the
            # object to be able to pass it.
            model.add_stack_ref(event[3], arg)
    elif event[0] == Opcodes.DEALLOC:
        model.remove_obj(event[1])
    elif event[0] == Opcodes.MEXIT:
        for arg in event[5:]:
            if model.has_stack_ref(event[4], arg):
                model.remove_stack_ref(event[4], arg)
    elif event[0] == Opcodes.VSTORE:
        # The event implies that there is a reference between caller and
        # oldObjID, but this must be verified due to an observed anomaly.
        if event[2] != "0" and model.has_stack_ref(event[3], event[2]):
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
# This function should be called after model.get_results() for correct results.
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


def format_time(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)
    

def run(model, fetch_rate=1, in_file=None, out_file="alidata.dat"):
    # Parse the events
    print "\nParsing input..."

    start = time.time()
    gc.disable()
    logevents = parse_fn(in_file) if in_file else parse_file(sys.stdin)
    gc.enable()
    end = time.time()
    
    print "Input parsing time: {}".format(format_time(end-start))
    print "\nExecuting with fetch rate {0}\n".format(fetch_rate)

    start = time.time()
    aliasing_data = execute(model, logevents, fetch_rate)
    end = time.time()

    print "\nFinished executing"
    print "Execution time: {}".format(format_time(end-start))

    # Write plotting data to file
    with open(out_file, "w") as f:
        for i,x in enumerate(aliasing_data):
            f.write("{0} {1} {2} {3}\n".format(
                i * fetch_rate / float(len(logevents)),
                max(x), min(x), sum(x) / float(len(x))))

    # Get results
    results = model.get_results()
    # Need to collect information about potentially remaining objects in model.
    get_remaining_results(model, results)    

    # Print results
    print_results(results, aliasing_data)
