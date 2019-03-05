// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var MAX_APPS_PER_ROW = [];
MAX_APPS_PER_ROW[LayoutMode.SMALL] = 4;
MAX_APPS_PER_ROW[LayoutMode.NORMAL] = 6;

function getAppsCallback(data) {
  logEvent('received apps');

  // In the case of prefchange-triggered updates, we don't receive this flag.
  // Just leave it set as it was before in that case.
  if ('showPromo' in data)
    apps.showPromo = data.showPromo;

  var appsSection = $('apps');
  var appsSectionContent = $('apps-content');
  var appsMiniview = appsSection.getElementsByClassName('miniview')[0];
  var appsPromo = $('apps-promo');
  var appsPromoLink = $('apps-promo-link');
  var appsPromoPing = APP_LAUNCH_URL.PING_WEBSTORE + '+' + apps.showPromo;
  var webStoreEntry, webStoreMiniEntry;

  // Hide menu options that are not supported on the OS or windowing system.

  // The "Launch as Window" menu option.
  $('apps-launch-type-window-menu-item').hidden = data.disableAppWindowLaunch;

  // The "Create App Shortcut" menu option.
  $('apps-create-shortcut-command-menu-item').hidden =
      $('apps-create-shortcut-command-separator').hidden =
          data.disableCreateAppShortcut;

  // Hide the context menu, if there is any open.
  cr.ui.contextMenuHandler.hideMenu();

  appsMiniview.textContent = '';
  appsSectionContent.textContent = '';

  data.apps.sort(function(a,b) {
    return a.app_launch_index - b.app_launch_index;
  });

  // Determines if the web store link should be detached and place in the
  // top right of the screen.
  apps.detachWebstoreEntry =
      !apps.showPromo && data.apps.length >= MAX_APPS_PER_ROW[layoutMode];

  markNewApps(data.apps);
  apps.data = data.apps;

  clearClosedMenu(apps.menu);

  // We wait for the app icons to load before displaying them, but never wait
  // longer than 200ms.
  apps.loadedImages = 0;
  apps.imageTimer = setTimeout(apps.showImages.bind(apps), 200);

  data.apps.forEach(function(app) {
    appsSectionContent.appendChild(apps.createElement(app));
  });

  if (data.showPromo) {
    // Add the promo content...
    $('apps-promo-heading').textContent = data.promoHeader;
    appsPromoLink.href = data.promoLink;
    appsPromoLink.textContent = data.promoButton;
    appsPromoLink.ping = appsPromoPing;
    $('apps-promo-hide').textContent = data.promoExpire;

    // ... then display the promo.
    document.documentElement.classList.add('apps-promo-visible');
  } else {
    document.documentElement.classList.remove('apps-promo-visible');
  }

  // Only show the web store entry if there are apps installed, since the promo
  // is sufficient otherwise.
  if (data.apps.length > 0) {
    webStoreEntry = apps.createWebStoreElement();
    webStoreEntry.querySelector('a').ping = appsPromoPing;
    appsSectionContent.appendChild(webStoreEntry);
    if (apps.detachWebstoreEntry) {
      webStoreEntry.classList.add('loner');
    } else {
      webStoreEntry.classList.remove('loner');
      apps.data.push('web-store-entry');
    }
  }

  data.apps.slice(0, MAX_MINIVIEW_ITEMS).forEach(function(app) {
    appsMiniview.appendChild(apps.createMiniviewElement(app));
    addClosedMenuEntryWithLink(apps.menu, apps.createClosedMenuElement(app));
  });
  if (data.apps.length < MAX_MINIVIEW_ITEMS) {
    webStoreMiniEntry = apps.createWebStoreMiniElement();
    webStoreMiniEntry.querySelector('a').ping = appsPromoPing;
    appsMiniview.appendChild(webStoreMiniEntry);
    addClosedMenuEntryWithLink(apps.menu,
                               apps.createWebStoreClosedMenuElement());
  }

  if (!data.showLauncher)
    hideSection(Section.APPS);
  else
    appsSection.classList.remove('disabled');

  addClosedMenuFooter(apps.menu, 'apps', MENU_APPS, Section.APPS);

  apps.loaded = true;

  if (appsPromoLink)
    appsPromoLink.ping = appsPromoPing;
  maybeDoneLoading();

  // Disable the animations when the app launcher is being (re)initailized.
  apps.layout({disableAnimations:true});

  if (isDoneLoading()) {
    updateMiniviewClipping(appsMiniview);
    layoutSections();
  }
}

