<?php

/**
 * $Id: ldapbaseauthenticationprovider.inc.php 6139 2006-12-20 11:51:02Z conradverm $
 *
 * The contents of this file are subject to the KnowledgeTree Public
 * License Version 1.1 ("License"); You may not use this file except in
 * compliance with the License. You may obtain a copy of the License at
 * http://www.ktdms.com/KPL
 * 
 * Software distributed under the License is distributed on an "AS IS"
 * basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 * 
 * The Original Code is: KnowledgeTree Open Source
 * 
 * The Initial Developer of the Original Code is The Jam Warehouse Software
 * (Pty) Ltd, trading as KnowledgeTree.
 * Portions created by The Jam Warehouse Software (Pty) Ltd are Copyright
 * (C) 2006 The Jam Warehouse Software (Pty) Ltd;
 * All Rights Reserved.
 *
 */

require_once(KT_LIB_DIR . '/authentication/authenticationprovider.inc.php');
require_once(KT_LIB_DIR . '/authentication/Authenticator.inc');

class KTLDAPBaseAuthenticationProvider extends KTAuthenticationProvider {
    var $sName = "LDAP authentication provider";
    var $sNamespace = "ktstandard.authentication.ldapprovider";

    var $aAttributes = array ("cn", "uid", "givenname", "sn", "mail", "mobile");
    var $aMembershipAttributes = array ("memberOf");

    // {{{ KTLDAPBaseAuthenticationProvider
    function KTLDAPBaseAuthenticationProvider() {
        parent::KTAuthenticationProvider();
        $this->aConfigMap = array(
            'servername' => _kt('LDAP Server'),
            'serverport' => _kt('The LDAP server port'),
            'basedn' => _kt('Base DN'),
            'searchuser' => _kt('LDAP Search User'),
            'searchpassword' => _kt('LDAP Search Password'),
            'searchattributes' => _kt('Search Attributes'),
            'objectclasses' => _kt('Object Classes'),
            'tls' => _kt('Use Transaction Layer Security (TLS)'),
        );
    }
    // }}}

    // {{{ showSource
    function showSource($oSource) {
        $aConfig = unserialize($oSource->getConfig());
        if (empty($aConfig)) {
            $aConfig = array();
        }
        $sRet = "<dl>\n";
        foreach ($this->aConfigMap as $sSettingName => $sName) {
            $sRet .= "  <dt>$sName</dt>\n";
            $sValue = KTUtil::arrayGet($aConfig, $sSettingName, _kt("Unset"), false);
            if (is_array($sValue)) {
                $sRet .= "  <dd>" . join("<br />", $sValue) . "</dd>\n";
            } else if (is_bool($sValue)) {
                if ($sValue === true) {
                    $sRet .= "  <dd>" . _kt('True') . "</dd>\n";
                } else {
                    $sRet .= "  <dd>" . _kt('False') . "</dd>\n";
                }
            } else if ($sSettingName == 'searchpassword') {
                $sRet .= "  <dd><em>*** Hidden ***</em></dd>\n";
            } else {
                $sRet .= "  <dd>" . $sValue . "</dd>\n";
            }
        }
        $sRet .= "</dl>\n";
        return $sRet;
    }
    // }}}

    // {{{ showUserSource
    function showUserSource($oUser, $oSource) {
        return '<a href="' . KTUtil::addQueryStringSelf('action=editUserSource&user_id=' . $oUser->getId()) . '">' . _kt('Edit LDAP info') . '</a>';
    }
    // }}}

    // {{{ do_editUserSource
    function do_editUserSource() {
        $submit = KTUtil::arrayGet($_REQUEST, 'submit');
        if (KTUtil::arrayGet($submit, 'save')) {
            return $this->_do_saveUserSource();
        }

        $user_id = KTUtil::arrayGet($_REQUEST, 'user_id');
        $oUser =& $this->oValidator->validateUser($user_id);

        $this->oPage->setBreadcrumbDetails(_kt("editing LDAP details"));
        $oTemplate = $this->oValidator->validateTemplate('ktstandard/authentication/ldapedituser');

        $oAuthenticationSource = KTAuthenticationSource::getForUser($oUser);

        $dn = $oUser->getAuthenticationDetails();

        $fields = array();
        $fields[] = new KTStringWidget(_kt('Distinguished name'), _kt('The location of this user in the LDAP tree'), 'dn', $dn, $this->oPage, true);

        $aTemplateData = array(
            'context' => &$this,
            'fields' => $fields,
            'user' => $oUser,
        );
        return $oTemplate->render($aTemplateData);
    }
    // }}}

