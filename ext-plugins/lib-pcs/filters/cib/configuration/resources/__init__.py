# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

from ....filters.pcs_resource import map_resource_to_pkgs

pcs_resource_deps = ('''\
    <xsl:for-each select=".//primitive">
'''
+ map_resource_to_pkgs('ocf:heartbeat:IPaddr2',       'iproute')
+ map_resource_to_pkgs('ocf:heartbeat:LVM',           'lvm')
+ map_resource_to_pkgs('ocf:heartbeat:VirtualDomain', 'virsh')
+ map_resource_to_pkgs('ocf:heartbeat:apache',        'httpd')
+ map_resource_to_pkgs('ocf:heartbeat:mysql',         'mysql')
+ map_resource_to_pkgs('ocf:heartbeat:nfsserver',     'nfs-utils')
+ map_resource_to_pkgs('ocf:heartbeat:pgsql',         'postgresql')
 + '''\
    </xsl:for-each>
''')
