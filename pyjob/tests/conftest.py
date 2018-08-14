__author__ = 'Felix Simkovic'

import inspect
import os
import pytest
import random
import string

from pyjob.script import Script

pytest_plugins = ['helpers_namespace']


@pytest.helpers.register
def fibonacci(n):
    cache = [0, 1]
    if n == 1:
        return cache[0]
    for i in range(n - 2):
        tmp = cache[0]
        cache[0] = cache[1]
        cache[1] += tmp
    return cache[1]


@pytest.helpers.register
def get_py_script(i, target):
    script = Script(shebang='#!/usr/bin/env python', prefix='pyjob', stem='test{}'.format(i), suffix='.py')
    script.content.extend(inspect.getsource(fibonacci).splitlines())
    script.content.pop(0)  # Decorator
    script.content.append("n = {}; print('%dth fib is: %d' % (n, {}(n)))".format(target, 'fibonacci'))
    return script


@pytest.helpers.register
def unlink(paths):
    for p in paths:
        if os.path.isfile(p):
            os.unlink(p)


@pytest.helpers.register
def randomstr(n=5):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))