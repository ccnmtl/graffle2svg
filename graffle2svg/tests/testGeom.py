
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

class TestRotate(TestCase):
    def testIdentic(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts)
        assert rotated==((-1.0, 1.0), (1.0, 1.0))

    def testOpposite(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts, angle=180.)
        assert rotated==[[1., 1.], [-1., 1.]]
 
    def test360(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts, 360)
        assert rotated==((-1.0, 1.0), (1.0, 1.0))
        
    def test90(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts,90)
        self.assertAlmostEqual(0,rotated[0][0],4)
        self.assertAlmostEqual(0,rotated[0][1],4)
        self.assertAlmostEqual(0,rotated[1][0],4)
        self.assertAlmostEqual(2,rotated[1][1],4)
        
      
def get_tests():
    TS = TestSuite()
    TS.addTest(makeSuite(TestCentre))
    TS.addTest(makeSuite(TestRotate))
    return TS
