#!/usr/bin/env python
import sys, os, gc, time, json
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
            # Shouldn't happen, but most often in the logs, the object
            # constructor method event (4) is run before allocation event (1),
            # meaning that the object is has to be added to the graph without
            # a type, and then have it set in this following allocation event.
            # Since this is the allocation event, and therefore the first time
            # the object SHOULD be observed, it makes sense to reset the
            # object's queries, whatever they were up until this moment.
            model.set_obj_type(event[1], event[2])
            model.reset_obj_queries(event[1])
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
        #raise Exception("OPCODE {0} NOT RECOGNISED".format(event[0]))
        print "ERROR: OPCODE {0} NOT RECOGNISED".format(event[0])
        

def execute(model, log_events, query_rate=1, collect_rate=1, update_rate=1000):
    for i, event in enumerate(log_events):
        if i % update_rate == 0:
            print "Processing line", i
            
        if i % collect_rate == 0:
            model.collect_data(i / float(len(log_events)))
            
        process(model, event)
        
        if i % query_rate == 0:
            for obj in model.get_obj_ids():
                for qry in model.get_obj_queries(obj):
                    qry.apply()
    
    model.collect_data(1.0)


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


def format_time(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)
    

def run(model, in_file=None, query_rate=1, collect_rate=1, update_rate=1000):
    # Parse the events
    print "Parsing input..."

    start = time.time()
    gc.disable()
    log_events = parse_fn(in_file) if in_file else parse_file(sys.stdin)
    gc.enable()
    end = time.time()
    
    print "\nExecuting with parameters:"
    if in_file:
        print "-- in_file = {}".format(in_file)
    print "-- query_rate = {}".format(query_rate)
    print "-- collect_rate = {}".format(collect_rate)
    print "-- update_rate = {}".format(update_rate)
    print

    start = time.time()
    execute(model,
            log_events,
            query_rate=query_rate,
            collect_rate=collect_rate,
            update_rate=update_rate)
    end = time.time()

    print "\nFinished executing"
    print "Execution time: {}".format(format_time(end-start))

    # Get results
    results = model.get_results()
    # Need to collect information about potentially remaining objects in model.
    get_remaining_results(model, results)

    return results
