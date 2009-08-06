
from unittest import makeSuite, TestCase, TestSuite
from styles import CascadingStyles

class TestDefaults(TestCase):
    def setUp(self):
        self.cs = CascadingStyles({"font":"arial","font-size":"12pt"})
        
    def testNone(self):
        assert str(self.cs) == ""
        
    def testRemoveScope(self):
        self.cs.appendScope()
        self.cs["font"] = "newfont"
        self.cs.popScope()
        assert str(self.cs) == ""
        
        
    def testIgnoreDefault(self):
        self.cs.appendScope()
        self.cs["font"] = "newfont"
        self.cs.appendScope()
        self.cs["font"] = "arial"
        assert str(self.cs) == ""
        
        
class TestScope(TestCase):
    def setUp(self):
        self.cs = CascadingStyles({"font":"arial","font-size":"12pt"})
        
    def testRemoveScope(self):
        self.cs.appendScope()
        self.cs["font"] = "newfont"
        self.cs["font"] == "newfont"

def get_tests():
    import testCascadingStyles
    TS = TestSuite()
    TS.addTest(makeSuite(TestDefaults))
    TS.addTest(makeSuite(TestScope))
    return TS
