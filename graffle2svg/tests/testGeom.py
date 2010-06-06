
from unittest import makeSuite, TestCase, TestSuite
import geom

class TestGeom(TestCase):
    def assertFigureAlmostEqual(self,first,second,places=7, msg=None):
        if len(first) != len(second):
            raise self.failureException, (msg or 'sizes different')
        for i in range(len(first)):
            if round(abs(second[i][0]-first[i][0]),places) != 0:
                            raise self.failureException, \
                  (msg or '%r != %r within %r places at rank %r' % (first, second, places,i))
            if round(abs(second[i][1]-first[i][1]),places) != 0:
                            raise self.failureException, \
                  (msg or '%r != %r within %r places at rank %r' % (first, second, places,i))


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

class TestRotate(TestGeom):
    def testIdentic(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts)
        self.assertFigureAlmostEqual(rotated,((-1.0, 1.0), (1.0, 1.0)))

    def testOpposite(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts, angle=180.)
        self.assertFigureAlmostEqual(rotated,[[1., 1.], [-1., 1.]])
 
    def test360(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts, 360)
        self.assertFigureAlmostEqual(rotated,((-1.0, 1.0), (1.0, 1.0)))
        
    def test90(self):
        pts=((-1., 1.), (3., 1.),(-1,-2))
        rotated =geom.rotate_points(pts,90)
        self.assertFigureAlmostEqual(rotated,((-0.5,-2.5),(-0.5,1.5),(2.5,-2.5)))

    def testRounding360(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts, 359.999999)
        self.assertFigureAlmostEqual(rotated,((-1.0, 1.0), (1.0, 1.0)))
        
    def testRoundingOpposite(self):
        pts=((-1., 1.), (1., 1.))
        rotated =geom.rotate_points(pts, 180.000001)
        self.assertFigureAlmostEqual(rotated,[[1., 1.], [-1., 1.]])

      
def get_tests():
    TS = TestSuite()
    TS.addTest(makeSuite(TestCentre))
    TS.addTest(makeSuite(TestRotate))
    return TS
