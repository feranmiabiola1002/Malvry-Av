import unittest
import os
import tempfile
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from scanner import Scanner
from database import init_default_signatures

class TestScanner(unittest.TestCase):
    def setUp(self):
        init_default_signatures()
        self.scanner = Scanner()
        self.test_dir = tempfile.mkdtemp()
    def tearDown(self):
        self.scanner.close()
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    def test_clean_file(self):
        test_file = os.path.join(self.test_dir, 'clean.txt')
        with open(test_file, 'w') as f:
            f.write('clean')
        result = self.scanner.scan_file(test_file)
        self.assertIsNone(result)
    def test_directory_scan(self):
        for i in range(5):
            with open(os.path.join(self.test_dir, f'file_{i}.txt'), 'w') as f:
                f.write(f'File {i}')
        results = self.scanner.scan_directory(self.test_dir)
        self.assertIsInstance(results, list)

if __name__ == '__main__':
    unittest.main()
