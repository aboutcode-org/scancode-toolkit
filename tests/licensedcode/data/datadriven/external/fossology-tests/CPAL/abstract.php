<?php

/**
 * EXHIBIT A. Common Public Attribution License Version 1.0
 * The contents of this file are subject to the Common Public Attribution License Version 1.0 (the “License”);
 * you may not use this file except in compliance with the License. You may obtain a copy of the License at
 * http://www.oxwall.org/license. The License is based on the Mozilla Public License Version 1.1
 * but Sections 14 and 15 have been added to cover use of software over a computer network and provide for
 * limited attribution for the Original Developer. In addition, Exhibit A has been modified to be consistent
 * with Exhibit B. Software distributed under the License is distributed on an “AS IS” basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the specific language
 * governing rights and limitations under the License. The Original Code is Oxwall software.
 * The Initial Developer of the Original Code is Oxwall Foundation (http://www.oxwall.org/foundation).
 * All portions of the code written by Oxwall Foundation are Copyright (c) 2011. All Rights Reserved.

 * EXHIBIT B. Attribution Information
 * Attribution Copyright Notice: Copyright 2011 Oxwall Foundation. All rights reserved.
 * Attribution Phrase (not exceeding 10 words): Powered by Oxwall community software
 * Attribution URL: http://www.oxwall.org/
 * Graphic Image as provided in the Covered Code.
 * Display of Attribution Information is required in Larger Works which are defined in the CPAL as a work
 * which combines Covered Code or portions thereof with code not governed by the terms of the CPAL.
 */

/**
 * Base controller class for all admin pages.
 * All admin controllers should be extended from this class.
 *
 * @author Sardar Madumarov <madumarov@gmail.com>
 * @package ow_system_plugins.admin.controllers
 * @since 1.0
 */
abstract class ADMIN_CTRL_Abstract extends OW_ActionController
{

    /**
     * Constructor.
     */
    public function __construct()
    {
        parent::__construct();

        if ( !OW::getUser()->isAdmin() )
        {
            throw new AuthenticateException();
        }

        if ( !OW::getRequest()->isAjax() )
        {
            $document = OW::getDocument();
            $document->setMasterPage(new ADMIN_CLASS_MasterPage());
            $this->setPageTitle(OW::getLanguage()->text('admin', 'page_default_title'));
        }

        BOL_PluginService::getInstance()->checkManualUpdates();
        $plugin = BOL_PluginService::getInstance()->findNextManualUpdatePlugin();

        $handlerParams = OW::getRequestHandler()->getHandlerAttributes();

        // TODO refactor shortcut below
        if ( !defined('OW_PLUGIN_XP') && $plugin !== null )
        {
            if ( ( $handlerParams['controller'] === 'ADMIN_CTRL_Plugins' && $handlerParams['action'] === 'manualUpdateRequest' ) )
            {
                //action
            }
            else
            {
                throw new RedirectException(OW::getRouter()->urlFor('ADMIN_CTRL_Plugins', 'manualUpdateRequest', array('key' => $plugin->getKey())));
            }
        }

        // TODO temp admin pge inform event
        function admin_check_if_admin_page()
        {
            return true;
        }
        OW::getEventManager()->bind('admin.check_if_admin_page', 'admin_check_if_admin_page');
    }

    public function setPageTitle( $title )
    {
        OW::getDocument()->setTitle($title);
    }
}