    // {{{ _do_saveUserSource
    function _do_saveUserSource() {
        $user_id = KTUtil::arrayGet($_REQUEST, 'user_id');
        $oUser =& $this->oValidator->validateUser($user_id);

        $dn = KTUtil::arrayGet($_REQUEST, 'dn', "");
        if (empty($dn)) {
            $this->errorRedirecToMain("Failed to validate LDAP details");
        }
        $oUser->setAuthenticationDetails($dn);
        $oUser->update();
        $this->successRedirectTo("editUser", _kt("Details updated"),
            sprintf('user_id=%d', $oUser->getId()));
    }
    // }}}

    // {{{ do_editSourceProvider
    function do_editSourceProvider() {
        require_once(KT_LIB_DIR . '/widgets/fieldWidgets.php');
        $this->oPage->setBreadcrumbDetails(_kt("editing LDAP settings"));
        $oTemplate = $this->oValidator->validateTemplate('ktstandard/authentication/ldapeditsource');
        $iSourceId = KTUtil::arrayGet($_REQUEST, 'source_id');
        $oSource = KTAuthenticationSource::get($iSourceId);
        $aConfig = unserialize($oSource->getConfig());
        if (empty($aConfig)) {
            $aConfig = array('serverport'=>389);
        }
        $aConfig['searchattributes'] = KTUtil::arrayGet($aConfig, 'searchattributes', split(',', 'cn,mail,sAMAccountName'));
        $aConfig['objectclasses'] = KTUtil::arrayGet($aConfig, 'objectclasses', split(',', 'user,inetOrgPerson,posixAccount'));
        $fields = array();
        $fields[] = new KTStringWidget(_kt('Server name'), _kt('The host name or IP address of the LDAP server'), 'servername', $aConfig['servername'], $this->oPage, true);
        $fields[] = new KTIntegerWidget(_kt('Server Port'), _kt('The port of the LDAP server (default: 389)'), 'serverport', $aConfig['serverport'], $this->oPage, true);
        $fields[] = new KTCheckboxWidget(_kt('Use Transaction Layer Security (TLS)'), _kt('Whether to use Transaction Layer Security (TLS), which encrypts traffic to and from the LDAP server'), 'tls_bool', $aConfig['tls'], $this->oPage, true);
        $fields[] = new KTStringWidget(_kt('Base DN'), _kt('The location in the LDAP directory to start searching from (CN=Users,DC=mycorp,DC=com)'), 'basedn', $aConfig['basedn'], $this->oPage, true);
        $fields[] = new KTStringWidget(_kt('Search User'), _kt('The user account in the LDAP directory to perform searches in the LDAP directory as (such as CN=searchUser,CN=Users,DC=mycorp,DC=com or searchUser@mycorp.com)'), 'searchuser', $aConfig['searchuser'], $this->oPage, true);
        $fields[] = new KTPasswordWidget(_kt('Search Password'), _kt('The password for the user account in the LDAP directory that performs searches'), 'searchpassword', $aConfig['searchpassword'], $this->oPage, true);
        $aOptions = array(
            'rows' => 7,
            'cols' => 25,
        );
        $fields[] = new KTTextWidget(_kt('Search Attributes'), _kt('The LDAP attributes to use to search for users when given their name (one per line, examples: <strong>cn</strong>, <strong>mail</strong>)'), 'searchattributes_nls', join("\n", $aConfig['searchattributes']), $this->oPage, true, null, null, $aOptions);
        $fields[] = new KTTextWidget(_kt('Object Classes'), _kt('The LDAP object classes to search for users (one per line, example: <strong>user</strong>, <strong>inetOrgPerson</strong>, <strong>posixAccount</strong>)'), 'objectclasses_nls', join("\n", $aConfig['objectclasses']), $this->oPage, true, null, null, $aOptions);
        $aTemplateData = array(
            'context' => &$this,
            'fields' => $fields,
            'source' => $oSource,
        );
        return $oTemplate->render($aTemplateData);
    }
    // }}}

