# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2flatccs filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import pardir
from subprocess import PIPE
import logging

from clufter.filter import Filter, FilterError
from clufter.utils import which, OneoffWrappedStdinPopen

log = logging.getLogger(__name__)
# XXX
CCS_FLATTEN = which('ccs_flatten', pardir) or ''


@Filter.deco('ccs', 'flatccs')
def ccs2flatccs(flt_ctxt, in_obj, verify=False):
    self = flt_ctxt.ctxt_wrapped
    # XXX currently ccs_flatten does not handle stdin (tempfile.mkstemp?)
    if verify:
        in_obj.verify()
    in_file = in_obj('file')
    try:
        command = [CCS_FLATTEN, in_file]
        log.info("running `{0}'".format(' '.join(command)))
        proc = OneoffWrappedStdinPopen(command, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise FilterError(self, "ccs_flatten binary seems unavailable")
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise FilterError(self, "ccs_flatten exit code: {0}\n\t{1}",
                          proc.returncode, err)
    elif out == '':
        # "No resource trees defined; nothing to do"
        try:
            with file(in_file, 'r') as f:
                out = f.read()
        except IOError, e:
            raise FilterError(self, e.strerror + ": {0}", e.filename)
    return ('bytestring', out)
