<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 exclude-result-prefixes="cbc">
 <xsl:output method="html" encoding="UTF-8" indent="no"/>
 <xsl:param name="document-type" select="'UNBOUND'"/>
 <xsl:param name="email-policy" select="'COVERING_EMAIL_ONLY'"/>
 <xsl:param name="profile-key" select="'UNBOUND'"/>
 <xsl:param name="render-purpose" select="'DOCUMENT'"/>
 <xsl:template match="/">
  <xsl:if test="local-name(/*) != $document-type or namespace-uri(/*) != concat('urn:oasis:names:specification:ubl:schema:xsd:',$document-type,'-2')"><xsl:message terminate="yes">REJECT: unexpected UBL document root or namespace</xsl:message></xsl:if>
  <xsl:if test="not($email-policy='COVERING_EMAIL_ONLY' or $email-policy='EMAIL_WITH_CANONICAL_DOCUMENT' or $email-policy='EMAIL_PRIMARY') or not($render-purpose='DOCUMENT' or $render-purpose='EMAIL')"><xsl:message terminate="yes">REJECT: unsupported policy or rendering purpose</xsl:message></xsl:if>
  <html lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/><title><xsl:value-of select="$document-type"/> — controlled UBL information view</title></head>
  <body style="font-family:Arial,Helvetica,sans-serif;color:#172b3d;background:#f5f7f9;padding:18px;margin:0;">
   <table role="presentation" cellspacing="0" cellpadding="0" style="max-width:920px;width:100%;margin:auto;background:white;border:1px solid #d8e1e8;border-collapse:collapse;">
    <tr><td style="padding:22px;background:#16354c;color:white;"><div style="font-size:12px">CONTROLLED BUSINESS DOCUMENT PROJECTION — CANDIDATE</div><h1 style="margin:10px 0 0;font-size:23px;color:white"><xsl:value-of select="$document-type"/></h1></td></tr>
    <tr><td style="padding:18px 22px;">
     <p><strong>Document ID:</strong> <xsl:value-of select="/*/cbc:ID[1]"/></p>
     <p><strong>Issue date:</strong> <xsl:value-of select="/*/cbc:IssueDate[1]"/></p>
     <p><strong>Currency:</strong> <xsl:value-of select="/*/cbc:DocumentCurrencyCode[1]"/></p>
     <p style="font-size:12px;color:#4d6275"><strong>Policy:</strong> <xsl:value-of select="$email-policy"/> | <strong>View:</strong> <xsl:value-of select="$render-purpose"/></p>
     <xsl:choose>
      <xsl:when test="$email-policy='COVERING_EMAIL_ONLY' and $render-purpose='EMAIL'">
       <p style="padding:12px;border-left:3px solid #ad6b3b;background:#fff5ea">This is a covering notification only. The signed or controlled parent document and any compulsory portal submission remain authoritative. No detailed business document content is disclosed in this email projection.</p>
      </xsl:when>
      <xsl:otherwise>
       <p style="font-size:12px;color:#4d6275">Source-order, nested and repeatable XML content is shown below. This human view does not replace validated canonical UBL XML or applicable legal and delivery controls.</p>
       <table role="presentation" cellspacing="0" cellpadding="5" style="width:100%;font-size:12px;border-collapse:collapse;">
        <tr><th align="left" style="background:#eaf0f5;border:1px solid #d8e1e8">UBL element / path</th><th align="left" style="background:#eaf0f5;border:1px solid #d8e1e8">Value / attributes</th></tr>
        <xsl:apply-templates select="/*/*" mode="line"/>
       </table>
      </xsl:otherwise>
     </xsl:choose>
    </td></tr>
    <tr><td style="padding:14px 22px;color:#56697b;background:#f2f6f8;font-size:11px"><p>Profile: <xsl:value-of select="$profile-key"/></p><p>Architecture projection only; release and correspondence must pass the governing CRM workflow. Binary payloads are retained in the canonical controlled document.</p></td></tr>
   </table>
  </body></html>
 </xsl:template>
 <xsl:template match="*" mode="line">
  <tr><td style="border:1px solid #d8e1e8;padding:5px;vertical-align:top">
   <xsl:for-each select="ancestor::*[parent::*]"><xsl:text>&#160;&#160;</xsl:text></xsl:for-each>
   <strong><xsl:value-of select="local-name()"/></strong><div style="color:#687a89;font-size:10px"><xsl:value-of select="namespace-uri()"/></div>
  </td><td style="border:1px solid #d8e1e8;padding:5px;vertical-align:top;white-space:pre-wrap">
   <xsl:choose>
    <xsl:when test="local-name()='EmbeddedDocumentBinaryObject' or local-name()='BinaryObject' or local-name()='GraphicImage' or local-name()='Picture'"><em>[binary retained in controlled source]</em></xsl:when>
    <xsl:when test="*"><em>Structured aggregate</em></xsl:when>
    <xsl:otherwise><xsl:value-of select="text()"/></xsl:otherwise>
   </xsl:choose>
   <xsl:for-each select="@*"><div style="font-size:11px;color:#586a76">@<xsl:value-of select="local-name()"/> = <xsl:value-of select="."/></div></xsl:for-each>
  </td></tr>
  <xsl:if test="not(local-name()='EmbeddedDocumentBinaryObject' or local-name()='BinaryObject')"><xsl:apply-templates select="*" mode="line"/></xsl:if>
 </xsl:template>
</xsl:stylesheet>
