<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 exclude-result-prefixes="cbc">
 <xsl:output method="text" encoding="UTF-8"/>
 <xsl:param name="document-type" select="'UNBOUND'"/>
 <xsl:param name="email-policy" select="'COVERING_EMAIL_ONLY'"/>
 <xsl:param name="profile-key" select="'UNBOUND'"/>
 <xsl:param name="render-purpose" select="'DOCUMENT'"/>
 <xsl:template match="/">
  <xsl:if test="local-name(/*) != $document-type or namespace-uri(/*) != concat('urn:oasis:names:specification:ubl:schema:xsd:',$document-type,'-2')"><xsl:message terminate="yes">REJECT: wrong root</xsl:message></xsl:if>
  <xsl:if test="not($email-policy='COVERING_EMAIL_ONLY' or $email-policy='EMAIL_WITH_CANONICAL_DOCUMENT' or $email-policy='EMAIL_PRIMARY') or not($render-purpose='DOCUMENT' or $render-purpose='EMAIL')"><xsl:message terminate="yes">REJECT: unsupported policy</xsl:message></xsl:if>
  <xsl:text>CONTROLLED UBL INFORMATION VIEW&#10;Document type: </xsl:text><xsl:value-of select="$document-type"/>
  <xsl:text>&#10;Document ID: </xsl:text><xsl:value-of select="/*/cbc:ID[1]"/>
  <xsl:text>&#10;Issue date: </xsl:text><xsl:value-of select="/*/cbc:IssueDate[1]"/>
  <xsl:text>&#10;Policy: </xsl:text><xsl:value-of select="$email-policy"/>
  <xsl:text>&#10;Purpose: </xsl:text><xsl:value-of select="$render-purpose"/><xsl:text>&#10;</xsl:text>
  <xsl:choose>
   <xsl:when test="$render-purpose='EMAIL' and $email-policy='COVERING_EMAIL_ONLY'"><xsl:text>COVERING EMAIL ONLY. Controlled parent document and statutory delivery conditions prevail.&#10;</xsl:text></xsl:when>
   <xsl:otherwise>
    <xsl:text>BEGIN STRUCTURED UBL CONTENT&#10;</xsl:text><xsl:apply-templates select="/*/*" mode="flat"/>
    <xsl:text>END STRUCTURED CONTENT&#10;</xsl:text>
   </xsl:otherwise>
  </xsl:choose>
  <xsl:text>Profile: </xsl:text><xsl:value-of select="$profile-key"/><xsl:text>&#10;NOT A SEND APPROVAL&#10;</xsl:text>
 </xsl:template>
 <xsl:template match="*" mode="flat">
  <xsl:for-each select="ancestor::*[parent::*]"><xsl:text>  </xsl:text></xsl:for-each>
  <xsl:value-of select="local-name()"/><xsl:text>: </xsl:text>
  <xsl:choose>
   <xsl:when test="local-name()='EmbeddedDocumentBinaryObject' or local-name()='BinaryObject' or local-name()='GraphicImage' or local-name()='Picture'"><xsl:text>[binary retained in controlled source]</xsl:text></xsl:when>
   <xsl:when test="*"><xsl:text>[aggregate]</xsl:text></xsl:when>
   <xsl:otherwise><xsl:value-of select="text()"/></xsl:otherwise>
  </xsl:choose>
  <xsl:for-each select="@*"><xsl:text> @</xsl:text><xsl:value-of select="local-name()"/><xsl:text>=</xsl:text><xsl:value-of select="."/></xsl:for-each>
  <xsl:text>&#10;</xsl:text>
  <xsl:if test="not(local-name()='EmbeddedDocumentBinaryObject' or local-name()='BinaryObject')"><xsl:apply-templates select="*" mode="flat"/></xsl:if>
 </xsl:template>
</xsl:stylesheet>
