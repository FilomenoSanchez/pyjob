# MIT License
#
# Copyright (c) 2017-18 Felix Simkovic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Felix Simkovic'
from pyjob import version
__version__ = version.__version__

from pyjob.cexec import cexec
from pyjob.pool import Pool


def QueueFactory(platform, *args, **kwargs):
    """Accessibility function for any :obj:`Queue <pyjob.queue.Queue>`
    
    Parameters
    ----------
    platform : str
       The platform to create the queue on

    """
    platform = platform.lower()
    if platform == 'local':
        from pyjob.local import LocalJobServer
        return LocalJobServer(*args, **kwargs)
    elif platform == 'sge':
        from pyjob.sge import SunGridEngine
        return SunGridEngine(*args, **kwargs)
