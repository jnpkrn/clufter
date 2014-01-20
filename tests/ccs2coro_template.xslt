<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="cluster">
    <corosync>
      <xsl:apply-templates select=".//clusternodes"/>
      <xsl:apply-templates select=".//cman"/>
      <xsl:apply-templates select=".//logging"/>
      <totem version="2" cluster_name="{@name}">
        <xsl:apply-templates select=".//totem"/>
      </totem>
    </corosync>
  </xsl:template>
  <xsl:template match="clusternodes">
    <nodelist>
      <xsl:apply-templates select=".//clusternode"/>
    </nodelist>
  </xsl:template>
  <xsl:template match="logging">
    <logging>
      <!-- XXX: the latter match (if any) should overwrite the former -->
      <xsl:apply-templates select=".//logging_daemon"/>
    </logging>
  </xsl:template>
  <xsl:template match="cman">
    <quorum provider="corosync_votequorum">
      <xsl:copy-of select="@*[             contains(concat(                 '|expected_votes',                 '|two_node',                 '|'), concat('|', name(), '|'))]"/>
    </quorum>
  </xsl:template>
  <xsl:template match="totem">
    <xsl:copy-of select="@*[         contains(concat(             '|consensus',             '|fail_recv_const',             '|join',             '|max_messages',             '|miss_count_const',             '|netmtu',             '|rrp_mode',             '|rrp_problem_count_threshold',             '|secauth',             '|seqno_unchanged_const',             '|token',             '|token_retransmits_before_loss_const',             '|window_size',             '|'), concat('|', name(), '|'))]"/>
    <xsl:apply-templates select=".//interface"/>
  </xsl:template>
  <xsl:template match="interface">
    <xsl:copy>
      <xsl:copy-of select="@*[         contains(concat(             '|ringnumber',             '|bindnetaddr',             '|broadcast',             '|mcastaddr',             '|mcastport',             '|ttl',             '|'), concat('|', name(), '|'))]"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="logging_daemon">
    <xsl:for-each select="self::node()[@name='corosync' and @subsys]">
      <logger_subsys>
        <xsl:copy-of select="@*[                 contains(concat(                     '|debug',                     '|logfile',                     '|subsys',                     '|to_logfile',                     '|to_syslog',                     '|'), concat('|', name(), '|'))]"/>
      </logger_subsys>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="clusternode">
    <node id="{@nodeid}" ring0_addr="{@name}"/>
  </xsl:template>
</xsl:stylesheet>
