def create_graph(logevent_list):
    graph = nx.MultiDiGraph()
    for num, event in enumerate(logevent_list):
        if event[0] == Opcodes.ALLOC:
            #add allocated object to graph, nodeID == objID
            graph.add_node(event[1])
        elif event[0] == Opcodes.FLOAD:
            pass
        elif event[0] == Opcodes.FSTORE:
            #K (callee), holder of the field
            if event[2] != "0":
                graph.add_edge(event[5], event[2], "stack")
                #TODO: fix constants 5 and 2
                graph.edge[5][2]["stack"]["ref_num"] = graph.edge[5][2]["stack"].get("ref_num", 0) + 1
                graph.add_edge(event[5], event[2]) # K -----> Z
            if event[3] != "0":
                graph.remove_edge(event[5], event[3]) # K --/--> O
        elif event[0] == Opcodes.MCALL:
            pass
        elif event[0] == Opcodes.DEALLOC:
            pass
        elif event[0] == Opcodes.MEXIT:
            #stack references goes out of scope
            #for each reference, remove one edge?
            pass
        elif event[0] == Opcodes.VSTORE:
            #Z (callee), holder of the field
            if event[1] != "0":
                graph.add_edge(event[3], event[1]) # Z -----> X
            if event[2] != "0":
                graph.remove_edge(event[3], event[2]) # Z --/--> Y
        else:
            print "OPCODE NOT RECOGNISED:", event[0]
            raise Exception
        #DEBUG
        #nx.draw(graph)
        #plt.savefig("./img/" + str(num+2) + ".png")
        #plt.close()
        #print "klar med " + str(num)
        #DEBUG
        #print event
        #for n in graph.nodes():
        #    print n, graph.node[n]
        #raw_input()
    return graph