    // {{{ do_performEditSourceProvider
    function do_performEditSourceProvider() {
        $iSourceId = KTUtil::arrayGet($_REQUEST, 'source_id');
        $oSource = KTAuthenticationSource::get($iSourceId);
        $aConfig = unserialize($oSource->getConfig());
        $aConfig['searchattributes'] = KTUtil::arrayGet($aConfig, 'searchattributes', split(',', 'cn,mail,sAMAccountName'));
        $aConfig['objectclasses'] = KTUtil::arrayGet($aConfig, 'objectclasses', split(',', 'user,inetOrgPerson,posixAccount'));
        $aConfig['tls'] = false;
        $aConfig['serverport'] =389;

        foreach ($this->aConfigMap as $k => $v) {
            $sValue = KTUtil::arrayGet($_REQUEST, $k . '_nls');
            if ($sValue) {
                $nls_array = split("\n", $sValue);
                $final_array = array();
                foreach ($nls_array as $nls_item) {
                    $nls_item = trim($nls_item);
                    if (empty($nls_item)) {
                        continue;
                    }
                    $final_array[] = $nls_item;
                }
                $aConfig[$k] = $final_array;
                continue;
            }
            if (array_key_exists($k . '_bool', $_REQUEST)) {
                if ($_REQUEST[$k . '_bool']) {
                    $aConfig[$k] = true;
                } else {
                    $aConfig[$k] = false;
                }
                continue;
            }
            $sValue = KTUtil::arrayGet($_REQUEST, $k);
            if ($sValue) {
                $aConfig[$k] = $sValue;
            }
        }
        $oSource->setConfig(serialize($aConfig));
        $res = $oSource->update();
        $this->successRedirectTo('viewsource', _kt("Configuration updated"), 'source_id=' . $oSource->getId());
    }
    // }}}

    // {{{ getAuthenticator
    function &getAuthenticator($oSource) {
        return new $this->sAuthenticatorClass($oSource);
    }
    // }}}

    // {{{ _do_editUserFromSource
    function _do_editUserFromSource() {
        $oTemplate = $this->oValidator->validateTemplate('ktstandard/authentication/ldapadduser');
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $id = KTUtil::arrayGet($_REQUEST, 'id');

        $aConfig = unserialize($oSource->getConfig());

        $oAuthenticator = $this->getAuthenticator($oSource);
        $aResults = $oAuthenticator->getUser($id);
        $aErrorOptions = array(
            'message' => _kt('Could not find user in LDAP server'),
        );
        $this->oValidator->notError($aResults);

        $fields = array();
        $fields[] =  new KTStaticTextWidget(_kt('LDAP DN'), _kt('The location of the user within the LDAP directory.'), 'dn', $id, $this->oPage);
        $fields[] =  new KTStringWidget(_kt('Username'), _kt('The username the user will enter to gain access to KnowledgeTree.  e.g. <strong>jsmith</strong>'), 'ldap_username', $aResults[$this->aAttributes[1]], $this->oPage, true);
        $fields[] =  new KTStringWidget(_kt('Name'), _kt('The full name of the user.  This is shown in reports and listings.  e.g. <strong>John Smith</strong>'), 'name', $aResults[$this->aAttributes[0]], $this->oPage, true);
        $fields[] =  new KTStringWidget(_kt('Email Address'), _kt('The email address of the user.  Notifications and alerts are mailed to this address if <strong>email notifications</strong> is set below. e.g. <strong>jsmith@acme.com</strong>'), 'email_address', $aResults[$this->aAttributes[4]], $this->oPage, false);
        $fields[] =  new KTCheckboxWidget(_kt('Email Notifications'), _kt('If this is specified then the user will have notifications sent to the email address entered above.  If it is not set, then the user will only see notifications on the <strong>Dashboard</strong>'), 'email_notifications', true, $this->oPage, false);
        $fields[] =  new KTStringWidget(_kt('Mobile Number'), _kt('The mobile phone number of the user.  e.g. <strong>999 9999 999</strong>'), 'mobile_number', $aResults[$this->aAttributes[5]], $this->oPage, false);
        $fields[] =  new KTStringWidget(_kt('Maximum Sessions'), _kt('As a safety precaution, it is useful to limit the number of times a given account can log in, before logging out.  This prevents a single account being used by many different people.'), 'max_sessions', '3', $this->oPage, true);

        $aTemplateData = array(
            'context' => &$this,
            'fields' => $fields,
            'source' => $oSource,
            'search_results' => $aSearchResults,
            'dn' => $id,
            'samaccountname' => $aResults['samaccountname'],
        );
        return $oTemplate->render($aTemplateData);
    }
    // }}}

