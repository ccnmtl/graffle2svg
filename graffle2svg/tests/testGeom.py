
from unittest import makeSuite, TestCase, TestSuite
import geom 

class TestCentre(TestCase):
        
    def testSimple(self):
        pts = [[-1,-1],[1,1]]
        centre = geom.findcentre(pts)
        assert centre[0] == 0
        assert centre[1] == 0
    
    def testSimpleFloat(self):
        pts = [[-1.,-1.],[1.,1.]]
        centre = geom.findcentre(pts)
        assert centre[0] == 0
        assert centre[1] == 0
        
    def testNonZeroCentre(self):
        pts = [[-4,-1],[0,1]]
        centre = geom.findcentre(pts)
        assert centre[0] == -2
        assert centre[1] == 0

def get_tests():
    TS = TestSuite()
    TS.addTest(makeSuite(TestCentre))
    return TS
