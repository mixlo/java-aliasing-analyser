#!usr/bin/env python
import analyser
import graphmodel
from combinators import *
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import json
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


def print_query_results(results, verbose=False, out_file=sys.stdout):
    stdout = sys.stdout
    sys.stdout = out_file
    res_len = len(results)
    
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

    print "\nNumber of objects created during the execution:", res_len
    print "Queries in accepting state:"
    
    for qry in query_stats:
        print "{0: >X}/{1} ~= {2:6.2f}%\t{3}" \
            .replace("X", str(len(str(res_len)))) \
            .format(
                query_stats[qry], 
                res_len, 
                round((float(query_stats[qry]) / float(res_len)) * 100, 2),
                qry)

    sys.stdout = stdout


def plot_min_max_avg(min_max_avg_fn):
    df = pd.read_csv(min_max_avg_fn,
                     names=["Progress", "Min", "Max", "Avg"])
    fig = plt.figure(figsize=(12, 8))
    ax = plt.gca()
    df.plot(kind="line", x="Progress", y="Min", color="yellow", ax=ax)
    df.plot(kind="line", x="Progress", y="Max", color="red", ax=ax)
    df.plot(kind="line", x="Progress", y="Avg", color="blue", ax=ax)
    plt.title("Min, max and average incoming references "
              "to any given object during execution")
    plt.xlabel("Execution (%)")
    plt.ylabel("Incoming references")
    plt.savefig(min_max_avg_fn.rpartition(".")[0] + ".png", dpi=1000)
    plt.close(fig)


def plot_bltin_vs_custom(bltin_vs_custom_fn):
    df = pd.read_csv(bltin_vs_custom_fn,
                     names=["Progress", "Built-in", "Custom"])
    fig = plt.figure(figsize=(12, 8))
    ax = plt.gca()
    df.plot(kind="line", x="Progress", y="Built-in", color="blue", ax=ax)
    df.plot(kind="line", x="Progress", y="Custom", color="red", ax=ax)
    plt.title("Number of built-in and custom objects during the execution")
    plt.xlabel("Execution (%)")
    plt.ylabel("Number of objects")
    plt.savefig(bltin_vs_custom_fn.rpartition(".")[0] + ".png", dpi=1000)
    plt.close(fig)


def plot(plot_funcs):
    print "\nPlotting..."
    for pf in plot_funcs:
        pf()
    print "Done"


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

    in_file = lf
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    base = os.path.splitext(os.path.basename(in_file))[0]
    postfix = "{}_{}".format(now, base)
    data_dir = "../data"

    os.mkdir("{}/results_{}".format(data_dir, postfix))
    
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
    
    min_max_avg_fn = "{0}/results_{1}/min_max_avg_{1}.csv" \
                     .format(data_dir, postfix)
    bltin_vs_custom_fn = "{0}/results_{1}/bltin_vs_custom_{1}.csv" \
                         .format(data_dir, postfix)
    
    data_collectors = [
        (min_max_avg_fn,  min_max_avg, lambda x: str(x).strip("()")),
        (bltin_vs_custom_fn, bltin_vs_custom, lambda x: str(x).strip("()"))]

    plot_funcs = [
        lambda: plot_min_max_avg(min_max_avg_fn),
        lambda: plot_bltin_vs_custom(bltin_vs_custom_fn)]

    gm = graphmodel.GraphModel(query_factories, data_collectors)
    
    out_file = "{0}/results_{1}/query_results_{1}.txt".format(data_dir, postfix)
    of = open(out_file, "w")
    
    query_results = analyser.run(gm,
                                 in_file=in_file,
                                 query_rate=qr,
                                 collect_rate=cr,
                                 update_rate=ur)
    print_query_results(query_results, verbose=False, out_file=of)

    if not np:
        of.close()
        plot(plot_funcs)



if __name__ == "__main__":
    main()
