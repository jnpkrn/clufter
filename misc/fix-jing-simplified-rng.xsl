<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:rng="http://relaxng.org/ns/structure/1.0">

<xsl:template match="/rng:grammar">
    <xsl:copy>
        <xsl:copy-of select="@*"/>
        <xsl:attribute name="datatypeLibrary">
            <xsl:value-of select="'http://www.w3.org/2001/XMLSchema-datatypes'"/>
        </xsl:attribute>
        <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<!-- drop these -->
<xsl:template match="@ns[. = '']"/>
<xsl:template match="@datatypeLibrary[
                         . = ''
                         or
                         . = 'http://www.w3.org/2001/XMLSchema-datatypes'
                     ]"/>

<xsl:template match="@*|node()">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
</xsl:template>

</xsl:stylesheet>
