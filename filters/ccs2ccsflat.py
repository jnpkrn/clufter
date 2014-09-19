# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""ccs2ccsflat filter"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

import logging
from os.path import split as path_split
from subprocess import PIPE

from ..filter import Filter, FilterError
from ..utils_prog import OneoffWrappedStdinPopen, dirname_x, which

try:
    from ..defaults import CCS_FLATTEN
except ImportError:
    CCS_FLATTEN = 'ccs_flatten'

log = logging.getLogger(__name__)


@Filter.deco('ccs', 'ccs-flat')
def ccs2ccsflat(flt_ctxt, in_obj):
    self = flt_ctxt.ctxt_wrapped

    ccsf_dirname, ccsf_basename = path_split(CCS_FLATTEN)
    # order of priority when searching for the binary (descending order):
    # - same as the root of the package (debugging purposes)
    # - directories-part as per specification in setup.cfg
    # - PATH env variable (if defined)
    ccs_flatten = which(ccsf_basename, dirname_x(__file__, 2), ccsf_dirname, '')

    # XXX currently ccs_flatten does not handle stdin (tempfile.mkstemp?)
    # XXX conversion is not idempotent, should prevent using ccs-flat as input
    #     (specifically, explicit ordering will get borken in subsequent round)
    in_file = in_obj('file')
    command = [ccs_flatten, in_file]
    log.info("running `{0}'".format(' '.join(command)))
    try:
        proc = OneoffWrappedStdinPopen(command, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise FilterError(self, "ccs_flatten binary seems unavailable")
    out, err = proc.communicate()
    if proc.returncode != 0 or out == '' and err != '':
        raise FilterError(self, "ccs_flatten exit code: {0}\n\t{1}",
                          proc.returncode, err)
    return ('bytestring', out)
