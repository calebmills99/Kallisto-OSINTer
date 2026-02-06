"""
Basic unit test for the PyQt6 interface.
Since GUI testing is complex, this test only checks that the GUI window can be instantiated.
"""

import unittest
import sys
from PyQt6 import QtWidgets
from src.ui.qt_interface import OSINTerGUI

class TestQtInterface(unittest.TestCase):
    def setUp(self):
        self.app = QtWidgets.QApplication(sys.argv)
    
    def test_gui_instantiation(self):
        gui = OSINTerGUI()
        self.assertIsNotNone(gui)
        self.assertEqual(gui.windowTitle(), "Kallisto-OSINTer GUI")

if __name__ == "__main__":
    unittest.main()