    // {{{ _do_createUserFromSource
    function _do_createUserFromSource() {
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $dn = KTUtil::arrayGet($_REQUEST, 'dn');
        $samaccountname = KTUtil::arrayGet($_REQUEST, 'samaccountname');
        $name = KTUtil::arrayGet($_REQUEST, 'name');
        if (empty($name)) { $this->errorRedirectToMain(_kt('You must specify a name for the user.')); }
        $username = KTUtil::arrayGet($_REQUEST, 'ldap_username');
        if (empty($name)) { $this->errorRedirectToMain(_kt('You must specify a new username.')); }
        // FIXME check for non-clashing usernames.

        $email_address = KTUtil::arrayGet($_REQUEST, 'email_address');
        $email_notifications = KTUtil::arrayGet($_REQUEST, 'email_notifications', false);
        if ($email_notifications !== false) $email_notifications = true;
        $mobile_number = KTUtil::arrayGet($_REQUEST, 'mobile_number');
        $max_sessions = KTUtil::arrayGet($_REQUEST, 'max_sessions', '3');
        // FIXME check for numeric max_sessions... db-error else?

        $oUser =& User::createFromArray(array(
            "Username" => $username,
            "Name" => $name,
            "Email" => $email_address,
            "EmailNotification" => $email_notifications,
            "SmsNotification" => false,   // FIXME do we auto-act if the user has a mobile?
            "MaxSessions" => $max_sessions,
            "authenticationsourceid" => $oSource->getId(),
            "authenticationdetails" => $dn,
            "authenticationdetails2" => $samaccountname,
            "password" => "",
        ));

        if (PEAR::isError($oUser) || ($oUser == false)) {
            $this->errorRedirectToMain(_kt("failed to create user."));
            exit(0);
        }

        $this->successRedirectToMain(_kt('Created new user') . ': ' . $oUser->getUsername());
        exit(0);
    }
    // }}}

    // {{{ _do_massCreateUsers
    function _do_massCreateUsers() {
        $aIds = KTUtil::arrayGet($_REQUEST, 'id');
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $oAuthenticator = $this->getAuthenticator($oSource);
        $aNames = array();
        foreach ($aIds as $sId) {
            $aResults = $oAuthenticator->getUser($sId);
            $dn = $sId;
            $sUserName = $aResults[$this->aAttributes[1]];
            $sName = $aResults[$this->aAttributes[0]];
            $sEmailAddress = $aResults[$this->aAttributes[4]];
            $sMobileNumber = $aResults[$this->aAttributes[5]];

            $oUser = User::createFromArray(array(
                "Username" => $sUserName,
                "Name" => $sName,
                "Email" => $sEmailAddress,
                "EmailNotification" => true,
                "SmsNotification" => false,   // FIXME do we auto-act if the user has a mobile?
                "MaxSessions" => 3,
                "authenticationsourceid" => $oSource->getId(),
                "authenticationdetails" => $dn,
                "authenticationdetails2" => $sUserName,
                "password" => "",
            ));
            $aNames[] = $sName;
        }
        $this->successRedirectToMain(_kt("Added users") . ": " . join(', ', $aNames));
    }
    // }}}

    // {{{ do_addUserFromSource
    function do_addUserFromSource() {
        $submit = KTUtil::arrayGet($_REQUEST, 'submit');
        if (!is_array($submit)) {
            $submit = array();
        }
        if (KTUtil::arrayGet($submit, 'chosen')) {
            $id = KTUtil::arrayGet($_REQUEST, 'id');
            $massimport = KTUtil::arrayGet($_REQUEST, 'massimport');
            if (!empty($id)) {
                if ($massimport) {
                    return $this->_do_massCreateUsers();
                } else {
                    return $this->_do_editUserFromSource();
                }
            } else {
                $this->oPage->addError(_kt("No valid LDAP user chosen"));
            }
        }
        if (KTUtil::arrayGet($submit, 'create')) {
            return $this->_do_createUserFromSource();
        }
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $oTemplate = $this->oValidator->validateTemplate('ktstandard/authentication/ldapsearchuser');

        $fields = array();
        $fields[] = new KTStringWidget(_kt("User's name"), _kt("The user's name, or part thereof, to find the user that you wish to add"), 'ldap_name', '', $this->oPage, true);
        $fields[] = new KTCheckboxWidget(_kt("Mass import"), _kt("Allow for multiple users to be selected to be added (will not get to manually verify the details if selected)"), 'massimport', false, $this->oPage, true);

        $oAuthenticator = $this->getAuthenticator($oSource);
        $name = KTUtil::arrayGet($_REQUEST, 'ldap_name');
        if (!empty($name)) {
            $aSearchResults = $oAuthenticator->searchUsers($name, array('cn', 'dn', $sIdentifierField));
            if (PEAR::isError($aSearchResults)) {
                $this->oPage->addError($aSearchResults->getMessage());
                $aSearchResults = null;
            }

            if (is_array($aSearchResults)) {
                foreach (array_keys($aSearchResults) as $k) {
                    if (is_array($aSearchResults[$k]['cn'])) {
                        $aSearchResults[$k]['cn'] = $aSearchResults[$k]['cn'][0];
                    }
                }
            }
        }

        $massimport = KTUtil::arrayGet($_REQUEST, 'massimport');
        
        $aTemplateData = array(
            'context' => &$this,
            'fields' => $fields,
            'source' => $oSource,
            'search_results' => $aSearchResults,
            'identifier_field' => $sIdentifierField,
            'massimport' => $massimport,
        );
        return $oTemplate->render($aTemplateData);
    }
    // }}}