function markNewApps(data) {
  var oldData = apps.data;
  data.forEach(function(app) {
    if (hashParams['app-id'] == app['id']) {
      delete hashParams['app-id'];
      app.isNew = true;
    } else if (oldData &&
        !oldData.some(function(id) { return id == app.id; })) {
      app.isNew = true;
    } else {
      app.isNew = false;
    }
  });
}

function appsPrefChangeCallback(data) {
  // Currently the only pref that is watched is the launch type.
  data.apps.forEach(function(app) {
    var appLink = document.querySelector('.app a[app-id=' + app['id'] + ']');
    if (appLink)
      appLink.setAttribute('launch-type', app['launch_type']);
  });
}

// Launches the specified app using the APP_LAUNCH_NTP_APP_RE_ENABLE histogram.
// This should only be invoked from the AppLauncherHandler.
function launchAppAfterEnable(appId) {
  chrome.send('launchApp', [appId, APP_LAUNCH.NTP_APP_RE_ENABLE]);
}

var apps = (function() {

  function createElement(app) {
    var div = document.createElement('div');
    div.className = 'app';

    var a = div.appendChild(document.createElement('a'));
    a.setAttribute('app-id', app['id']);
    a.setAttribute('launch-type', app['launch_type']);
    a.draggable = false;
    a.xtitle = a.textContent = app['name'];
    a.href = app['launch_url'];

    return div;
  }

  /**
   * Launches an application.
   * @param {string} appId Application to launch.
   * @param {MouseEvent} opt_mouseEvent Mouse event from the click that
   *     triggered the launch, used to detect modifier keys that change
   *     the tab's disposition.
   */
  function launchApp(appId, opt_mouseEvent) {
    var args = [appId, getAppLaunchType()];
    if (opt_mouseEvent) {
      // Launch came from a click - add details of the click
      // Otherwise it came from a 'command' event from elsewhere in the UI.
      args.push(opt_mouseEvent.altKey, opt_mouseEvent.ctrlKey,
                opt_mouseEvent.metaKey, opt_mouseEvent.shiftKey,
                opt_mouseEvent.button);
    }
    chrome.send('launchApp', args);
  }

  function isAppSectionMaximized() {
    return getAppLaunchType() == APP_LAUNCH.NTP_APPS_MAXIMIZED &&
      !$('apps').classList.contains('disabled');
  }

  function isAppsMenu(node) {
    return node.id == 'apps-menu';
  }

  function getAppLaunchType() {
    // We determine if the apps section is maximized, collapsed or in menu mode
    // based on the class of the apps section.
    if ($('apps').classList.contains('menu'))
      return APP_LAUNCH.NTP_APPS_MENU;
    else if ($('apps').classList.contains('collapsed'))
      return APP_LAUNCH.NTP_APPS_COLLAPSED;
    else
      return APP_LAUNCH.NTP_APPS_MAXIMIZED;
  }

  /**
   * @this {!HTMLAnchorElement}
   */
  function handleClick(e) {
    var appId = e.currentTarget.getAttribute('app-id');
    if (!appDragAndDrop.isDragging())
      launchApp(appId, e);
    return false;
  }

  // Keep in sync with LaunchType in extension_prefs.h
  var LaunchType = {
    LAUNCH_PINNED: 0,
    LAUNCH_REGULAR: 1,
    LAUNCH_FULLSCREEN: 2,
    LAUNCH_WINDOW: 3
  };

  // Keep in sync with LaunchContainer in extension_constants.h
  var LaunchContainer = {
    LAUNCH_WINDOW: 0,
    LAUNCH_PANEL: 1,
    LAUNCH_TAB: 2
  };

  var currentApp;
  var promoHasBeenSeen = false;

  function addContextMenu(el, app) {
    el.addEventListener('contextmenu', cr.ui.contextMenuHandler);
    el.addEventListener('keydown', cr.ui.contextMenuHandler);
    el.addEventListener('keyup', cr.ui.contextMenuHandler);

    Object.defineProperty(el, 'contextMenu', {
      get: function() {
        currentApp = app;

        $('apps-launch-command').label = app['name'];
        $('apps-options-command').canExecuteChange();

        var launchTypeEl;
        if (el.getAttribute('app-id') === app['id']) {
          launchTypeEl = el;
        } else {
          appLinkSel = 'a[app-id=' + app['id'] + ']';
          launchTypeEl = el.querySelector(appLinkSel);
        }

        var launchType = launchTypeEl.getAttribute('launch-type');
        var launchContainer = app['launch_container'];
        var isPanel = launchContainer == LaunchContainer.LAUNCH_PANEL;

        // Update the commands related to the launch type.
        var launchTypeIds = ['apps-launch-type-pinned',
                             'apps-launch-type-regular',
                             'apps-launch-type-fullscreen',
                             'apps-launch-type-window'];
        launchTypeIds.forEach(function(id) {
          var command = $(id);
          command.disabled = isPanel;
          command.checked = !isPanel &&
              launchType == command.getAttribute('launch-type');
        });

        return $('app-context-menu');
      }
    });
  }

  document.addEventListener('command', function(e) {
    if (!currentApp)
      return;

    var commandId = e.command.id;
    switch (commandId) {
      case 'apps-options-command':
        window.location = currentApp['options_url'];
        break;
      case 'apps-launch-command':
        launchApp(currentApp['id']);
        break;
      case 'apps-uninstall-command':
        chrome.send('uninstallApp', [currentApp['id']]);
        break;
      case 'apps-create-shortcut-command':
        chrome.send('createAppShortcut', [currentApp['id']]);
        break;
      case 'apps-launch-type-pinned':
      case 'apps-launch-type-regular':
      case 'apps-launch-type-fullscreen':
      case 'apps-launch-type-window':
        chrome.send('setLaunchType',
            [currentApp['id'],
             Number(e.command.getAttribute('launch-type'))]);
        break;
    }
  });

  document.addEventListener('canExecute', function(e) {
    switch (e.command.id) {
      case 'apps-options-command':
        e.canExecute = currentApp && currentApp['options_url'];
        break;
      case 'apps-launch-command':
        e.canExecute = true;
        break;
      case 'apps-uninstall-command':
        e.canExecute = !currentApp['can_uninstall'];
        break;
    }
  });

  // Moves the element at position |from| in array |arr| to position |to|.
  function arrayMove(arr, from, to) {
    var element = arr.splice(from, 1);
    arr.splice(to, 0, element[0]);
  }

  // The autoscroll rate during drag and drop, in px per second.
  var APP_AUTOSCROLL_RATE = 400;

  return {
    loaded: false,

    menu: $('apps-menu'),

    showPromo: false,

    detachWebstoreEntry: false,

    scrollMouseXY_: null,

    scrollListener_: null,

    // The list of app ids, in order, of each app in the launcher.
    data_: null,
    get data() { return this.data_; },
    set data(data) {
      this.data_ = data.map(function(app) {
        return app.id;
      });
      this.invalidate_();
    },

    dirty_: true,
    invalidate_: function() {
      this.dirty_ = true;
    },

    visible_: true,
    get visible() {
      return this.visible_;
    },
    set visible(visible) {
      this.visible_ = visible;
      this.invalidate_();
    },

    maybePingPromoSeen_: function() {
      if (promoHasBeenSeen || !this.showPromo || !isAppSectionMaximized())
        return;

      promoHasBeenSeen = true;
      chrome.send('promoSeen', []);
    },

    // DragAndDropDelegate

    dragContainer: $('apps-content'),
    transitionsDuration: 200,

    get dragItem() { return this.dragItem_; },
    set dragItem(dragItem) {
      if (this.dragItem_ != dragItem) {
        this.dragItem_ = dragItem;
        this.invalidate_();
      }
    },

    // The dimensions of each item in the app launcher.
    dimensions_: null,
    get dimensions() {
      if (this.dimensions_)
        return this.dimensions_;

      var width = 124;
      var height = 136;

      var marginWidth = 6;
      var marginHeight = 10;

      var borderWidth = 0;
      var borderHeight = 0;

      this.dimensions_ = {
        width: width + marginWidth + borderWidth,
        height: height + marginHeight + borderHeight
      };

      return this.dimensions_;
    },

    // Gets the item under the mouse event |e|. Returns null if there is no
    // item or if the item is not draggable.
    getItem: function(e) {
      var item = findAncestorByClass(e.target, 'app');

      // You can't drag the web store launcher.
      if (item && item.classList.contains('web-store-entry'))
        return null;

      return item;
    },

    // Returns true if |coordinates| point to a valid drop location. The
    // coordinates are relative to the drag container and the object should
    // have the 'x' and 'y' properties set.
    canDropOn: function(coordinates) {
      var cols = MAX_APPS_PER_ROW[layoutMode];
      var rows = Math.ceil(this.data.length / cols);

      var bottom = rows * this.dimensions.height;
      var right = cols * this.dimensions.width;

      if (coordinates.x >= right || coordinates.x < 0 ||
          coordinates.y >= bottom || coordinates.y < 0)
        return false;

      var position = this.getIndexAt_(coordinates);
      var appCount = this.data.length;

      if (!this.detachWebstoreEntry)
        appCount--;

      return position >= 0 && position < appCount;
    },

    setDragPlaceholder: function(coordinates) {
      var position = this.getIndexAt_(coordinates);
      var appId = this.dragItem.querySelector('a').getAttribute('app-id');
      var current = this.data.indexOf(appId);

      if (current == position || current < 0)
        return;

      arrayMove(this.data, current, position);
      this.invalidate_();
      this.layout();
    },

    getIndexAt_: function(coordinates) {
      var w = this.dimensions.width;
      var h = this.dimensions.height;

      var appsPerRow = MAX_APPS_PER_ROW[layoutMode];

      var row = Math.floor(coordinates.y / h);
      var col = Math.floor(coordinates.x / w);
      var index = appsPerRow * row + col;

      var appCount = this.data.length;
      var rows = Math.ceil(appCount / appsPerRow);

      // Rather than making the free space on the last row invalid, we
      // map it to the last valid position.
      if (index >= appCount && index < appsPerRow * rows)
        return appCount-1;

      return index;
    },

    scrollPage: function(xy) {
      var rect = this.dragContainer.getBoundingClientRect();

      // Here, we calculate the visible boundaries of the app launcher, which
      // are then used to determine when we should auto-scroll.
      var top = $('apps').getBoundingClientRect().bottom;
      var bottomFudge = 15; // Fudge factor due to a gradient mask.
      var bottom = top + maxiviewVisibleHeight - bottomFudge;
      var left = rect.left + window.scrollX;
      var right = Math.min(window.innerWidth, rect.left + rect.width);

      var dy = Math.min(0, xy.y - top) + Math.max(0, xy.y - bottom);
      var dx = Math.min(0, xy.x - left) + Math.max(0, xy.x - right);

      if (dx == 0 && dy == 0) {
        this.stopScroll_();
        return;
      }

      // If we scroll the page directly from this method, it may be choppy and
      // inconsistent. Instead, we loop using animation frames, and scroll at a
      // speed that's independent of how many times this method is called.
      this.scrollMouseXY_ = {dx: dx, dy: dy};

      if (!this.scrollListener_) {
        this.scrollListener_ = this.scrollImpl_.bind(this);
        this.scrollStep_();
      }
    },

    scrollStep_: function() {
      this.scrollStart_ = Date.now();
      window.webkitRequestAnimationFrame(this.scrollListener_);
    },

    scrollImpl_: function(time) {
      if (!appDragAndDrop.isDragging()) {
        this.stopScroll_();
        return;
      }

      if (!this.scrollMouseXY_)
        return;

      var step = time - this.scrollStart_;

      window.scrollBy(
          this.calcScroll_(this.scrollMouseXY_.dx, step),
          this.calcScroll_(this.scrollMouseXY_.dy, step));

      this.scrollStep_();
    },

    calcScroll_: function(delta, step) {
      if (delta == 0)
        return 0;

      // Increase the multiplier for every 50px the mouse is beyond the edge.
      var sign = delta > 0 ? 1 : -1;
      var scalar = APP_AUTOSCROLL_RATE * step / 1000;
      var multiplier = Math.floor(Math.abs(delta) / 50) + 1;

      return sign * scalar * multiplier;
    },

    stopScroll_: function() {
      this.scrollListener_ = null;
      this.scrollMouseXY_ = null;
    },

    saveDrag: function(draggedItem) {
      this.invalidate_();
      this.layout();

      var draggedAppId = draggedItem.querySelector('a').getAttribute('app-id');
      var appIds = this.data.filter(function(id) {
        return id != 'web-store-entry';
      });

      // Wait until the transitions are complete before notifying the browser.
      // Otherwise, the apps will be re-rendered while still transitioning.
      setTimeout(function() {
        chrome.send('reorderApps', [draggedAppId, appIds]);
      }, this.transitionsDuration + 10);
    },

    layout: function(options) {
      options = options || {};
      if (!this.dirty_ && options.force != true)
        return;

      try {
        var container = this.dragContainer;
        if (options.disableAnimations)
          container.setAttribute('launcher-animations', false);
        var d0 = Date.now();
        this.layoutImpl_();
        this.dirty_ = false;
        logEvent('apps.layout: ' + (Date.now() - d0));

      } finally {
        if (options.disableAnimations) {
          // We need to re-enable animations asynchronously, so that the
          // animations are still disabled for this layout update.
          setTimeout(function() {
            container.setAttribute('launcher-animations', true);
          }, 0);
        }
      }
    },

    layoutImpl_: function() {
      var apps = this.data || [];
      var rects = this.getLayoutRects_(apps.length);
      var appsContent = this.dragContainer;

      // Ping the PROMO_SEEN histogram only when the promo is maximized, and
      // maximum once per NTP load.
      this.maybePingPromoSeen_();

      if (!this.visible)
        return;

      for (var i = 0; i < apps.length; i++) {
        var app = appsContent.querySelector('[app-id='+apps[i]+']').parentNode;

        // If the node is being dragged, don't try to place it in the grid.
        if (app == this.dragItem)
          continue;

        app.style.left = rects[i].left + 'px';
        app.style.top = rects[i].top + 'px';
      }

      // We need to set the container's height manually because the apps use
      // absolute positioning.
      var rows = Math.ceil(apps.length / MAX_APPS_PER_ROW[layoutMode]);
      appsContent.style.height = (rows * this.dimensions.height) + 'px';
    },

    getLayoutRects_: function(appCount) {
      var availableWidth = this.dragContainer.offsetWidth;
      var rtl = isRtl();
      var rects = [];
      var w = this.dimensions.width;
      var h = this.dimensions.height;
      var appsPerRow = MAX_APPS_PER_ROW[layoutMode];

      for (var i = 0; i < appCount; i++) {
        var top = Math.floor(i / appsPerRow) * h;
        var left = (i % appsPerRow) * w;

        // Reflect the X axis if an RTL language is active.
        if (rtl)
          left = availableWidth - left - w;
        rects[i] = {left: left, top: top};
      }
      return rects;
    },

    get loadedImages() {
      return this.loadedImages_;
    },

    set loadedImages(value) {
      this.loadedImages_ = value;
      if (this.loadedImages_ == 0)
        return;

      // Each application icon is loaded asynchronously. Here, we display
      // the icons once they've all been loaded to make it look nicer.
      if (this.loadedImages_ == this.data.length) {
        this.showImages();
        return;
      }

      // We won't actually have the visible height until the sections have
      // been layed out.
      if (!maxiviewVisibleHeight)
        return;

      // If we know the visible height of the maxiview, then we can don't need
      // to wait for all the icons. Instead, we wait until the visible portion
      // have been loaded.
      var appsPerRow = MAX_APPS_PER_ROW[layoutMode];
      var rows = Math.ceil(maxiviewVisibleHeight / this.dimensions.height);
      var count = Math.min(appsPerRow * rows, this.data.length);
      if (this.loadedImages_ == count) {
        this.showImages();
        return;
      }
    },

    showImages: function() {
      $('apps-content').classList.add('visible');
      clearTimeout(this.imageTimer);
    },

    createElement: function(app) {
      var div = createElement(app);
      var a = div.firstChild;

      a.onclick = handleClick;
      a.ping = getAppPingUrl(
          'PING_BY_ID', this.showPromo, 'NTP_APPS_MAXIMIZED');
      a.style.backgroundImage = url(app['icon_big']);
      if (app.isNew) {
        div.setAttribute('new', 'new');
        // Delay changing the attribute a bit to let the page settle down a bit.
        setTimeout(function() {
          // Make sure the new icon is scrolled into view.
          document.body.scrollTop = document.body.scrollHeight;

          // This will trigger the 'bounce' animation defined in apps.css.
          div.setAttribute('new', 'installed');
        }, 500);
        div.addEventListener('webkitAnimationEnd', function(e) {
          div.removeAttribute('new');
        });
      }

      // CSS background images don't fire 'load' events, so we use an Image.
      var img = new Image();
      img.onload = function() { this.loadedImages++; }.bind(this);
      img.src = app['icon_big'];

      var settingsButton = div.appendChild(new cr.ui.ContextMenuButton);
      settingsButton.className = 'app-settings';
      settingsButton.title = localStrings.getString('appsettings');

      addContextMenu(div, app);

      return div;
    },

    createMiniviewElement: function(app) {
      var span = document.createElement('span');
      var a = span.appendChild(document.createElement('a'));

      a.setAttribute('app-id', app['id']);
      a.textContent = app['name'];
      a.href = app['launch_url'];
      a.onclick = handleClick;
      a.ping = getAppPingUrl(
          'PING_BY_ID', this.showPromo, 'NTP_APPS_COLLAPSED');
      a.style.backgroundImage = url(app['icon_small']);
      a.className = 'item';
      span.appendChild(a);

      addContextMenu(span, app);

      return span;
    },

    createClosedMenuElement: function(app) {
      var a = document.createElement('a');
      a.setAttribute('app-id', app['id']);
      a.textContent = app['name'];
      a.href = app['launch_url'];
      a.onclick = handleClick;
      a.ping = getAppPingUrl(
          'PING_BY_ID', this.showPromo, 'NTP_APPS_MENU');
      a.style.backgroundImage = url(app['icon_small']);
      a.className = 'item';

      addContextMenu(a, app);

      return a;
    },

    createWebStoreElement: function() {
      var elm = createElement({
        'id': 'web-store-entry',
        'name': localStrings.getString('web_store_title'),
        'launch_url': localStrings.getString('web_store_url')
      });
      elm.classList.add('web-store-entry');
      return elm;
    },

    createWebStoreMiniElement: function() {
      var span = document.createElement('span');
      span.appendChild(this.createWebStoreClosedMenuElement());
      return span;
    },

    createWebStoreClosedMenuElement: function() {
      var a = document.createElement('a');
      a.textContent = localStrings.getString('web_store_title');
      a.href = localStrings.getString('web_store_url');
      a.style.backgroundImage = url('chrome://theme/IDR_PRODUCT_LOGO_16');
      a.className = 'item';
      return a;
    }
  };
})();

// Enable drag and drop reordering of the app launcher.
var appDragAndDrop = new DragAndDropController(apps);
