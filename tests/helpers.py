import os

from sanction.test import with_patched_client


def mock_response(name, code=200):
    """This decorator uses captured responses to mock server responses."""
    testdir = os.path.dirname(__file__)
    filename = os.path.join(testdir, 'mocks', "response_%s.json" % name)
    with open(filename) as f:
        data = "".join(f.readlines())
    return with_patched_client(data, code)


def optional(run, deco):
    """This is a decorator which applies another decorator only if the
    condition is true."""
    if run:
        return deco
    else:
        def do_nothing(func):
            return func
        return do_nothing
