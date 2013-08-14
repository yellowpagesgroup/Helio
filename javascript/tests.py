import unittest
import subprocess
import urlparse, urllib
import os


def path2url(path):
    return urlparse.urljoin('file:', urllib.pathname2url(path))


class JavascriptTestRunner(unittest.TestCase):
    def test_run_qunit(self):
        return
        try:
            output = subprocess.check_output(['phantomjs', 'javascript/runner.js',
                                              path2url(os.getcwd() + '/javascript/qunit.html')])
            self.assertIn(' 0 failed', output)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.output)

