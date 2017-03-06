# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from __future__ import print_function

"""Testing `ccsflat2cibprelude' filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following makes available also: TeardownFilterTestCase, rewrite_root
from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(dirname(__file__)), '_com')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from .utils_2to3 import bytes_enc

flt = 'ccs2needlexml'

class FiltersCcs2NeedleXmlTestCase(TeardownFilterTestCase):
    def testLoggerSubsys(self):
        flt_obj = rewrite_root(self.flt_mgr.filters[flt], 'cluster/logging/logging_daemon')
        in_fmt = flt_obj.in_format
        io_strings = (
            ('''\
<logging_daemon name="corosync" subsys="CONFDB" to_syslog="yes"/>
''', '''\
<logger_subsys subsys="CMAP" to_syslog="yes"/>
'''),
            ('''\
<logging_daemon name="corosync" subsys="QDISKD"
                to_logfile="yes" logfile="/var/log/corosync-qdiskd.log"
                to_syslog="yes" syslog_priority="debug"/>
''', '''\
<logger_subsys subsys="QDEVICE" to_syslog="yes" syslog_priority="debug"/>
'''),
        )
        for (in_str, out_str) in io_strings:
            in_obj = in_fmt('bytestring', in_str)
            out_obj = flt_obj(in_obj)
            #print(out_obj.BYTESTRING())
            self.assertEquals(out_obj.BYTESTRING(), bytes_enc(out_str))


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(dirname(__file__)), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
