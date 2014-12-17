# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing general cluster helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname as d; execfile(join(d(d((__file__))), '_go'))


from unittest import TestCase

from .facts import cluster_pcs_flatiron, cluster_pcs_1_2


class TestClusterSystem(TestCase):
    def test_cluster_pcs_flatiron(self):
        self.assertFalse(cluster_pcs_flatiron('linux', ('redhat', ' 6.0' )))
        self.assertFalse(cluster_pcs_flatiron('linux', ('redhat', ' 6.1' )))
        self.assertFalse(cluster_pcs_flatiron('linux', ('redhat', ' 6.2' )))
        self.assertFalse(cluster_pcs_flatiron('linux', ('redhat', ' 6.4' )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('redhat', ' 6.5' )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('redhat', ' 6.8' )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('redhat', ' 6.22')))
        self.assertFalse(cluster_pcs_flatiron('linux', ('redhat', ' 7.0' )))
        self.assertFalse(cluster_pcs_flatiron('linux', ('redhat', ' 7.1' )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('fedora', '13'   )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('fedora', '14'   )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('fedora', '15'   )))
        self.assertTrue (cluster_pcs_flatiron('linux', ('fedora', '16'   )))
        self.assertFalse(cluster_pcs_flatiron('linux', ('fedora', '17'   )))
    def test_cluster_pcs_1_2(self):
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.0'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.1'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.2'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.4'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.5'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.8'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.22'  )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 7.0'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 7.1'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('fedora', '13'     )))
        self.assertTrue (cluster_pcs_1_2('linux', ('fedora', '14'     )))
        self.assertTrue (cluster_pcs_1_2('linux', ('fedora', '15'     )))
        self.assertTrue (cluster_pcs_1_2('linux', ('fedora', '16'     )))
        self.assertTrue (cluster_pcs_1_2('linux', ('fedora', '17'     )))
        self.assertFalse(cluster_pcs_1_2('linux', ('debian', 'squeeze')))


from os.path import join, dirname as d; execfile(join(d(d(__file__)), '_gone'))
