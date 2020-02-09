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
__version__ = '1.0'

import logging
import re
import uuid

from pyjob.cexec import cexec
from pyjob.exception import PyJobExecutableNotFoundError, PyJobError
from pyjob.script import Script
from pyjob.task import ClusterTask

logger = logging.getLogger(__name__)

RE_LINE_SPLIT = re.compile(r":\s+")
RE_PID_MATCH = re.compile(r"Your job .* has been submitted")


class SunGridEngineTask(ClusterTask):
    """SunGridEngine executable :obj:`~pyjob.task.Task`"""

    JOB_ARRAY_INDEX = '$SGE_TASK_ID'
    SCRIPT_DIRECTIVE = '#$'

    @property
    def info(self):
        """:obj:`~pyjob.sge.SunGridEngineTask` information"""
        if self.pid is None:
            return {}
        try:
            stdout = cexec(["qstat", "-j", str(self.pid)], permit_nonzero=True)
        except PyJobExecutableNotFoundError:
            return {}
        data = {}
        for line in stdout.splitlines():
            line = line.strip()
            if 'jobs do not exist' in line:
                return data
            if not line or "=" * 30 in line:
                continue
            else:
                kv = RE_LINE_SPLIT.split(line, 1)
                if len(kv) == 2:
                    data[kv[0]] = kv[1]
        return data

    @staticmethod
    def sge_avail_config(param):
        """Get the set of available configurations for a given SGE parameter

        Parameters
        ----------
        param : str
            The parameter to be tested

        Returns
        -------
        set
            A set with the available configurations for the parameter of interest

        Raises
        ------
        :exc:`ValueError`
           Invalid parameter. Supported parameters are 'environment' or 'queue'

        """

        if param == 'environment':
            cmd = ["qconf", 'spl']
        elif param == 'queue':
            cmd = ["qconf", 'sql']
        else:
            raise ValueError('Invalid parameter {}. Available parameters are "environment" or "queue".'.format(param))

        stdout = cexec(cmd, permit_nonzero=True)
        config = []
        for line in stdout.splitlines():
            line = line.split()
            if len(line) > 1:
                return config
            else:
                config.append(line[0].encode('utf-8'))
        return set(config)

    def _check_requirements(self):
        """Check if the requirements for task execution are met"""

        # Check if SGE is available
        try:
            cexec(['qstat'])
        except PyJobExecutableNotFoundError:
            raise PyJobError('Cannot find SGE. Please ensure this is the correct platform to run your task!')

        # Check if the requested environment exists
        if self.environment not in self.sge_config('environment'):
            raise PyJobError('Requested environment {} cannot be found. List of available environments: {}'
                             ''.format(self.environment, self.sge_avail_config('environment')))

        # Check if the requested queue exists
        if self.queue not in self.sge_config('queue'):
            raise PyJobError('Requested queue {} cannot be found. List of available queues: {}'
                             ''.format(self.queue, self.sge_avail_config('queue')))

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.sge.SunGridEngineTask`"""
        if self.pid is None:
            return
        cexec(['qdel', str(self.pid)])
        logger.debug("Terminated task: %d", self.pid)

    def _run(self):
        """Method to initialise :obj:`~pyjob.sge.SunGridEngineTask` execution"""
        self.runscript = self._create_runscript()
        self.runscript.write()
        stdout = cexec(['qsub', self.runscript.path], cwd=self.directory)
        for line in stdout.split('\n'):
            line = line.strip()
            if re.match(RE_PID_MATCH, line):
                if len(self.script) > 1:
                    self.pid = int(line.split()[2].split(".")[0])
                else:
                    self.pid = int(line.split()[2])
        logger.debug('%s [%d] submission script is %s', self.__class__.__name__, self.pid, self.runscript.path)

    def _create_runscript(self):
        """Utility method to create runscript"""
        runscript = Script(directory=self.directory, prefix='sge_', suffix='.script', stem=str(uuid.uuid1().int))
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -V')
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -w e')
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -j yes')
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -N {}'.format(self.name))
        if self.dependency:
            cmd = '-hold_jid {}'.format(','.join(map(str, self.dependency)))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.priority:
            cmd = '-p {}'.format(self.priority)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.queue:
            cmd = '-q {}'.format(self.queue)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.runtime:
            cmd = '-l h_rt={}'.format(self.get_time(self.runtime))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.shell:
            cmd = '-S {}'.format(self.shell)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.nprocesses:
            cmd = '-pe {} {}'.format(self.environment, self.nprocesses)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.directory:
            cmd = '-wd {}'.format(self.directory)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.extra:
            cmd = ' '.join(map(str, self.extra))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if len(self.script) > 1:
            logf = runscript.path.replace('.script', '.log')
            jobsf = runscript.path.replace('.script', '.jobs')
            with open(jobsf, 'w') as f_out:
                f_out.write('\n'.join(self.script))
            cmd = '-t {}-{} -tc {}'.format(1, len(self.script), self.max_array_size)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -o {}'.format(logf))
            runscript.extend(self.get_array_bash_extension(jobsf, 0))
        else:
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -o {}'.format(self.log[0]))
            runscript.append(self.script[0])
        return runscript
