#!usr/bin/env python
import analyser
import graphmodel
from combinators import *
import numpy as np
import matplotlib.pyplot as plt


# Implemented by API:
# ----
# Analyser
# Model interface
# Combinators

# Implemented by user:
# ---
# A model based on Model interface, e.g. graphmodel.py

# 1. Create queries using Combinators
# 2. Create instance of own implementation of Model interface,
#    passing the queries as arguments
# 3. run analyser.execute(filename, model, fetch_rate, out_file="alidata.dat")


def plot(in_file="alidata.dat", out_file="aliplot.png"):
    alidata = np.loadtxt(in_file)
    plt.plot(alidata[:,0], alidata[:,1], label="max")
    plt.plot(alidata[:,0], alidata[:,2], label="min")
    plt.plot(alidata[:,0], alidata[:,3], label="avg")
    #plt.savefig(out_file)
    plt.title("Max, min and average incoming references "
              "to any given object during execution")
    plt.xlabel("Execution (%)")
    plt.ylabel("Incoming references")
    plt.legend()
    plt.savefig(out_file)
    plt.show()


def main():
    #Create model and query factories

    #lambdas only take one argument, because right now, graph model 
    #only accepts queries that are run on each object by itself, not 
    #e.g. two objects in relation to each other
    qb = lambda o: Observe("lambda in_total_refs: in_total_refs <= 1", 
                           lambda: gm.in_total_refs(o))

    # Query to check for dominators
    qb2 = lambda o: Observe()

    # Checks whether objects are never referenced by more than one object at
    # the same time (objects' incoming references are always 1 or 0 at any
    # given time during the execution). Will freeze if condition is broken.
    q1 = lambda o: Always(qb(o))

    # Checks whether it's not ever the case that an object is referenced by
    # more than 1 object at a given time during the execution. Logically equal
    # to q1.
    q2 = lambda o: Not(Ever(Not(qb(o))))

    # Checks whether objects are referenced by more than 1 object at a given
    # time during the execution. Won't freeze.
    q3 = lambda o: Not(q1(o))

    # Checks if any of q1 and q3 holds at a given time during the execution.
    # Will freeze if q1 or a3 freezes in a condition such that q4's
    # condition can never change (e.q. q4 will freeze in accepting state if q1
    # freezes in an accepting state).
    q4 = lambda o: Any([q1(o), q3(o)])

    # Checks if both q1 and q3 holds at the same time, at any time during the
    # execution. Will freeze if q1 or a3 freezes in a condition such that q5's
    # condition can never change (e.q. q5 will freeze in a non-accepting state
    # if q1 freezes in a non-accepting state).
    q5 = lambda o: All([q1(o), q3(o)])

    query_factories = [q1, q3, q5]
    gm = graphmodel.GraphModel(query_factories)

    # This will print query results and min, max, avg incoming references
    # during the execution to the terminal, and also print the information
    # about incoming references to the specified output filename. This file
    # can then be used for plotting.
    analyser.run(gm)

    plot()


if __name__ == "__main__":
    main()
