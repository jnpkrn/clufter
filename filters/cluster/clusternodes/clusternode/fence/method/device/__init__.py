# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_2to3 import execfile
from ....utils_prog import dirname_x

from logging import getLogger
log = getLogger(__name__)

# XXX a bit dirty DRY approach
from os.path import exists, join
use = dirname_x(__file__, 6)
use = join(use, 'fencedevices', 'fencedevice')
use = use + '.py' if exists(use + '.py') else join(use, '__init__.py')
myglobals = {'__package__': __package__}
try:
    execfile(use, myglobals)
except IOError:
    log.error("Unable to refer to `{0}' file".format(use))
else:
    ccs_obfuscate_credentials = myglobals['ccs_obfuscate_credentials']
    # XXX might be in tighter bind to particular fencedevice-s
    ccs_artefacts = myglobals['ccs_artefacts_common_params']
