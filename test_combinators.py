import unittest
from combinators import *


#CHECK THAT ALL TESTS COVER THE FROZEN CASES


def applier(qry, evts):
    results = []
    for evt in evts:
        qry.apply(evt)
        results.append(qry.isAccepting())
        if qry.isFrozen():
            results.append("FROZEN")
            break
    return results


def applier_printer(q, evts):
    print "["
    for evt in evts:
        q.apply(evt)
        print q.isAccepting()
        if q.isFrozen():
            print "..."
            print q.isAccepting()
            break
    print "]"
    

class TestCombinators(unittest.TestCase):

    def test_Observe(self):
        evts1 = [0, 1, 2, 3, 1]
        evts2 = [2, 1, 0, 21, 4]
        q1 = Observe(lambda n: n <= 1)
        q2 = Observe(lambda n: n > 2)
        self.assertEquals(applier(q1.clone(), evts1), 
                          [True, True, False, False, True])
        self.assertEquals(applier(q1.clone(), evts2), 
                          [False, True, True, False, False])
        self.assertEquals(applier(q2.clone(), evts1), 
                          [False, False, False, True, False])
        self.assertEquals(applier(q2.clone(), evts2), 
                          [False, False, False, True, True])

    def test_Not(self):
        evts1 = [0, 1, 2, 3, 1]
        evts2 = [2, 1, 0, 21, 4]
        q1 = Not(Observe(lambda n: n <= 1))
        q2 = Not(Observe(lambda n: n > 2))
        self.assertEquals(applier(q1.clone(), evts1), 
                          [False, False, True, True, False])
        self.assertEquals(applier(q1.clone(), evts2), 
                          [True, False, False, True, True])
        self.assertEquals(applier(q2.clone(), evts1), 
                          [True, True, True, False, True])
        self.assertEquals(applier(q2.clone(), evts2), 
                          [True, True, True, False, False])
        

    def test_Ever(self):
        evts1 = [0, 1, 2, 3, 1]
        evts2 = [2, 1, 0, 21, 4]
        evts3 = [2, 2, 2, 2, 2]
        q1 = Ever(Observe(lambda n: n <= 1))
        q2 = Not(Ever(Observe(lambda n: n > 2)))
        self.assertEquals(applier(q1.clone(), evts1), 
                          [True, "FROZEN"])
        self.assertEquals(applier(q1.clone(), evts2), 
                          [False, True, "FROZEN"])
        self.assertEquals(applier(q1.clone(), evts3), 
                          [False, False, False, False, False])
        self.assertEquals(applier(q2.clone(), evts1), 
                          [True, True, True, False, "FROZEN"])
        self.assertEquals(applier(q2.clone(), evts2), 
                          [True, True, True, False, "FROZEN"])
        self.assertEquals(applier(q2.clone(), evts3), 
                          [True, True, True, True, True])
        

    def test_Always(self):
        evts1 = [0, 1, 2, 3, 1]
        evts2 = [3, 7, 5, 21, 4]
        evts3 = [1, 1, 1, 1, 1]
        q1 = Always(Observe(lambda n: n <= 1))
        q2 = Not(Always(Observe(lambda n: n > 2)))
        self.assertEquals(applier(q1.clone(), evts1), 
                          [True, True, False, "FROZEN"])
        self.assertEquals(applier(q1.clone(), evts2), 
                          [False, "FROZEN"])
        self.assertEquals(applier(q1.clone(), evts3), 
                          [True, True, True, True, True])
        self.assertEquals(applier(q2.clone(), evts1), 
                          [True, "FROZEN"])
        self.assertEquals(applier(q2.clone(), evts2), 
                          [False, False, False, False, False])
        self.assertEquals(applier(q2.clone(), evts3), 
                          [True, "FROZEN"])
        

    def test_Any(self):
        evts1 = [0, 1, 2, 3, 4]
        evts2 = [0, 3, 4, 3, 0]
        evts3 = [1, 2, 3, 4, 5]
        sub_q1 = Observe(lambda n: n == 1)
        sub_q2 = Observe(lambda n: n == 2)
        sub_q3 = Ever(Not(Observe(lambda n: n <= 3)))
        sub_q4 = Not(Ever(Observe(lambda n: n > 2)))
        sub_q5 = Not(Ever(Observe(lambda n: n > 3)))
        q1 = Any([sub_q1.clone(), sub_q2.clone()])
        q2 = Any([sub_q1.clone(), sub_q3.clone()])
        q3 = Any([sub_q4.clone(), sub_q5.clone()])
        self.assertEquals(applier(q1.clone(), evts1),
                          [False, True, True, False, False])
        self.assertEquals(applier(q1.clone(), evts2),
                          [False, False, False, False, False])
        #sub_q3 getting frozen in accepting state at n = 4
        #should mean the Any query also gets frozen: 
        self.assertEquals(applier(q2.clone(), evts1),
                          [False, True, False, False, True, "FROZEN"])
        self.assertEquals(applier(q2.clone(), evts2),
                          [False, False, True, "FROZEN"])
        #sub_q4 and sub_q5 getting frozen in unaccepting states at 
        #n = 2 and n = 3 respectively should mean that the Any 
        #query also gets frozen:
        self.assertEquals(applier(q3.clone(), evts3),
                          [True, True, True, False, "FROZEN"])
        

    def test_All(self):
        evts1 = [0, 1, 2, 3, 4]
        evts2 = [0, 3, 4, 3, 0]
        sub_q1 = Observe(lambda n: n < 3)
        sub_q2 = Not(Observe(lambda n: n == 1))
        sub_q3 = Ever(Observe(lambda n: n > 1))
        sub_q4 = Ever(Not(Observe(lambda n: n == 2)))
        sub_q5 = Always(Observe(lambda n: n == 0))
        q1 = All([sub_q1.clone(), sub_q2.clone()])
        q2 = All([sub_q3.clone(), sub_q4.clone()])
        q3 = All([sub_q1.clone(), sub_q5.clone()])
        self.assertEquals(applier(q1.clone(), evts1),
                          [True, False, True, False, False])
        self.assertEquals(applier(q1.clone(), evts2),
                          [True, False, False, False, True])
        self.assertEquals(applier(q2.clone(), evts1),
                          [False, False, True, "FROZEN"])
        self.assertEquals(applier(q3.clone(), evts2),
                          [True, False, "FROZEN"])


if __name__ == "__main__":
    unittest.main()
