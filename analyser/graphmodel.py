#!/usr/bin/env python
import model
import networkx as nx

#TODO: Documentation

# Implementation of model using a DiGraph from the networkx library
class GraphModel(model.Model):
    # Can't use ref_dealloc=True as of now, some bug in Erik's output
    # makes it possible for an object to appear to lose all references,
    # but still be kept track of and referenced again further on.
    def __init__(self, qry_fs, data_collectors=[], ref_dealloc=False):
        self._g = nx.DiGraph()
        self.qry_fs = qry_fs
        self.data_collectors = [(open(fn, "w+"), func, to_str) \
                                for fn, func, to_str in data_collectors]
        #self.ref_dealloc = ref_dealloc
        self.ref_dealloc = False
        self.results = {}

    def add_obj(self, obj_id, obj_type="(unknown)"):
        if self._g.has_node(obj_id): 
            raise Exception("add_obj: "
                            "Object {0} already exists" \
                            .format(obj_id))
        self._g.add_node(obj_id, 
                         type=obj_type,
                         queries=[qf(self, obj_id) \
                                  for qf in self.qry_fs])

    def set_obj_type(self, obj_id, obj_type):
        if not self._g.has_node(obj_id):
            raise Exception("set_obj_type: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        self._g.node[obj_id]["type"] = obj_type

    def get_obj_type(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("get_obj_type: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return self._g.node[obj_id]["type"]
    
    def add_stack_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("add_stack_ref: "
                            "Referrer object {0} doesn't exist" \
                            .format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("add_stack_ref: "
                            "Referee object {0} doesn't exist" \
                            .format(referee_id))
        #if there aren't any edges yet
        if not self._g.has_edge(referrer_id, referee_id):
            self._g.add_edge(referrer_id, referee_id, stack=0, heap=0)
        self._g.adj[referrer_id][referee_id]["stack"] += 1

    def add_heap_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("add_heap_ref: "
                            "Referrer object {0} doesn't exist" \
                            .format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("add_heap_ref: "
                            "Referee object {0} doesn't exist" \
                            .format(referee_id))
        #if there aren't any edges yet
        if not self._g.has_edge(referrer_id, referee_id):        
            self._g.add_edge(referrer_id, referee_id, stack=0, heap=0)
        self._g.adj[referrer_id][referee_id]["heap"] += 1

    def remove_obj(self, obj_id, force=False):
        if not self._g.has_node(obj_id):
            raise Exception("remove_obj: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        if not force:
            if self.in_total_refs(obj_id) > 0:
                raise Exception("remove_obj: "
                                "Object {0} has incoming references" \
                                .format(obj_id))
            if self.out_total_refs(obj_id) > 0:
                raise Exception("remove_obj: "
                                "Object {0} has outgoing references" \
                                .format(obj_id))
        #Save queries and remove object
        self.results[obj_id] = \
            {"type" : self._g.node[obj_id]["type"], 
             "queries" : self._g.node[obj_id]["queries"]}
        self._g.remove_node(obj_id)

    def remove_stack_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("remove_stack_ref: "
                            "Referrer object {0} doesn't exist" \
                            .format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("remove_stack_ref: "
                            "Referee object {0} doesn't exist" \
                            .format(referee_id))
        if not self._g.has_edge(referrer_id, referee_id):
            raise Exception("remove_stack_ref: "
                            "Referrer {0} and referee {1} "
                            "have no connection" \
                            .format(referrer_id, referee_id))
        if self._g.adj[referrer_id][referee_id]["stack"] == 0:
            raise Exception("remove_stack_ref: "
                            "No references between "
                            "referrer {0} and referee {1}" \
                            .format(referrer_id, referee_id))
        self._g.adj[referrer_id][referee_id]["stack"] -= 1
        # This is run if we remove objects when reference count
        # reaches 0, not waiting for deallocation event
        if self.ref_dealloc and self.in_total_refs(referee_id) == 0:
            self.remove_obj(referee_id)

    def remove_heap_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("remove_heap_ref: "
                            "Referrer object {0} doesn't exist" \
                            .format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("remove_heap_ref: "
                            "Referee object {0} doesn't exist" \
                            .format(referee_id))
        if not self._g.has_edge(referrer_id, referee_id):
            raise Exception("remove_heap_ref: "
                            "Referrer {0} and referee {1} "
                            "have no connection" \
                            .format(referrer_id, referee_id))
        if self._g.adj[referrer_id][referee_id]["heap"] == 0:
            raise Exception("remove_heap_ref: "
                            "No references between "
                            "referrer {0} and referee {1}" \
                            .format(referrer_id, referee_id))
        self._g.adj[referrer_id][referee_id]["heap"] -= 1
        # This is run if we remove objects when reference count
        # reaches 0, not waiting for deallocation event
        if self.ref_dealloc and self.in_total_refs(referee_id) == 0:
            self.remove_obj(referee_id)

    def has_obj(self, obj_id):
        return self._g.has_node(obj_id)

    def has_stack_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("has_stack_ref: "
                            "Referrer object {0} doesn't exist" \
                            .format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("has_stack_ref: "
                            "Referee object {0} doesn't exist" \
                            .format(referee_id))
        return self._g.has_edge(referrer_id, referee_id) and \
               self._g.adj[referrer_id][referee_id]["stack"] > 0

    def has_heap_ref(self, referrer_id, referee_id):
        if not self._g.has_node(referrer_id):
            raise Exception("has_heap_ref: "
                            "Referrer object {0} doesn't exist" \
                            .format(referrer_id))
        if not self._g.has_node(referee_id):
            raise Exception("has_heap_ref: " 
                            "Referee object {0} doesn't exist" \
                            .format(referee_id))
        return self._g.has_edge(referrer_id, referee_id) and \
               self._g.adj[referrer_id][referee_id]["heap"] > 0

    #Returns node array by value, not by reference
    def get_obj_ids(self):
        return self._g.nodes()
    
    #Returns queries by reference, to be able to apply them
    def get_obj_queries(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("get_obj_queries: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return self._g.node[obj_id]["queries"]

    def reset_obj_queries(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("reset_obj_queries: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        self._g.node[obj_id]["queries"] = [qf(self, obj_id) \
                                           for qf in self.qry_fs]

    def collect_data(self, progress):
        for save_file, func, to_str in self.data_collectors:
            save_file.write("{}, {}\n".format(progress,
                                              to_str(func(self))))

    def get_results(self):
        for save_file, _, _ in self.data_collectors:
            save_file.close()
        return self.results.copy()

    # Own methods, not part of the interface. Used in queries.

    def in_stack_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("in_stack_refs: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"], 
                      self._g.in_edges(obj_id, data=True), 0)

    def in_heap_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("in_heap_refs: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return reduce(lambda x,y: x + y[2]["heap"], 
                      self._g.in_edges(obj_id, data=True), 0)

    def in_total_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("in_total_refs: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"] + y[2]["heap"], 
                      self._g.in_edges(obj_id, data=True), 0)

    def out_stack_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("out_stack_refs: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"], 
                      self._g.out_edges(obj_id, data=True), 0)

    def out_heap_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("out_heap_refs: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return reduce(lambda x,y: x + y[2]["heap"], 
                      self._g.out_edges(obj_id, data=True), 0)

    def out_total_refs(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("out_total_refs: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return reduce(lambda x,y: x + y[2]["stack"] + y[2]["heap"], 
                      self._g.out_edges(obj_id, data=True), 0)

    def is_instance_of(self, obj_id, obj_type):
        if not self._g.has_node(obj_id):
            raise Exception("is_instance_of: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        return self._g.node[obj_id]["type"] == obj_type
    
    def is_builtin(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("is_builtin: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
        t = self._g.node[obj_id]["type"]
        return (t == "(unknown)" or
                t.startswith("java/") or
                t.startswith("sun/") or
                t.startswith("["))
