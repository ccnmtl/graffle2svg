
from unittest import makeSuite, TestCase, TestSuite
from rtf import extractRTFString

class TestValid(TestCase):
    """Tests with valid RTF"""
    def testSimple(self):
        assert extractRTFString(r"{\rtf1\ansi testing}")["text"] == "testing"
       
    def testfontweight(self):
        extractRTFString(r"{\rtf\ansi\fs10\b testing}")

def get_tests():
    import testCascadingStyles
    TS = TestSuite()
    TS.addTest(makeSuite(TestValid))
    return TS
