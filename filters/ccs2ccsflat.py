# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2ccsflat filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from logging import getLogger
from os.path import split as path_split
from subprocess import PIPE
from sys import stdin

from ..filter import Filter, FilterError
from ..utils_prog import OneoffWrappedStdinPopen, dirname_x, which

try:
    from ..defaults import CCS_FLATTEN
except ImportError:
    CCS_FLATTEN = 'ccs_flatten'

log = getLogger(__name__)


@Filter.deco('ccs', 'ccs-flat')
def ccs2ccsflat(flt_ctxt, in_obj):
    self = flt_ctxt.ctxt_wrapped

    ccsf_dirname, ccsf_basename = path_split(CCS_FLATTEN)
    # order of priority when searching for the binary (descending order):
    # - same as the root of the package (debugging purposes)
    # - directories-part as per specification in setup.cfg
    # - PATH env variable (if defined)
    ccs_flatten = which(ccsf_basename, dirname_x(__file__, 2), ccsf_dirname, '')
    if not ccs_flatten:
        raise FilterError(self, "ccs_flatten binary seems unavailable")

    # XXX currently ccs_flatten does not handle stdin (tempfile.mkstemp?)
    # XXX conversion is not idempotent, should prevent using ccs-flat as input
    #     (specifically, explicit ordering will get borken in subsequent round)
    in_file = in_obj('file')
    if not isinstance(in_file, basestring):
        # convert '-'/'@0' already converted to fileobj back to '-'
        if in_file is not stdin:
            raise RuntimeError("Only stdin ('-') supported")
        in_file = '-'
    command = [ccs_flatten, in_file]
    log.info("running `{0}'".format(' '.join(command)))
    try:
        proc = OneoffWrappedStdinPopen(command, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise FilterError(self, "error running ccs_flatten binary")
    out, err = proc.communicate()
    if proc.returncode != 0 or out == '' and err != '':
        raise FilterError(self, "ccs_flatten {0}\n\t{1}",
                          ("exit code: {0}" if proc.returncode > 0 else
                           "killing signal: {0}").format(abs(proc.returncode)),
                          err)
    return ('bytestring', out)
