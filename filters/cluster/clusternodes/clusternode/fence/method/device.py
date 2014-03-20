# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from logging import getLogger
log = getLogger(__name__)

# XXX a bit dirty DRY approach
from os.path import dirname, exists, join
use = reduce(lambda a, b: dirname(a), xrange(5), __file__)
use = join(use, 'fencedevices', 'fencedevice')
use = use + '.py' if exists(use + '.py') else join(use, '__init__.py')
myglobals = {}
try:
    execfile(use, myglobals)
except IOError:
    log.error("Unable to refer to `{0}' file".format(use))
else:
    ccs_obfuscate_credentials = myglobals['ccs_obfuscate_credentials']
