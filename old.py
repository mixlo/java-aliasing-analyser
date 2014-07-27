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



#THIS WORKS BASED ON THE ASSUMPTION THAT
#TRANSITIONS' APPLY METHODS ARE BOOLEAN
#FUNCTIONS
class Query(object):
    def __init__(self, start_state):
        self.current_state = start_state
        self.failure = False
    def in_accepting_state(self):
        return self.current_state.accepting
    def apply(self, model, obj):
        transition_found = False
        for t in self.current_state.transitions:
            if t.apply(model, obj):
                self.current_state = t.target_state
                transition_found = True
                break
        if not transition_found:
            self.failure = True



class State(object):
    def __init__(self, accepting):
        self.accepting = accepting
        self.transitions = transitions
    def set_transitions(transitions):
        self.transitions = transitions



#INTERFACE
class Transition(object):
    def apply(self, model, obj):
        raise NotImplementedError()



class Whatever(Transition):
    def __init__(self, target_state):
        self.target_state = target_state
    def apply(self, model, obj_id):
        return True



#FURTHER GENERALIZATIONS IN THE FUTURE
#THE USER PROVIDES THE FUNCTION, ONE-ARGUMENT FUNCTION
#IMPLEMENTATION
class InDegree(Transition):
    def __init__(self, target_state, comp_func):
        self.target_state = target_state
        self.comp_func = comp_func
    def apply(self, model, obj_id):
        return self.comp_func(model.count_stack_refs(obj_id) + 
                              model.count_heap_refs(obj_id))



#IMPLEMENTATION
class StackInDegree(Transition):
    def __init__(self, target_state, comp_func):
        self.target_state = target_state
        self.comp_func = comp_func
    def apply(self, model, obj_id):
        return self.comp_func(model.count_stack_refs(obj_id))



#IMPLEMENTATION
class HeapInDegree(Transition):
    def __init__(self, target_state, comp_func):
        self.target_state = target_state
        self.comp_func = comp_func
    def apply(self, model, obj_id):
        return self.comp_func(model.count_heap_refs(obj_id))



class QueryFactory(object):
    def __init__(self, produce_function):
        self.produce_function = produce_function
    def produce(self):
        return self.produce_function()



def first_unique_then_aliased_query_function():
    s1 = State(False)
    s2 = State(True)

    t1 = InDegree(s1, lambda x: x <= 1)
    t2 = InDegree(s2, lambda x: x > 1)
    t3 = Whatever(s2)

    s1.set_transitions([t1, t2])
    s2.set_transitions([t3])

    return Query(s1)
