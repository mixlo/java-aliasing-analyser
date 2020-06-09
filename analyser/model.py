#!/usr/bin/env python


class Model(object):
    """
    An interface describing the base properties of the model.
    The model describes the state of the execution at a certain time.
    During initiation the model will be provided a list of lambda 
    expressions. These lambda expressions act as query factories.
    An example of such a lambda expression:

    >>> lambda o: Observe("lambda in_total_refs: in_total_refs <= 1", 
                          lambda: gm.in_total_refs(o))
    
    When an object is added to the model, the model uses the query 
    factories to generate combinators for the object by running each 
    of the lambda expressions, passing into them the ID of the object. 

    The Observe query of a combinator expects a boolean function (the 
    query) testing some condition on the object, along with zero or 
    more "argument getters" used by the boolean function. These 
    getters are lambda expressions that when run fetch information 
    from the model about the object, necessary to test the condition, 
    and pass it into the boolean function as arguments (hence the 
    name).

    The combinators need to be able to run the getters without having 
    to know which getter needs which kind of arguments. The getters 
    are therefore formed as zero argument lambda expressions. If the 
    getters need the object ID to fetch the correct information, they 
    need a way to access it without the use of parameters. This is 
    solved by using the query factories as closures, passing the 
    object ID into the internal definition of the lambda expressions 
    (see example).

    However, as (currently) only the ID of the added object is passed 
    in to the query factories, this is the only resource the getters 
    have to use to fetch information from the model. It is hence for 
    now not possible to, for example, fetch information about an edge 
    between this object and another specific object, since that would 
    require knowledge of the ID of both objects.

    The boolean function (the query) passed in to the combinator is 
    encapsulated in a string, this is to get a string representation 
    of the combinator for its 'toString' method. The string is 
    evaluated into a lambda expression using the Python built-in 
    'eval' function.

    During initiation, the model should also define a results 
    dictionary. This will be used to collect the results at the end of 
    the execution of the program. The keys of the dictionary should be 
    object IDs, and the values should be dicts with two elements. One 
    with "type" as key and the object type (string) as value, and the 
    other with "queries" as key and the objects' associated queries as 
    value.
    """

    def __init__(self, qry_fs, data_collectors):
        """
        TYPE: lambda list -> void
        Initialise the model with the provided list of query 
        factories, and data collectors.
        """
        raise NotImplementedError()

    def add_obj(self, obj_id, obj_type):
        """
        TYPE: string * string -> void
        Add an object to the model, then generate new queries and 
        associate them with the object.
        """
        raise NotImplementedError()

    def set_obj_type(self, obj_id, obj_type):
        """
        TYPE: string * string -> void
        Set the type property of an object.
        """
        raise NotImplementedError()

    def get_obj_type(self, obj_id):
        """
        TYPE: string -> string
        Return the type property of an object.
        """
        raise NotImplementedError();

    def add_stack_ref(self, referrer_id, referee_id):
        """
        TYPE: string * string -> void
        Add a stack reference between two objects.
        """
        raise NotImplementedError()

    def add_heap_ref(self, referrer_id, referee_id):
        """
        TYPE: string * string -> void
        Add a heap reference between two objects.
        """
        raise NotImplementedError()

    def remove_obj(self, obj_id):
        """
        TYPE: string -> void
        Remove an object from the model after saving its associated 
        queries for the final measurements.
        """
        raise NotImplementedError()

    def remove_stack_ref(self, referrer_id, referee_id):
        """
        TYPE: string * string -> void
        Remove a stack reference between two objects.
        """
        raise NotImplementedError()

    def remove_heap_ref(self, referrer_id, referee_id):
        """
        TYPE: string * string -> void
        Remove a heap reference between two objects.
        """
        raise NotImplementedError()

    def has_obj(self, obj_id):
        """
        TYPE: string -> boolean
        Check whether an object exists in the model.
        """
        raise NotImplementedError()

    def has_stack_ref(self, referrer_id, referee_id):
        """
        TYPE: string * string -> boolean
        Return True if for two objects, there exists at least one 
        stack reference between them. Otherwise return False.
        """
        raise NotImplementedError()

    def has_heap_ref(self, referrer_id, referee_id):
        """
        TYPE: string * string -> boolean
        Return True if for two objects, there exists at least one 
        heap reference between them. Otherwise return False.
        """
        raise NotImplementedError()

    def get_obj_ids(self):
        """
        TYPE: void -> string list
        Return a list of IDs corresponding to the currently existing 
        objects in the model.
        """
        raise NotImplementedError()

    def get_obj_queries(self, obj_id):
        """
        TYPE: string -> combinator list
        Return a reference to the list of queries for a given object, 
        to be able to apply the queries during execution.
        """
        raise NotImplementedError()

    def reset_obj_queries(self, obj_id):
        """
        TYPE: string -> void
        Reset all queries for a given object.
        """
        raise NotImplementedError()

    def collect_data(self, progress):
        """
        TYPE: float -> void
        Run all data collection functions and save the results to 
        their respectively assigned files. The provided argument 
        signifies the progress percentage of the execution.
        """
        raise NotImplementedError()

    def get_results(self):
        """
        TYPE: void -> dict
        Return a copy of the results dictionary of the model.
        """
        raise NotImplementedError()
