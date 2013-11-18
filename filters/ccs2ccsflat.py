# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2ccsflat filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import pardir
from subprocess import Popen, PIPE
import logging

from clufter.filter import Filter, FilterError
from clufter.utils import which

log = logging.getLogger(__name__)
# XXX
CCS_FLATTEN = which('ccs_flatten', pardir) or ''


@Filter.deco('ccs', 'ccsflat')
def ccs2ccsflat(self, in_obj, verify=False):
    # XXX currently ccs_flatten does not handle stdin (tempfile.mkstemp?)
    if verify:
        in_obj.verify()
    in_file = in_obj('file')
    try:
        command = [CCS_FLATTEN, in_file]
        log.info("running `{0}'".format(' '.join(command)))
        proc = Popen(command, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise FilterError(self, "ccs_flatten binary seems unavailable")
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise FilterError(self, "ccs_flatten exit code: {0}\n\t{1}",
                          proc.returncode, err)
    elif out == '':
        # "No resource trees defined; nothing to do"
        with file(in_file, 'r') as f:
            out = f.read()
    return ('bytestring', out)
