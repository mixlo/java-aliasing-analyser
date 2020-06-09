#!usr/bin/env python
import analyser
import graphmodel
from combinators import *
import plot
import sys
import os
import datetime
import argparse


# Implemented by API:
# ----
# Analyser
# Model interface
# Combinators

# Implemented by user:
# ---
# A model based on Model interface, e.g. graphmodel.py
# A script such as this one that executes the analyser with an instance of the
# model, provided with query factories, data collectors and other parameters.


def str_to_int(s):
    try:
        return int(s)
    except:
        return -1


def print_query_results(results, exec_info, verbose=False, out_file=sys.stdout):
    stdout = sys.stdout
    sys.stdout = out_file
    res_len = len(results)

    padding = len(str(max(exec_info["query_rate"], exec_info["collect_rate"])))
    print "\nEXECUTION PARAMETERS\n"
    if exec_info["log_fn"]:
        print "-- Input file   = {}".format(exec_info["log_fn"])
    print     "-- Query rate   = {: >PAD}".replace("PAD", str(padding)) \
                                          .format(exec_info["query_rate"])
    print     "-- Collect rate = {: >PAD}".replace("PAD", str(padding)) \
                                          .format(exec_info["collect_rate"])
    
    print "\n", "-"*50
    print "\nRESULTS"

    if verbose:
        print "\nA = Accepting, F = Frozen"
        print "-"*50
    
    query_stats = {}
    zipped = sorted(zip(results.keys(), results.values()),
                    key=lambda tup: str_to_int(tup[0]))
    
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

    print "\nExecution time:", exec_info["exec_time"]
    print "Number of objects created during the execution:", res_len
    print "Queries in accepting state:\n"
    
    for qry in query_stats:
        print "{0: >X}/{1} ~= {2:6.2f}%\t{3}" \
            .replace("X", str(len(str(res_len)))) \
            .format(
                query_stats[qry], 
                res_len, 
                round((float(query_stats[qry]) / float(res_len)) * 100, 2),
                qry)

    sys.stdout = stdout


def min_max_avg(model):
    try:
        inc_refs = [model.in_total_refs(o) for o in model.get_obj_ids()]
        return min(inc_refs), max(inc_refs), sum(inc_refs)/float(len(inc_refs))
    except:
        return 0, 0, 0.0


def bltin_vs_custom(model):
    b, c = 0, 0
    for o in model.get_obj_ids():
        if model.is_builtin(o):
            b += 1
        else:
            c += 1
    return b, c
    

def rate_type(num):
    x = int(num)
    if x < 1:
        raise argparse.ArgumentTypeError("Minimum rate is 1.")
    return x


def parse_args():
    prog_desc = ("Execute the the Java aliasing analyser with specified "
                 "parameters.")
    lf_help = ("The logfile to be parsed.")
    qr_help = ("The query rate. Default is 1.")
    cr_help = ("The collect rate. Default is 1.")
    ur_help = ("The update rate. Default is 1.")
    np_help = ("Determines whether to plot the data after execution.")
    
    parser = argparse.ArgumentParser(prog="test", description=prog_desc)
    parser.add_argument("logfile",
                        help=lf_help)
    parser.add_argument("-q", "--qrate",
                        help=qr_help, type=rate_type, default=1)
    parser.add_argument("-c", "--crate",
                        help=cr_help, type=rate_type, default=1)
    parser.add_argument("-u", "--urate",
                        help=ur_help, type=rate_type, default=1000)
    parser.add_argument("-n", "--noplot",
                        help=np_help, action="store_true")
    
    args = parser.parse_args()
    lf, qr, cr, ur, np = (args.logfile,
                          args.qrate,
                          args.crate,
                          args.urate,
                          args.noplot)

    if not os.path.isfile(lf):
        parser.error("'{}' is not a file.".format(lf))

    return lf, qr, cr, ur, np


def main():
    lf, qr, cr, ur, np = parse_args()

    log_fn = lf
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    base = os.path.splitext(os.path.basename(log_fn))[0]
    postfix = "{}-{}".format(now, base)
    results_dir = "../data/results-{}".format(postfix)

    os.mkdir(results_dir)
    
    #Create model and query factories

    unaliased = lambda m, o: \
                Observe("Object is unaliased",
                        lambda: m.in_total_refs(o) <= 1)
    is_builtin = lambda m, o: \
                 Observe("Object is built-in",
                         lambda: m.is_builtin(o))
    le4_incs = lambda m, o: \
               Observe("Object has <= 4 incoming references",
                       lambda: m.in_total_refs(o) <= 4)
    
    always_unaliased = lambda m, o: Always(unaliased(m, o))
    custom_obj = lambda m, o: Immediately(Not(is_builtin(m, o)))
    custom_le4_inc_refs = lambda m, o: All([custom_obj(m, o),
                                            Always(le4_incs(m, o))])
    
    query_factories = [always_unaliased,
                       custom_obj,
                       custom_le4_inc_refs]
    
    min_max_avg_fn = "{0}/min_max_avg-{1}.csv" \
                     .format(results_dir, postfix)
    bltin_vs_custom_fn = "{0}/bltin_vs_custom-{1}.csv" \
                         .format(results_dir, postfix)
    
    data_collectors = [
        (min_max_avg_fn,     min_max_avg,     lambda x: str(x).strip("()")),
        (bltin_vs_custom_fn, bltin_vs_custom, lambda x: str(x).strip("()"))]

    gm = graphmodel.GraphModel(query_factories, data_collectors)
    
    out_file = "{0}/query_results-{1}.txt".format(results_dir, postfix)
    of = open(out_file, "w")
    
    query_results, exec_info = analyser.run(gm,
                                            log_fn=log_fn,
                                            query_rate=qr,
                                            collect_rate=cr,
                                            update_rate=ur)
    
    print_query_results(query_results, exec_info, verbose=False, out_file=of)
    of.close()

    if not np:
        print "\nPlotting..."
        plot.plot_min_max_avg(min_max_avg_fn)
        plot.plot_bltin_vs_custom(bltin_vs_custom_fn)
        print "Done"



if __name__ == "__main__":
    main()