    // {{{ do_addGroupFromSource
    function do_addGroupFromSource() {
        $submit = KTUtil::arrayGet($_REQUEST, 'submit');
        if (!is_array($submit)) {
            $submit = array();
        }
        if (KTUtil::arrayGet($submit, 'chosen')) {
            $id = KTUtil::arrayGet($_REQUEST, 'id');
            if (!empty($id)) {
                return $this->_do_editGroupFromSource();
            } else {
                $this->oPage->addError(_kt("No valid LDAP group chosen"));
            }
        }
        if (KTUtil::arrayGet($submit, 'create')) {
            return $this->_do_createGroupFromSource();
        }
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $oTemplate = $this->oValidator->validateTemplate('ktstandard/authentication/ldapsearchgroup');

        $fields = array();
        $fields[] = new KTStringWidget(_kt("Group's name"), _kt("The group's name, or part thereof, to find the group that you wish to add"), 'name', '', $this->oPage, true);

        $oAuthenticator = $this->getAuthenticator($oSource);
        $name = KTUtil::arrayGet($_REQUEST, 'name');
        if (!empty($name)) {
            $oAuthenticator = $this->getAuthenticator($oSource);
            $aSearchResults = $oAuthenticator->searchGroups($name);
        }
        
        $aTemplateData = array(
            'context' => &$this,
            'fields' => $fields,
            'source' => $oSource,
            'search_results' => $aSearchResults,
            'identifier_field' => 'displayName',
        );
        return $oTemplate->render($aTemplateData);
    }
    // }}}

    // {{{ _do_editGroupFromSource
    function _do_editGroupFromSource() {
        $oTemplate = $this->oValidator->validateTemplate('ktstandard/authentication/ldapaddgroup');
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $id = KTUtil::arrayGet($_REQUEST, 'id');

        $aConfig = unserialize($oSource->getConfig());

        $oAuthenticator = $this->getAuthenticator($oSource);
        $aAttributes = $oAuthenticator->getGroup($id);
        
        $fields = array();
        $fields[] = new KTStaticTextWidget(_kt('LDAP DN'), _kt('The location of the group within the LDAP directory.'), 'dn', $aAttributes['dn'], $this->oPage);
        $fields[] = new KTStringWidget(_kt('Group Name'), _kt('The name the group will enter to gain access to KnowledgeTree.  e.g. <strong>accountants</strong>'), 'ldap_groupname', $aAttributes['cn'], $this->oPage, true);
        $fields[] = new KTCheckboxWidget(_kt('Unit Administrators'), _kt('Should all the members of this group be given <strong>unit</strong> administration privileges?'), 'is_unitadmin', false, $this->oPage, false);
        $fields[] = new KTCheckboxWidget(_kt('System Administrators'), _kt('Should all the members of this group be given <strong>system</strong> administration privileges?'), 'is_sysadmin', false, $this->oPage, false);

        $aTemplateData = array(
            'context' => &$this,
            'fields' => $fields,
            'source' => $oSource,
            'search_results' => $aSearchResults,
            'dn' => $aAttributes['dn'],
        );
        return $oTemplate->render($aTemplateData);
    }
    // }}}

