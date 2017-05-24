# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
"""Testing general cluster helpers"""
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
c = lambda x: compile(x.read(), x.name, 'exec')
with open(join(dirname(__file__), '_go')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(c(f))


from unittest import TestCase

from .facts import cluster_pcs_flatiron, cluster_pcs_1_2, cmd_pkg_install, \
                   component_or_state, infer, package


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
        self.assertFalse(cluster_pcs_1_2('linux', ('redhat', ' 6.0'   )))
        self.assertFalse(cluster_pcs_1_2('linux', ('redhat', ' 6.1'   )))
        self.assertFalse(cluster_pcs_1_2('linux', ('redhat', ' 6.2'   )))
        self.assertFalse(cluster_pcs_1_2('linux', ('redhat', ' 6.4'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.5'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.8'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 6.22'  )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 7.0'   )))
        self.assertTrue (cluster_pcs_1_2('linux', ('redhat', ' 7.1'   )))
        self.assertFalse(cluster_pcs_1_2('linux', ('fedora', '13'     )))
        self.assertFalse(cluster_pcs_1_2('linux', ('fedora', '14'     )))
        self.assertFalse(cluster_pcs_1_2('linux', ('fedora', '15'     )))
        self.assertFalse(cluster_pcs_1_2('linux', ('fedora', '16'     )))
        self.assertFalse(cluster_pcs_1_2('linux', ('fedora', '17'     )))
        self.assertTrue (cluster_pcs_1_2('linux', ('fedora', '18'     )))
        self.assertFalse(cluster_pcs_1_2('linux', ('debian', 'squeeze')))
        self.assertFalse(cluster_pcs_1_2('linux', ('debian', 'wheezy' )))


class TestPackage(TestCase):
    def test_package_rhel60(self):
        sys_id = 'linux', ('redhat', ' 6.0')
        self.assertEqual(package('lvm',        *sys_id), 'lvm2')
        self.assertEqual(package('mysql',      *sys_id), 'mysql-server')
        self.assertEqual(package('postgresql', *sys_id), 'postgresql-server')
        self.assertEqual(package('virsh',      *sys_id), 'libvirt-client')
    def test_package_rhel70(self):
        sys_id = 'linux', ('redhat', ' 7.0')
        self.assertEqual(package('lvm',        *sys_id), 'lvm2')
        self.assertEqual(package('mysql',      *sys_id), 'mariadb-server')
        self.assertEqual(package('postgresql', *sys_id), 'postgresql-server')
        self.assertEqual(package('virsh',      *sys_id), 'libvirt-client')


class TestPkgInstall(TestCase):
    def test_pkg_install_rhel60(self):
        sys_id = 'linux', ('redhat', ' 6.0')
        self.assertEqual(cmd_pkg_install(('mc', 'vim'), *sys_id),
                         'yum install -y mc vim')
    def test_pkg_install_rhel70(self):
        sys_id = 'linux', ('redhat', ' 7.0')
        self.assertEqual(cmd_pkg_install(('mc', 'vim'), *sys_id),
                         'yum install -y mc vim')
    def test_pkg_install_fedora19(self):
        sys_id = 'linux', ('fedora', ' 19')
        self.assertEqual(cmd_pkg_install(('mc', 'vim'), *sys_id),
                         'yum install -y mc vim')
    def test_pkg_install_unknown(self):
        sys_id = 'linux', ('frobnical', ' 21')
        self.assertEqual(cmd_pkg_install(('gnomovision', ), *sys_id), '')
    def test_pkg_install_empty(self):
        sys_id = 'linux', ('fedora', ' 21')
        self.assertEqual(cmd_pkg_install((), *sys_id), '')
    def test_pkg_install_generator(self):
        sys_id = 'linux', ('fedora', ' 21')
        self.assertEqual(cmd_pkg_install(iter(('mc', 'vim')), *sys_id),
                         'yum install -y mc vim')
    def test_pkg_install_generator_empty(self):
        sys_id = 'linux', ('fedora', ' 21')
        self.assertEqual(cmd_pkg_install(iter(()), *sys_id), '')


class TestExtra(TestCase):
    def test_extra_corosync_qnet(self):
        check = 'comp:corosync[qnet]'
        self.assertFalse(infer(check, 'linux', ('redhat', ' 7.2')))
        self.assertTrue(infer(check, 'linux', ('redhat', ' 7.3')))

    def test_extra_pacemaker_schema2(self):
        check = 'comp:pacemaker[schema-2.0]'
        self.assertFalse(infer(check, 'linux', ('redhat', '6.5')))
        self.assertTrue(infer(check, 'linux', ('redhat', '6.6')))

    def test_extra_pcs_agents_via_pacemaker(self):
        check = 'comp:pcs[agents-via-pacemaker]'
        self.assertFalse(infer(check, 'linux', ('redhat', '6.9')))
        self.assertTrue(infer(check, 'linux', ('redhat', '7.4')))

    def test_extra_pcs_utilization(self):
        check = 'comp:pcs[utilization]'
        self.assertFalse(infer(check, 'linux', ('redhat', '6.0')))
        self.assertTrue (infer(check, 'linux', ('redhat', '6.8')))
        self.assertFalse(infer(check, 'linux', ('redhat', '7.1')))
        self.assertFalse(infer(check, 'linux', ('redhat', '7.2')))
        self.assertTrue (infer(check, 'linux', ('redhat', '7.3')))

    def test_extra_resource_agents_named(self):
        check = 'resource-agents[named]'
        self.assertEqual(component_or_state(check, 'linux', ('redhat', '6.0')),
                         "(resource-agents yet untracked) / linux-redhat-6.0")
        self.assertEqual(component_or_state(check, 'linux', ('redhat', '6.5')),
                         "resource-agents=3.9.2 / linux-redhat-6.5")
        self.assertEqual(component_or_state(check, 'linux', ('redhat', '6.6')),
                         "")
        self.assertEqual(component_or_state(check, 'linux', ('debian', 'squeeze')),
                         "(resource-agents yet untracked) / linux-debian-squeeze")
        self.assertEqual(component_or_state(check, 'linux', ('debian', 'wheezy')),
                         "resource-agents=3.9.2 / linux-debian-wheezy")
        self.assertEqual(component_or_state(check, 'linux', ('debian', 'jessie')),
                         "")


from os.path import join, dirname; from sys import modules as m  # 2/3 compat
b = m.get('builtins', m.get('__builtin__')); e, E, h = 'exec', 'execfile', hash
with open(join(dirname(__file__), '_gone')) as f:
    getattr(b, e, getattr(b, E, h)(f.name).__repr__.__name__.__ne__)(f.read())
