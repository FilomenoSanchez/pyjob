__author__ = 'Felix Simkovic'

import mock
import os
import pytest

from pyjob.torque import TorqueTask


@pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
@mock.patch('pyjob.torque.TorqueTask._check_requirements')
class TestCreateRunscript(object):
    def test_1(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_2(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -t 1-3%3',
            '#PBS -o {}'.format(logf),
            '#PBS -e {}'.format(logf),
            'script=$(awk "NR==$PBS_ARRAYID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1',
        ]
        assert jobs == paths

    def test_3(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -t 1-3%1',
            '#PBS -o {}'.format(logf),
            '#PBS -e {}'.format(logf),
            'script=$(awk "NR==$PBS_ARRAYID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1',
        ]
        assert jobs == paths

    def test_4(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, name='foobar')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N foobar',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_5(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, processes=5)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 5',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_6(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, queue='barfoo')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -q barfoo',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_7(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, directory='..')
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), '..'))
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + wd,
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_8(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, runtime=120)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -l walltime=02:00:00',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_9(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, shell='/bin/csh')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -S /bin/csh',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_10(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, priority=-1)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -p -1',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_11(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = TorqueTask(paths, extra=['-l mem=100', '-r y'])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -l mem=100 -r y',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]
