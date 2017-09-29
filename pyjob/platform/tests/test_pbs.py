# MIT License
#
# Copyright (c) 2017 Felix Simkovic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.  #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Testing facility for pyjob.platform.pbs"""

__author__ = "Felix Simkovic"
__date__ = "10 May 2017"

import inspect
import os
import time
import unittest

from pyjob.misc import make_script
from pyjob.platform import prep_array_script
from pyjob.platform.pbs import PortableBatchSystem


def skipUnless(condition):
    if condition:
        return lambda x: x
    else:
        return lambda x: None


@skipUnless("PBS_ROOT" in os.environ)
class TestPortableBatchSystem(unittest.TestCase):

    # ================================================================================
    # SINGLE JOB SUBMISSIONS

    def test_alt_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = PortableBatchSystem.sub(
            jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        PortableBatchSystem.alt(jobid, priority=-1)
        data = PortableBatchSystem.stat(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, data['Job Id'])
        self.assertEqual(-1, int(data['Priority']))
        PortableBatchSystem.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_kill_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = PortableBatchSystem.sub(
            jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(PortableBatchSystem.stat(jobid))
        PortableBatchSystem.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_hold_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = PortableBatchSystem.sub(jobs, hold=False, name=inspect.stack()[
                                        0][3], shell="/bin/sh", log=os.devnull)
        time.sleep(5)
        PortableBatchSystem.hold(jobid)
        PortableBatchSystem.kill(jobid)
        map(os.unlink, jobs)

    def test_rls_1(self):
        jobs = [make_script(["touch", "pyjob_rls__test_1"])]
        jobid = PortableBatchSystem.sub(jobs, hold=True, name=inspect.stack()[
                                        0][3], shell="/bin/sh", log=os.devnull)
        time.sleep(5)
        PortableBatchSystem.rls(jobid)
        while PortableBatchSystem.stat(jobid):
            time.sleep(1)
        self.assertTrue(os.path.isfile('pyjob_rls__test_1'))
        os.unlink('pyjob_rls__test_1')
        for f in jobs:
            os.unlink(f)

    def test_stat_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = PortableBatchSystem.sub(
            jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        data = PortableBatchSystem.stat(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, data['Job Id'])
        self.assertTrue('pbs_o_shell' in data)
        self.assertTrue('pbs_o_workdir' in data)
        self.assertTrue('pbs_o_host' in data)
        PortableBatchSystem.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_sub_1(self):
        jobs = [make_script(["sleep 1"])]
        jobid = PortableBatchSystem.sub(
            jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(PortableBatchSystem.stat(jobid))
        PortableBatchSystem.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_sub_2(self):
        assert "PYJOB_ENV" not in os.environ
        os.environ["PYJOB_ENV"] = "pyjob_random"
        job = [make_script(["echo $PYJOB_ENV"])]
        log = job[0].replace(".sh", ".log")
        jobid = PortableBatchSystem.sub(
            job, log=log, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        while PortableBatchSystem.stat(jobid):
            time.sleep(1)
        self.assertTrue(os.path.isfile(log))
        self.assertTrue(open(log).read().strip(), "pyjob_random")
        for f in job + [log]:
            os.unlink(f)

    # ================================================================================
    # ARRAY JOB SUBMISSIONS

    def test_kill_2(self):
        jobs = [make_script(["sleep 100"]) for _ in range(5)]
        array_script, array_jobs = prep_array_script(
            jobs, os.getcwd(), PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[1, 5], hold=True,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(PortableBatchSystem.stat(jobid))
        PortableBatchSystem.kill(jobid)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_stat_2(self):
        jobs = [make_script(["sleep 100"]) for _ in range(5)]
        array_script, array_jobs = prep_array_script(
            jobs, os.getcwd(), PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[
                                        1, 5], hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        data = PortableBatchSystem.stat(jobid)
        PortableBatchSystem.kill(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, data['Job Id'])
        self.assertTrue('pbs_o_shell' in data)
        self.assertTrue('pbs_o_workdir' in data)
        self.assertTrue('pbs_o_host' in data)
        self.assertTrue('job-array tasks' in data)
        self.assertEqual("1-5:1", data['job-array tasks'].strip())
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_3(self):
        jobs = [make_script(["sleep 1"]) for _ in range(5)]
        array_script, array_jobs = prep_array_script(
            jobs, os.getcwd(), PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[1, 5], hold=True,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(PortableBatchSystem.stat(jobid))
        PortableBatchSystem.kill(jobid)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_4(self):
        directory = os.getcwd()
        jobs = [make_script([["sleep 5"], ['echo "file {0}"'.format(i)]], directory=directory)
                for i in range(5)]
        array_script, array_jobs = prep_array_script(
            jobs, directory, PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[1, 5], log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while PortableBatchSystem.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual("file {0}".format(i), open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_5(self):
        directory = os.getcwd()
        jobs = [make_script(['echo "file {0}"'.format(i)], directory=directory)
                for i in range(100)]
        array_script, array_jobs = prep_array_script(
            jobs, directory, PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[1, 100], log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while PortableBatchSystem.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual("file {0}".format(i), open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_6(self):
        jobs = [make_script(["echo $PBS_ROOT"], directory=os.getcwd())
                for _ in range(2)]
        array_script, array_jobs = prep_array_script(
            jobs, os.getcwd(), PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[1, 2], log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while PortableBatchSystem.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual(os.environ["PBS_ROOT"], open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_7(self):
        assert "PYJOB_ENV1" not in os.environ
        os.environ["PYJOB_ENV1"] = "pyjob_random1"
        jobs = [make_script(["echo $PYJOB_ENV1"], directory=os.getcwd())
                for _ in range(2)]
        array_script, array_jobs = prep_array_script(
            jobs, os.getcwd(), PortableBatchSystem.ARRAY_TASK_ID)
        jobid = PortableBatchSystem.sub(array_script, array=[1, 2], directory=os.getcwd(), log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while PortableBatchSystem.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual(os.environ["PYJOB_ENV1"], open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