    // {{{ _do_createGroupFromSource
    function _do_createGroupFromSource() {
        $oSource =& KTAuthenticationSource::get($_REQUEST['source_id']);
        $dn = KTUtil::arrayGet($_REQUEST, 'dn');
        $name = KTUtil::arrayGet($_REQUEST, 'ldap_groupname');
        if (empty($name)) { $this->errorRedirectToMain(_kt('You must specify a name for the group.')); }

        $is_unitadmin = KTUtil::arrayGet($_REQUEST, 'is_unitadmin', false);
        $is_sysadmin = KTUtil::arrayGet($_REQUEST, 'is_sysadmin', false);

        $oGroup =& Group::createFromArray(array(
            "name" => $name,
            "isunitadmin" => $is_unitadmin,
            "issysadmin" => $is_sysadmin,
            "authenticationdetails" => $dn,
            "authenticationsourceid" => $oSource->getId(),
        ));

        if (PEAR::isError($oGroup) || ($oGroup == false)) {
            $this->errorRedirectToMain(_kt("failed to create group."));
            exit(0);
        }

        $oAuthenticator = $this->getAuthenticator($oSource);
        $oAuthenticator->synchroniseGroup($oGroup);

        $this->successRedirectToMain(_kt('Created new group') . ': ' . $oGroup->getName());
        exit(0);
    }
    // }}}

    // {{{ autoSignup
    function autoSignup($sUsername, $sPassword, $aExtra, $oSource) {
        $oAuthenticator =& $this->getAuthenticator($oSource);
        $dn = $oAuthenticator->checkSignupPassword($sUsername, $sPassword);

        if (PEAR::isError($dn)) {
            return;
        }
        if (!is_string($dn)) {
            return;
        }

        if (empty($dn)) {
            return;
        }

        $aResults = $oAuthenticator->getUser($dn);
        $sUserName = $aResults[$this->aAttributes[1]];
        $sName = $aResults[$this->aAttributes[0]];
        $sEmailAddress = $aResults[$this->aAttributes[4]];
        $sMobileNumber = $aResults[$this->aAttributes[5]];

        $oUser = User::createFromArray(array(
            "Username" => $sUserName,
            "Name" => $sName,
            "Email" => $sEmailAddress,
            "EmailNotification" => true,
            "SmsNotification" => false,   // FIXME do we auto-act if the user has a mobile?
            "MaxSessions" => 3,
            "authenticationsourceid" => $oSource->getId(),
            "authenticationdetails" => $dn,
            "authenticationdetails2" => $sUserName,
            "password" => "",
        ));

        if (PEAR::isError($oUser)) {
            return;
        }

        if (!is_a($oUser, 'User')) {
            return;
        }

        $this->_createSignupGroups($dn, $oSource);

        return $oUser;
    }

    function _createSignupGroups($dn, $oSource) {
        $oAuthenticator =& $this->getAuthenticator($oSource);
        $aGroupDNs = $oAuthenticator->getGroups($dn);
        foreach ($aGroupDNs as $sGroupDN) {
            $oGroup = Group::getByAuthenticationSourceAndDetails($oSource, $sGroupDN);
            if (PEAR::isError($oGroup)) {
                $oGroup = $this->_createGroup($sGroupDN, $oSource);
                if (PEAR::isError($oGroup)) {
                    continue;
                }
            }
            $oAuthenticator->synchroniseGroup($oGroup);
        }
    }

    function _createGroup($dn, $oSource) {
        $oAuthenticator =& $this->getAuthenticator($oSource);
        $aGroupDetails = $oAuthenticator->getGroup($dn);
        $name = $aGroupDetails['cn'];
        $oGroup =& Group::createFromArray(array(
            "name" => $name,
            "isunitadmin" => false,
            "issysadmin" => false,
            "authenticationdetails" => $dn,
            "authenticationsourceid" => $oSource->getId(),
        ));
        return $oGroup;
    }
}

class KTLDAPBaseAuthenticator extends Authenticator {
    /**
     * The LDAP server to connect to
     */
    var $sLdapServer;
    var $iLdapPort;
    /**
     * The base LDAP DN to perform authentication against
     */
    var $sBaseDN;
    /**
     * The LDAP accessor class
     */
    var $oLdap;

