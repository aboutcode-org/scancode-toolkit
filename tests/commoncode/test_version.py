#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import unittest

from commoncode import version


class TestVersionHint(unittest.TestCase):

    def test_version_hint(self):
        data = {
            '/xmlgraphics/fop/source/fop-1.0-src.zip': '1.0',
            '/xml/xindice/xml-xindice-1.2m1-src.zip': '1.2m1',
            '/xmlgraphics/fop/binaries/fop-0.94-bin-jdk1.3.tar.gz': '0.94',
            '/xmlgraphics/batik/batik-src-1.7beta1.zip': '1.7beta1',
            '/xmlgraphics/batik/batik-1.7-jre13.zip': '1.7',
            '/xmlbeans/source/xmlbeans-2.3.0-src.tgz': '2.3.0',
            '/xml/xindice/source/xml-xindice-1.2m1-src.tar.gz': '1.2m1',
            '/xml/xerces-p/binaries/XML-Xerces-2.3.0-4-win32.zip': '2.3.0-4',
            '/xml/xerces-p/source/XML-Xerces-2.3.0-3.tar.gz': '2.3.0-3',
            '/xml/xalan-j/source/xalan-j_2_7_0-src-2jars.tar.gz': '2_7_0',
            '/xml/security/java-library/xml-security-src-1_0_5D2.zip': '1_0_5D2',
            '/xml/commons/binaries/xml-commons-external-1.4.01-bin.zip': '1.4.01',
            '/xml/commons/xml-commons-1.0.b2.zip': '1.0.b2',
            '/xml/cocoon/3.0/cocoon-all-3.0.0-alpha-1-dist.tar.gz': '3.0.0-alpha-1',
            '/xerces/j/source/Xerces-J-tools.2.10.0-xml-schema-1.1-beta.tar.gz': '2.10.0',
            '/xerces/c/3/binaries/xerces-c-3.1.1-x86_64-solaris-cc-5.10.tar.gz': '3.1.1',
            '/xerces/c/3/binaries/xerces-c-3.1.1-x86_64-windows-vc-8.0.zip': '3.1.1',
            '/xerces/c/2/binaries/xerces-c_2_8_0-x86-windows-vc_7_1.zip': '2_8_0',
            '/ws/woden/1.0M8/apache-woden-src-1.0M8.tar.gz': '1.0M8',
            '/ws/scout/0_7rc1/source/scout-0.7rc1-src.zip': '0.7rc1',
            '/ws/juddi/3_0/juddi-portal-bundle-3.0.0.rc1.zip': '3.0.0.rc1',
            '/ws/juddi/3_0/juddi-portal-bundle-3.0.0.beta.zip': '3.0.0.beta',
            '/ws/juddi/2_0RC7/juddi-tomcat-2.0rc7.zip': '2.0rc7',
            '/ws/axis2/tools/1_4_1/axis2-wsdl2code-maven-plugin-1.4.1.jar': '1.4.1',
            '/ws/axis/1_4/axis-src-1_4.zip': '1_4',
            '/ws/axis-c/source/win32/axis-c-1.6b-Win32-trace-src.zip': '1.6b',
            '/tuscany/java/sca/2.0-M5/apache-tuscany-sca-all-2.0-M5-src.tar.gz': '2.0-M5',
            '/turbine/turbine-2.3.3-rc1/source/turbine-2.3.3-RC1-src.zip': '2.3.3-RC1',
            '/tomcat/tomcat-connectors/jk/binaries/win64/jk-1.2.30/ia64/symbols-1.2.30.zip': '1.2.30',
            '/tomcat/tomcat-7/v7.0.0-beta/bin/apache-tomcat-7.0.0-windows-i64.zip': '7.0.0',
            '/tomcat/tomcat-4/v4.1.40/bin/apache-tomcat-4.1.40-LE-jdk14.exe': '4.1.40',
            '/tapestry/tapestry-src-5.1.0.5.tar.gz': '5.1.0.5',
            '/spamassassin/source/Mail-SpamAssassin-rules-3.3.0.r901671.tgz': '3.3.0.r901671',
            '/spamassassin/Mail-SpamAssassin-rules-3.3.1.r923257.tgz': '3.3.1.r923257',
            '/shindig/1.1-BETA5-incubating/shindig-1.1-BETA5-incubating-source.zip': '1.1-BETA5',
            '/servicemix/nmr/1.0.0-m3/apache-servicemix-nmr-1.0.0-m3-src.tar.gz': '1.0.0-m3',
            '/qpid/0.6/qpid-dotnet-0-10-0.6.zip': '0.6',
            '/openjpa/2.0.0-beta/apache-openjpa-2.0.0-beta-binary.zip': '2.0.0-beta',
            '/myfaces/source/portlet-bridge-2.0.0-alpha-2-src-all.tar.gz': '2.0.0-alpha-2',
            '/myfaces/source/myfaces-extval20-2.0.3-src.tar.gz': '2.0.3',
            '/harmony/milestones/6.0/debian/amd64/harmony-6.0-classlib_0.0r946981-1_amd64.deb': '6.0',
            '/geronimo/eclipse/updates/plugins/org.apache.geronimo.st.v21.ui_2.1.1.jar': '2.1.1',
            '/directory/studio/update/1.x/plugins/org.apache.directory.studio.aciitemeditor_1.5.2.v20091211.jar': '1.5.2.v20091211',
            '/db/torque/torque-3.3/source/torque-gen-3.3-RC3-src.zip': '3.3-RC3',
            '/cayenne/cayenne-3.0B1.tar.gz': '3.0B1',
            '/cayenne/cayenne-3.0M4-macosx.dmg': '3.0M4',
            '/xmlgraphics/batik/batik-docs-current.zip': 'current',
            '/xmlgraphics/batik/batik-docs-previous.zip': 'previous',
            '/poi/dev/bin/poi-bin-3.7-beta1-20100620.zip': '3.7-beta1-20100620',
            '/excalibur/avalon-logkit/source/excalibur-logkit-2.0.dev-0-src.zip': '2.0.dev-0',
            '/db/derby/db-derby-10.4.2.0/derby_core_plugin_10.4.2.zip': '10.4.2',
            '/httpd/modpython/win/2.7.1/mp152dll.zip': '2.7.1',
            '/perl/mod_perl-1.31/apaci/mod_perl.config.sh': '1.31',
            '/xml/xerces-j/old_xerces2/Xerces-J-bin.2.0.0.alpha.zip': '2.0.0.alpha',
            '/xml/xerces-p/archives/XML-Xerces-1.7.0_0.tar.gz': '1.7.0_0',
            '/httpd/docs/tools-2004-05-04.zip': '2004-05-04',
            '/ws/axis2/c/M0_5/axis2c-src-M0.5.tar.gz': 'M0.5',
            '/jakarta/poi/dev/src/jakarta-poi-1.8.0-dev-src.zip': '1.8.0-dev',
            '/tapestry/tapestry-4.0-beta-8.zip': '4.0-beta-8',
            '/openejb/3.0-beta-1/openejb-3.0-beta-1.zip': '3.0-beta-1',
            '/tapestry/tapestry-4.0-rc-1.zip': '4.0-rc-1',
            '/jakarta/tapestry/source/3.0-rc-3/Tapestry-3.0-rc-3-src.zip': '3.0-rc-3',
            '/jakarta/lucene/binaries/lucene-1.3-final.tar.gz': '1.3-final',
            '/jakarta/tapestry/binaries/3.0-beta-1a/Tapestry-3.0-beta-1a-bin.zip': '3.0-beta-1a',
            '/poi/release/bin/poi-bin-3.0-FINAL-20070503.tar.gz': '3.0-FINAL-20070503',
            '/harmony/milestones/M4/apache-harmony-hdk-r603534-linux-x86-32-libstdc++v6-snapshot.tar.gz': 'r603534',
            '/ant/antidote/antidote-20050330.tar.bz2': '20050330',
            '/apr/not-released/apr_20020725223645.tar.gz': '20020725223645',
            '/ibatis/source/ibatis.net/src-revision-709676.zip': 'revision-709676',
            '/ws/axis-c/source/win32/axis-c-src-1-2-win32.zip': '1-2',
            '/jakarta/slide/most-recent-2.0rc1-binaries/jakarta-slide 2.0rc1 jakarta-tomcat-4.1.30.zip': '2.0rc1',
            '/httpd/modpython/win/3.0.1/python2.2.1-apache2.0.43.zip': '2.2.1',
            '/ant/ivyde/updatesite/features/org.apache.ivy.feature_2.1.0.cr1_20090319213629.jar': '2.1.0.cr1_20090319213629',
            '/jakarta/poi/dev/bin/poi-2.0-pre1-20030517.jar': '2.0-pre1-20030517',
            '/jakarta/poi/release/bin/jakarta-poi-1.5.0-FINAL-bin.zip': '1.5.0-FINAL',
            '/jakarta/poi/release/bin/poi-bin-2.0-final-20040126.zip': '2.0-final-20040126',
            '/activemq/apache-activemq/5.0.0/apache-activemq-5.0.0-sources.jar': '5.0.0',
            '/turbine/turbine-2.2/source/jakarta-turbine-2.2-B1.tar.gz': '2.2-B1',
            '/ant/ivyde/updatesite/features/org.apache.ivy.feature_2.0.0.cr1.jar': '2.0.0.cr1',
            '/ant/ivyde/updatesite/features/org.apache.ivy.feature_2.0.0.final_20090108225011.jar': '2.0.0.final_20090108225011',
            '/ws/axis/1_2RC3/axis-src-1_2RC3.zip': '1_2RC3',
            '/commons/lang/old/v1.0-b1.1/commons-lang-1.0-b1.1.zip': '1.0-b1.1',
            '/commons/net/binaries/commons-net-1.2.0-release.tar.gz': '1.2.0-release',
            '/ant/ivyde/2.0.0.final/apache-ivyde-2.0.0.final-200907011148-RELEASE.tgz': '2.0.0.final-200907011148-RELEASE',
            '/geronimo/eclipse/updates/plugins/org.apache.geronimo.jetty.j2ee.server.v11_1.0.0.jar': 'v11_1.0.0',
            '/jakarta/cactus/binaries/jakarta-cactus-13-1.7.1-fixed.zip': '1.7.1-fixed',
            '/jakarta/jakarta-turbine-maven/maven/jars/maven-1.0-b5-dev.20020731.085427.jar': '1.0-b5-dev.20020731.085427',
            '/xml/xalan-j/source/xalan-j_2_5_D1-src.tar.gz': '2_5_D1',
            '/ws/woden/IBuilds/I20051002_1145/woden-I20051002_1145.tar.bz2': 'I20051002_1145',
            '/commons/beanutils/source/commons-beanutils-1.8.0-BETA-src.tar.gz': '1.8.0-BETA',
            '/cocoon/BINARIES/cocoon-2.0.3-vm14-bin.tar.gz': '2.0.3-vm14',
            '/felix/xliff_filters_v1_2_7_unix.jar': 'v1_2_7',
            '/excalibur/releases/200702/excalibur-javadoc-r508111-15022007.tar.gz': 'r508111-15022007',
            '/geronimo/eclipse/updates/features/org.apache.geronimo.v20.feature_2.0.0.jar': 'v20.feature_2.0.0',
            '/geronimo/2.1.6/axis2-jaxws-1.3-G20090406.jar': '1.3-G20090406',
            '/cassandra/debian/pool/main/c/cassandra/cassandra_0.4.0~beta1-1.diff.gz': '0.4.0~beta1-1',
            '/ha-api-3.1.6.jar': '3.1.6',
            'ha-api-3.1.6.jar': '3.1.6'
            }

        # FIXME: generate a test function for each case
        for path in data:
            expected = data[path]
            if not expected.lower().startswith('v'):
                expected = 'v ' + expected
            assert version.hint(path) == expected
