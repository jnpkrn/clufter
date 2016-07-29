# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""cmd-wrap command"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..command import Command
from ..protocol import protocols

from os import isatty


@Command.deco('cmd-wrap')
def cmd_wrap(cmd_ctxt,
             input="-",
             output="-",
             text_width='0'):
    """Wrap long lines carrying (fairly) convoluted shell commands

    Options:
        input       lines carrying moderately convoluted shell commands
        output      (hopefully) the same content fitting the text width
        text_width  for commands rewrapping (0/-1/neg. ~ auto/disable/hi-limit)
    """
    cmd_ctxt['text_width'] = text_width
    cmd_ctxt.filter('cmd-wrap')['color'] = output == "-" and isatty(1) and \
                                           cmd_ctxt['color'] is not False \
                                           or cmd_ctxt['color']

    file_proto = protocols.plugins['file'].ensure_proto
    return (
        file_proto(input),
        file_proto(output),
    )
