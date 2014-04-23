import matplotlib.pyplot as plt
import networkx as nx
import igraph as ig
import graph_tool.all as gt
import time


def test_nx(test_size):
    start_time = time.time()
    g = nx.Graph()
    for i in xrange(test_size):
        g.add_node(i)
    for x in xrange(test_size-1):
        for y in xrange(x+1, test_size):
            g.add_edge(x, y)
    end_time = time.time()
    print "nx time:", end_time - start_time
    nx.draw(g)
    plt.savefig("nx_graph.png")


def test_ig(test_size):
    start_time = time.time()
    g = ig.Graph()
    for i in xrange(test_size):
        g.add_vertex()
    for x in xrange(test_size-1):
        for y in xrange(x+1, test_size):
            g.add_edge(x, y)
    end_time = time.time()
    print "ig time:", end_time - start_time
    ig.plot(g, "ig_graph.png")


def test_gt(test_size):
    start_time = time.time()
    g = gt.Graph(directed=False)
    for i in xrange(test_size):
        g.add_vertex()
    for x in xrange(test_size-1):
        for y in xrange(x+1, test_size):
            g.add_edge(x, y)
    end_time = time.time()
    print "gt time:", end_time - start_time
    gt.graph_draw(g, vertex_text=g.vertex_index, output="gt_graph.png")


def main():
    test_size = int(raw_input("Enter test size: "))
    test_nx(test_size)
    test_ig(test_size)
    test_gt(test_size)


if  __name__ == "__main__":
    main()
