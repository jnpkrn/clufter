# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters.ccs_artefacts import artefact_cond_ra

ccs_artefacts = ''.join((
    artefact_cond_ra('@interfaces_file',
                     kind='A', desc="interfaces file for ASE server"),
    artefact_cond_ra('@login_file',
                     kind='S', desc="login/password pair file"),
))
