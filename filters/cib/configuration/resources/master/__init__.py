# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....utils_2to3 import execfile
from ....utils_prog import dirname_x

from logging import getLogger
log = getLogger(__name__)

# XXX a bit dirty DRY approach
from os.path import join
use = join(dirname_x(__file__, 2), '_clone_master.py')
myglobals = dict(__package__=__package__, __name__=__name__)
try:
    execfile(use, myglobals)
except IOError:
    log.error("Unable to refer to `{0}' file".format(use))
else:
    cib2pcscmd = myglobals['cib2pcscmd']