    function KTLDAPBaseAuthenticator($oSource) {
        $this->oSource =& KTUtil::getObject('KTAuthenticationSource', $oSource);
        $aConfig = unserialize($this->oSource->getConfig());
        $this->sLdapServer = $aConfig['servername'];
        $this->iLdapPort = $aConfig['serverport'];
        $this->sBaseDN = $aConfig['basedn'];
        $this->sSearchUser = $aConfig['searchuser'];
        $this->sSearchPassword = $aConfig['searchpassword'];
        $this->aObjectClasses = KTUtil::arrayGet($aConfig, 'objectclasses');
        if (empty($this->aObjectClasses)) {
            $this->aObjectClasses = array('user', 'inetOrgPerson', 'posixAccount');
        }
        $this->aSearchAttributes = KTUtil::arrayGet($aConfig, 'searchattributes');
        if (empty($this->aSearchAttributes)) {
            $this->aSearchAttributes = array('cn', 'samaccountname');
        }
        $this->bTls = KTUtil::arrayGet($aConfig, 'tls', false);

        if ($this->iLdapPort + 0 == 0) $this->iLdapPort=389; // some basic validation in case port is blank or 0
    
        require_once('Net/LDAP.php');
        $config = array(
            'dn' => $this->sSearchUser,
            'password' => $this->sSearchPassword,
            'host' => $this->sLdapServer,
            'base' => $this->sBaseDN,
            'options' => array('LDAP_OPT_REFERRALS' => 0),
            'tls' => $this->bTls,
            'port'=> $this->iLdapPort
        );

        $this->oLdap =& Net_LDAP::connect($config);
        if (PEAR::isError($this->oLdap)) {
            return $oLdap;
        }
    }

    /**
     * Authenticate the user against the LDAP directory
     *
     * @param string the user to authenticate
     * @param string the password to check
     * @return boolean true if the password is correct, else false
     */
    function checkPassword($oUser, $sPassword) {
        $dn = $oUser->getAuthenticationDetails();
        $config = array(
            'host' => $this->sLdapServer,
            'base' => $this->sBaseDN,
            'tls' => $this->bTls,
            'port'=> $this->iLdapPort
        );
        $oLdap =& Net_LDAP::connect($config);
        if (PEAR::isError($oLdap)) {
            return $oLdap;
        }
        $res = $oLdap->reBind($dn, $sPassword);
        return $res;
    }

    function checkSignupPassword($sUsername, $sPassword) {
        $aUsers = $this->findUser($sUsername);
        if (empty($aUsers)) {
            return false;
        }
        if (count($aUsers) !== 1) {
            return false;
        }
        $dn = $aUsers[0]['dn'];
        $config = array(
            'host' => $this->sLdapServer,
            'base' => $this->sBaseDN,
            'tls' => $this->bTls,
            'port'=> $this->iLdapPort
        );
        $oLdap =& Net_LDAP::connect($config);
        if (PEAR::isError($oLdap)) {
            return $oLdap;
        }
        $res = $oLdap->reBind($dn, $sPassword);
        if ($res === true) {
            return $dn;
        }
        return $res;
    }

    function getGroups($dn) {
        if (PEAR::isError($this->oLdap)) {
            return $this->oLdap;
        }

        $oEntry = $this->oLdap->getEntry($dn, array('memberOf'));
        if (PEAR::isError($oEntry)) {
            return $oEntry;
        }
        $aAttr = $oEntry->attributes();
        return $aAttr['memberOf'];
    }


    /**
     * Searched the directory for a specific user
     *
     * @param string the username to search for
     * @param array the attributes to return from the search
     * @return array containing the users found
     */
    function getUser($dn) {
        if (PEAR::isError($this->oLdap)) {
            return $this->oLdap;
        }

        $oEntry = $this->oLdap->getEntry($dn, $this->aAttributes);
        if (PEAR::isError($oEntry)) {
            return $oEntry;
        }
        $aAttr = $oEntry->attributes();
        $aAttr['dn'] = $oEntry->dn();

        global $default;
        foreach ($aAttr as $k => $v) {
            $default->log->info(sprintf("LDAP: For DN %s, attribute %s value is %s", $dn, $k, print_r($v, true)));
            if (is_array($v)) {
                $v = array_shift($v);
            }
            $aRet[strtolower($k)] = $v;
        }
        return $aRet;
    }

