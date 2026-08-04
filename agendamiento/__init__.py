import unittest

def load_tests(loader, tests, pattern):
    from . import tests as test_module
    return loader.loadTestsFromModule(test_module)
