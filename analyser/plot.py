#!usr/bin/env python
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os


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
    plt.savefig(min_max_avg_fn.rpartition(".")[0] + ".png", dpi=300)
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
    plt.savefig(bltin_vs_custom_fn.rpartition(".")[0] + ".png", dpi=300)
    plt.close(fig)


def parse_args():
    prog_desc = ("Plot data collection results.")
    file_help = ("The results file.")
    func_help = ("The plot function in this module.")

    parser = argparse.ArgumentParser(prog="plot", description=prog_desc)
    parser.add_argument("file", help=file_help)
    parser.add_argument("func", help=func_help)
        
    args = parser.parse_args()
    pfile, pfunc = args.file, args.func

    if not os.path.isfile(pfile):
        parser.error("'{}' is not a file.".format(pfile))

    if pfunc not in globals():
        parser.error("Function '{}' doesn't exist.".format(pfunc))

    return pfile, globals()[pfunc]

    
def main():
    pfile, pfunc = parse_args()
    print "\nPlotting..."
    pfunc(pfile)
    print "Done"



if __name__ == "__main__":
    main()