    /**
     * Searches the LDAP directory for users matching the supplied search string.
     *
     * @param string the username to search for
     * @param array the attributes to return from the search
     * @return array containing the users found
     */
    function searchUsers($sSearch) {
        global $default;
        if (PEAR::isError($this->oLdap)) {
            return $this->oLdap;
        }

        $aParams = array(
            'scope' => 'sub',
            'attributes' => array('cn', 'dn', 'samaccountname'),
        );
        $rootDn = $this->sBaseDN;
        if (is_array($rootDn)) {
            $rootDn = join(",", $rootDn);
        }
        $sObjectClasses = "|";
        foreach ($this->aObjectClasses as $sObjectClass) {
            $sObjectClasses .= sprintf('(objectClass=%s)', trim($sObjectClass));
        }
        $sSearchAttributes = "|";
        foreach ($this->aSearchAttributes as $sSearchAttribute) {
            $sSearchAttributes .= sprintf('(%s=*%s*)', trim($sSearchAttribute), $sSearch);
        }
        $sFilter = sprintf('(&(%s)(%s))', $sObjectClasses, $sSearchAttributes);
        $default->log->debug("Search filter is: " . $sFilter);
        $oResult = $this->oLdap->search($rootDn, $sFilter, $aParams);
        if (PEAR::isError($oResult)) {
            return $oResult;
        }
        $aRet = array();
        foreach($oResult->entries() as $oEntry) {
            $aAttr = $oEntry->attributes();
            $aAttr['dn'] = $oEntry->dn();
            $aRet[] = $aAttr;
        }
        return $aRet;
    }

    function findUser($sUsername) {
        global $default;
        if (PEAR::isError($this->oLdap)) {
            return $this->oLdap;
        }

        $aParams = array(
            'scope' => 'sub',
            'attributes' => array('cn', 'dn', 'samaccountname'),
        );
        $rootDn = $this->sBaseDN;
        if (is_array($rootDn)) {
            $rootDn = join(",", $rootDn);
        }
        $sObjectClasses = "|";
        foreach ($this->aObjectClasses as $sObjectClass) {
            $sObjectClasses .= sprintf('(objectClass=%s)', trim($sObjectClass));
        }
        $sSearchAttributes = "|";
        foreach ($this->aSearchAttributes as $sSearchAttribute) {
            $sSearchAttributes .= sprintf('(%s=%s)', trim($sSearchAttribute), $sUsername);
        }
        $sFilter = sprintf('(&(%s)(%s))', $sObjectClasses, $sSearchAttributes);
        $default->log->debug("Search filter is: " . $sFilter);
        $oResult = $this->oLdap->search($rootDn, $sFilter, $aParams);
        if (PEAR::isError($oResult)) {
            return $oResult;
        }
        $aRet = array();
        foreach($oResult->entries() as $oEntry) {
            $aAttr = $oEntry->attributes();
            $aAttr['dn'] = $oEntry->dn();
            $aRet[] = $aAttr;
        }
        return $aRet;
    }

    function searchGroups($sSearch) {
        if (PEAR::isError($this->oLdap)) {
            return $this->oLdap;
        }

        $aParams = array(
            'scope' => 'sub',
            'attributes' => array('cn', 'dn', 'displayName'),
        );
        $rootDn = $oAuthenticator->sBaseDN;
        if (is_array($rootDn)) {
            $rootDn = join(",", $rootDn);
        }
        $sFilter = sprintf('(&(objectClass=group)(cn=*%s*))', $sSearch);
        $oResults = $this->oLdap->search($rootDn, $sFilter, $aParams);
        $aRet = array();
        foreach($oResults->entries() as $oEntry) {
            $aAttr = $oEntry->attributes();
            $aAttr['dn'] = $oEntry->dn();
            $aRet[] = $aAttr;
        }
        return $aRet;
    }

    function getGroup($dn, $aAttributes = null) {
        if (empty($aAttributes)) {
            $aAttributes = array('cn');
        }
        if (PEAR::isError($this->oLdap)) {
            return $this->oLdap;
        }

        $oEntry = $this->oLdap->getEntry($dn, $aAttributes);
        if (PEAR::isError($oEntry)) {
            return $oEntry;
        }
        $aAttr = $oEntry->attributes();
        $aAttr['dn'] = $oEntry->dn();
        return $aAttr;
    }

    function synchroniseGroup($oGroup) {
        $oGroup =& KTUtil::getObject('Group', $oGroup);
        $dn = $oGroup->getAuthenticationDetails();
        $aAttr = $this->getGroup($dn, array('member'));
        if (PEAR::isError($aAttr)) {
            return $aAttr;
        }
        $aMembers = KTUtil::arrayGet($aAttr, 'member', array());
        if (!is_array($aMembers)) {
            $aMembers = array($aMembers);
        }
        $aUserIds = array();
        foreach ($aMembers as $sMember) {
            $iUserId = User::getByAuthenticationSourceAndDetails($this->oSource, $sMember, array('ids' => true));
            if (PEAR::isError($iUserId)) {
                continue;
            }
            $aUserIds[] = $iUserId;
        }
        $oGroup->setMembers($aUserIds);
    }
}

