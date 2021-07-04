import json
import unittest
from html import escape
from pathlib import Path

import stache

IGNORED = ['delimiters.json', '~inheritance.json', '~partials.json']


def generate_test(test, filename):
    class TestCase(unittest.TestCase):
        def runTest(self):
            nodes = stache.parse(test['template'], '')
            html = stache.render(nodes, test['data'], escape)
            self.assertEqual(html, test['expected'])

        def __str__(self):
            return f'{filename} - {test["name"]}'

        def shortDescription(self):
            return test['desc']

    return TestCase()


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    for path in Path('spec/specs/').iterdir():
        if path.suffix == '.json' and path.name not in IGNORED:
            with open(path) as fh:
                data = json.load(fh)
            suite.addTest(unittest.TestSuite(
                generate_test(test, path.name) for test in data['tests']
            ))
    return suite
