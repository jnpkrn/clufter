# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2ccsflat filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from subprocess import PIPE
import logging

from clufter.filter import Filter, FilterError
from clufter.utils_prog import OneoffWrappedStdinPopen, dirname_x, which

log = logging.getLogger(__name__)
# XXX
CCS_FLATTEN = which('ccs_flatten', dirname_x(__file__, 2)) or ''


@Filter.deco('ccs', 'ccs-flat')
def ccs2ccsflat(flt_ctxt, in_obj):
    self = flt_ctxt.ctxt_wrapped
    # XXX currently ccs_flatten does not handle stdin (tempfile.mkstemp?)
    # XXX conversion is not idempotent, should prevent using ccs-flat as input
    #     (specifically, explicit ordering will get borken in subsequent round)
    in_file = in_obj('file')
    command = [CCS_FLATTEN, in_file]
    log.info("running `{0}'".format(' '.join(command)))
    try:
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
