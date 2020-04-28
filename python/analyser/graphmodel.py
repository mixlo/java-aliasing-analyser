#!/usr/bin/env python
import model
import networkx as nx

#TODO: Documentation

# Implementation of model using a DiGraph from the networkx library
class GraphModel(model.Model):
    def __init__(self, qry_fs):
        self._g = nx.DiGraph()
        self.qry_fs = qry_fs
        self.results = {}

    def add_obj(self, obj_id, obj_type="(unknown)"):
        if self._g.has_node(obj_id): 
            raise Exception("add_obj: "
                            "Object {0} already exists" \
                            .format(obj_id))
        self._g.add_node(obj_id, 
                         type=obj_type,
                         queries=[qf(obj_id) for qf in self.qry_fs])

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

    def remove_obj(self, obj_id):
        if not self._g.has_node(obj_id):
            raise Exception("remove_obj: "
                            "Object {0} doesn't exist" \
                            .format(obj_id))
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

    def get_results(self):
        return self.results.copy()
