Intel(R) PRO/Wireless 3945ABG Network Connection driver for Linux* in 
support of:

Intel(R) PRO/Wireless 3945ABG Network Connection Adapter
Intel(R) PRO/Wireless 3945BG Network Connection Adapter

Note: The Intel(R) PRO/Wireless 3945ABG Network Connection driver for 
Linux is a unified driver that works on both hardware adapters listed 
above. In this document the Intel(R) PRO/Wireless 3945ABG Network Connection 
driver for Linux will be used to reference the unified driver.

Copyright (C) 2005 - 2006, Intel Corporation

README.ipw3945

Version: 1.1.3
Date   : December 08, 2006


Index
-----------------------------------------------
0.   IMPORTANT INFORMATION BEFORE USING THIS DRIVER
1.   Introduction
1.1. Overview of Features
2.   Loading the Driver
3.   Feature Details
3.1. LEDs
3.2. Association Details
3.3. Roaming Details
3.4. Scanning Details
3.5. Antenna Selection and "Diversity"
3.6. IEEE 802.11h Details 
3.7. Tx Power 
3.8. Security Details
3.9. Power Management
4.   Configuring the driver
4.1. Command Line Parameters
4.3. Sysfs Helper Files:
5.   Wireless Tools Details
5.1. iwlist
5.2. iwpriv
5.3. iwconfig
6.   Support
7.   License


===============================================
0.   IMPORTANT INFORMATION BEFORE USING THIS DRIVER
===============================================

Important Notice FOR ALL USERS OR DISTRIBUTORS!!!! 

Intel wireless LAN adapters are engineered, manufactured, tested, and
quality checked to ensure that they meet all necessary local and
governmental regulatory agency requirements for the regions that they
are designated and/or marked to ship into. Since wireless LANs are
generally unlicensed devices that share spectrum with radars,
          satellites, and other licensed and unlicensed devices, it is sometimes
          necessary to dynamically detect, avoid, and limit usage to avoid
          interference with these devices. In many instances Intel is required to
          provide test data to prove regional and local compliance to regional and
          governmental regulations before certification or approval to use the
          product is granted. Intel's wireless LAN's EEPROM, firmware, and
          software driver are designed to carefully control parameters that affect
          radio operation and to ensure electromagnetic compliance (EMC). These
          parameters include, without limitation, RF power, spectrum usage,
          channel scanning, and human exposure. 

          For these reasons Intel cannot permit any manipulation by third parties
          of the software provided in binary format with the wireless WLAN
          adapters (e.g., the EEPROM and firmware). Furthermore, if you use any
          patches, utilities, or code with the Intel wireless LAN adapters that
          have been manipulated by an unauthorized party (i.e., patches,
              utilities, or code (including open source code modifications) which have
              not been validated by Intel), (i) you will be solely responsible for
          ensuring the regulatory compliance of the products, (ii) Intel will bear
          no liability, under any theory of liability for any issues associated
          with the modified products, including without limitation, claims under
          the warranty and/or issues arising from regulatory non-compliance, and
          (iii) Intel will not provide or be required to assist in providing
          support to any third parties for such modified products.  

          Note: Many regulatory agencies consider Wireless LAN adapters to be
          modules, and accordingly, condition system-level regulatory approval
          upon receipt and review of test data documenting that the antennas and
          system configuration do not cause the EMC and radio operation to be
          non-compliant.

          The drivers available for download from SourceForge are provided as a 
          part of a development project.  Conformance to local regulatory 
          requirements is the responsibility of the individual developer.  As 
          such, if you are interested in deploying or shipping a driver as part of 
          solution intended to be used for purposes other than development, please 
          obtain a tested driver from Intel Customer Support at:

          http://support.intel.com/support/notebook/sb/CS-006408.htm


          ===============================================
          1.   Introduction
          ===============================================
          The following sections attempt to provide a brief introduction to using 
          the Intel(R) PRO/Wireless 3945ABG driver for Linux.

          This document is not meant to be a comprehensive manual on 
          understanding or using wireless technologies, but should be sufficient 
          to get you moving without wires on Linux.

          For information on building and installing the driver, see the INSTALL
          file.


          1.1. Overview of Features
          -----------------------------------------------
          The current release (1.1.3) supports the following features:

  + BSS mode (Infrastructure, Managed)
  + IBSS mode (Ad-Hoc)
+ WEP (OPEN and SHARED KEY mode)
  + 802.1x EAP via wpa_supplicant and xsupplicant
+ 802.11i (WPA/WPA2)
  + Wireless Extension support 
  + Full B and G rate support
+ Full A rate support (ABG only)
  + Transmit power control
+ S state support (ACPI suspend/resume)

  The following features are currently enabled, but not officially
  supported:

  + QoS
+ Monitor mode (aka RFMon)
  + Associated RF promiscuous mode
  + Frame Rx simulation

  The distinction between officially supported and enabled is a reflection 
  of the amount of validation and interoperability testing that has been
  performed on a given feature. Note: in addition, the features may not have 
  all of the code in the driver to fully enable the feature.


  ===============================================
  2. Loading the Driver
  ===============================================

  See the INSTALL document for information on installing the driver.

  Once installed, a typical method for launching the driver and the 
  regulatory daemon is via the load script provided in the source package:

# ./load debug=0x43fff   <--- You need to be root for this

  NOTE:  You will not be able to rmmod the driver so long as the 
  ipw3945d daemon is running.  

  If you followed the steps of the INSTALL document to set up your
  modprobe.conf, you can load the module by simply running:

# modprobe ipw3945       <--- You need to be root for this

  If you did not configure your modprobe.conf to automatically launch the 
  regulatory daemon (see INSTALL), you must do so manually after loading 
  the module:

# /sbin/ipw3945d  <--- You need to be root for this*

  * See README.ipw3945d (provided in the regulatory daemon package) for 
  information on how to configure the system to run the regulatory 
  daemon as a non-root user.

  If you want to unload the module (and kill the deamon as well), you can 
  simply use the unload script:

# ./unload               <--- You need to be root for this

  or likewise if you configured modprobe.conf:

# modprobe -r ipw3945       <--- You need to be root for this

  If you did not configure modprobe.conf to unload the regulatory daemon 
  and are not using the unload script, you need to kill the regulatory 
  daemon before you will be able to unload the module:

# /sbin/ipw3945d --kill <--- You need to be root for this
# modprobe -r ipw3945


  ===============================================
  3. Feature Details
  ===============================================

  3.1. LEDs
  -----------------------------------------------

  The driver will attempt to control the wireless LED, if one is 
  configured in hardware.  There are typically two LEDs:

  Activity -- used to indicate wireless activity
  Link     -- used to indicate wireless link

  The LED blink states can be interpreted as:

  Link

  Off                      -- Radio OFF
  Long off, long on        -- Unassociated
  Short off, short on      -- Scanning
  Solid on                 -- Associated
  Intermittent off         -- Attempting to roam

  Activity

  Off                      -- No network activity
  Blinking                 -- Speed of blink correlates to speed of 
  Tx/Rx

  NOTE:  In configurations where there is only one LED, the states may be 
  overlaid -- for example, while no data is being transferred while 
  associated, the LED may be solid.  When data is being transferred it may 
  blink according to the data transfer speed.


  3.2. Association Details
  -----------------------------------------------

  The driver is configured to only attempt association once you have 
  specified the ESSID for the network to associate with.  You can 
  override this behavior by providing the associate=1 module parameter.

  See the section 'Command Line Parameters' for more information.


  3.3. Roaming Details
  -----------------------------------------------

  Roaming criteria is based on missed beacons.  Once a given number of 
  beacons have been missed, the STA will look for an alternate AP on the 
  same network (ESSID and CHANNEL).  If one with a stronger signal is 
  found, it will attempt a re-association with the new AP.


  3.4. Scanning Details
  -----------------------------------------------

  Active / Passive scanning is controlled by the regulatory daemon.  
  The driver can request to invoke active scanning on any channel, 
  but only those channels currently allowing active scanning will 
  be allowed to actually send probe requests.


  3.5. Antenna Selection and "Diversity"
  -----------------------------------------------

  If you use only one antenna, you should manually select it via the
  "antenna" load parameter, or via /sys/bus/pci/drivers/ipw3945/00*/antenna.

  Modes are:
0:  Diversity ... NIC selects best antenna by itself (this is the default)
  1:  Main antenna only
  2:  Aux antenna only


  3.6. IEEE 802.11h Details 
  -----------------------------------------------

  Only BASIC reporting is supported; CCA and RPI are optional and not 
  implemented.  The driver currently does not respond with the appropriate 
  refusal frame if it receives a request that it will not provide a 
  report for.  

  Received TPC Request's will result in a TPC report being transmitted.  

  Channel Switch is currently supported; a received channel switch will 
  result in the channel switching.

  The STA will not perform measurements requested by other STAs.

  IBSS is not supported on channels marked passive-only. 

  The use of IBSS networks (starting or joining) on channels marked as 
  radar spectrum is also not supported.

  The user can manually control the transmit power control via the 
  iwconfig txpower command (see below for details on behavior of the
      txpower command with this driver).


  3.7. Tx Power 
  -----------------------------------------------

  Through the use of the wireless tools, you can set an upper limit on 
  the maximum transmit power to use.  When unassociated, the driver
  defaults to reporting the Tx power of the maximum transmit power supported 
  by any of the channels.  For example, if one channel supports 16dBm and the
  rest support only 14dBm, upon loading the driver the reported Tx power
  level will be set to 'auto' with a level of '16dBm'.  Attempts to
  set the Tx power above 16dBm will be clamped by the driver.

  When tuning to a channel, if no user limit has been configured, the driver
  will set the transmit power to the maximum supported by that channel.  
  The wireless tools will report 'auto' with that level.

  If you configure a maximum value, the wireless tools will report 'fixed'
  and the value you specified if unassociated.  If you are associated, the
  driver will use and report the lesser of either the limit provided or the
  limit configured for that channel in the hardware.

  After setting the transmit power level limit via Tx power both scan probe 
  requests and data packets will be clamped to this level.  If you attempt
  to provide a value outside of the supported range (-12dBm to the maximum 
      supported by your SKU, typically in the range of 14dBm to 17dBm) that
  value will be automatically clamped.

  Scan probe requests have a lower bound of 0dBm.  If you set a value 
  below 0dBm, that value will be used for other packets, but scan requests 
  will be set to 0dBm.


  3.8. Security Details
  -----------------------------------------------

  The driver currently supports WEP (64 and 128) as well as 802.1x, WPA, 
  and WPA2 with the use of wpa_supplicant.  If you are using a newer 
  kernel with Wireless Extensions > 18, then you should use a newer 
  version of wpa_supplicant and the -Dext driver.  If you are using an 
  older kernel, you should use wpa_supplicant and the -Dipw driver.

  Users have reported problems using older (0.3.x) versions of 
  wpa_supplicant with various authentication modes (WPA PSK, etc.).  
  If you experience problems using wpa_supplicant, please upgrade to the 
  latest version of the supplicant (0.4.6 or newer).


  3.9. Power Management
  -----------------------------------------------
  The Intel PRO/Wireless 3945ABG Network Connection driver for Linux 
  supports the configuration of the Power Save Protocol through a private 
  wireless extension interface. The driver supports the following 
  different modes:

  0       AC - Always ON
  1-5 Different levels of power management.  The higher the 
  Number, the greater the power savings, but with an impact to 
  packet latencies. 
  6 AC - Always ON
  7 BATTERY - Default setting for battery mode
  >7      AC - Always ON

  Power management works by powering down the radio after a certain 
  interval of time has passed where no packets are passed through the 
  radio.  Once powered down, the radio remains in that state for a given 
  period of time.  For higher power savings, the interval between last 
  packet processed to sleep is shorter and the sleep period is longer.

  When the radio is asleep, the access point sending data to the station 
  must buffer packets at the AP until the station wakes up and requests 
  any buffered packets.  If you have an AP that does not correctly support 
  the PSP protocol you may experience packet loss or very poor performance 
  while power management is enabled.  If this is the case, you will need 
  to try to find a firmware update for your AP, or disable power 
management (via `iwconfig eth1 power off`)

  To configure the power level on the Intel PRO/Wireless 3945ABG Network
  Connection driver for Linux, you must use the iwpriv set_power command:

  Setting the power management on and off via 'iwconfig power' is not
  currently supported by the driver.

  iwpriv set_power 1-5  Set the power level as specified.
  iwpriv set_power 7    Set power level to default BATTERY level.

  Setting the power level to any other value (0, 6, >7) will result in setting
  the device into AC mode with Power Management disabled.  

  If you explicitly set AC mode, the radio will always be on, however because
  you have set a specific mode, it will still show as 'Power Management: on'
  via wireless tools.

  You can view the current power level setting via:

  iwpriv get_power

  It will return the current period or timeout that is configured as a string
  in the form of xxxx/yyyy (z) where xxxx is the timeout interval (amount of
      time after packet processing), yyyy is the period to sleep (amount of time 
        to wait before powering the radio and querying the access point for buffered
        packets), and z is the 'power level'.

      If the adapter was configured to a mode outside the range 1-7, the value
      6 (AC) will be displayed followed by the text OFF to indicate a value 
      outside of the Power Management range was specified.

      If the adapter is configured to any mode 1-7 then the wireless tool will
      report 'Power Management: on'.  If the mode is set to 0 or > 7, the
      wireless tools will report 'Power Management: off'.


      ===============================================
      4. Configuring the driver
      ===============================================

      4.1. Command Line Parameters
      -----------------------------------------------

      Like many modules used in the Linux kernel, the Intel(R) PRO/Wireless
      3945ABG driver for Linux allows configuration options to be provided 
      as module parameters.  The most common way to specify a module parameter 
      is via the command line.  

      The general form is:

      % modprobe ipw3945 parameter=value

      antenna
      Select antenna to use.  If both antennas are used, antenna
      selection is handled by the driver and microcode.

      1 = Main, 2 = Aux.  Default is 0 [both]

      associate
      Set to 0 to disable the auto scan-and-associate functionality of the
      driver.  If disabled, the driver will not attempt to scan 
      for and associate to a network until it has been configured with 
      one or more properties for the target network, for example 
      configuring the network SSID.

      0 = only scan and associate once configured, 
      1 = auto scan and associate.
      Default 0 [do nothing until configured]

      auto_create
      Set to 0 to disable the auto creation of an ad-hoc network 
      matching the channel and network name parameters provided.  

      0 = do not attempt to create ad-hoc network
      1 = automatically create ad-hoc network once configured

      Default is 1 [auto create].

      channel
      channel number for association.  The normal method for setting
      the channel would be to use the standard wireless tools
      (i.e. `iwconfig eth1 channel 10`), but it is useful sometimes
      to set this while debugging.  Channel 0 means 'ANY'

      For information on which channels are available, see the 'channels'
      sysfs entry (documented below).

      Default is 0 [ANY].

      debug
      If using a debug build, this is used to control the amount of debug
      info is logged.  See the 'dvals' and 'load' script for more info on
      how to use this. 

      The dvals and load scripts are provided in the ipw3945-1.1.3.tgz
      development snapshot releases available from the SourceForge 
      project at http://ipw3945.sf.net)

      NOTE:  This entry is only available if CONFIG_IPW3945_DEBUG is
      enabled.

      disable
      Manually disable the radio (software RF kill).  This parameter
      allows you to configure the syfs rf_kill setting to turn on 
      software based RF kill.  You must clear out the sysfs entry in
      order to turn the radio on if this parameter is provided.

      For additional details on the rf_kill sysfs entry see the section
      on sysfs below.

      0 = Radio ON, 1 = Radio OFF.  Default is 0 [Radio ON]

      led
      Can be used to turn on LED code.

      0 = Off, 1 = On.  Default is 1 [LED On].

      mode
      Can be used to set the default mode of the adapter.

      0 = Managed, 1 = Ad-Hoc, 2 = Monitor.  Default is 0 [Managed]

      NOTE:  Monitor is only available if CONFIG_IPW3945_MONITOR is
      enabled.

      If CONFIG_IPW3945_QOS is enabled:

      qos_enable

      Enable all Qos functionality.

      0 = disable, 1 = enable.  Default is 0 [disabled]

      qos_burst_enable

      Enable QoS burst mode.

      0 = disable, 1 = enable.  Default is 0 [disabled]

      qos_no_ack_mask

      Mask transmit queue to not ACK.  Currently not used.

      qos_burst_CCK

      Duration of burst for CCK (802.11B) frames.

      Default = 0

      qos_burst_OFDM

      Duration of burst for OFDM (802.11A/G) frames.

      Default = 0.

      If CONFIG_IPW3945_PROMISCUOUS is enabled:

      rtap_iface
      Set to 1 to create a promiscuous radiotap interface.  This 
      interface will be set to type ARPHRD_IEEE80211_RADIOTAP and will 
      be passed every frame received over the air by the adapter.

      Default = 0.


      4.3. Sysfs Helper Files:
      -----------------------------------------------

  The Linux kernel provides a pseudo file system that can be used to 
access various components of the operating system.  The Intel(R)
  PRO/Wireless 3945ABG Network Connection driver for Linux exposes 
  several configuration parameters through this mechanism.

  An entry in the sysfs can support reading and/or writing.  You can 
  typically query the contents of a sysfs entry through the use of cat, 
  and can set the contents via echo.  For example:

  % cat /sys/bus/pci/drivers/ipw3945/debug_level

  Will report the current debug level of the driver's logging subsystem 
  (only available if CONFIG_IPW_DEBUG was configured when the driver was 
   built).

  You can set the debug level via:

  % echo $VALUE > /sys/bus/pci/drivers/ipw3945/debug_level

  Where $VALUE would be a number in the case of this sysfs entry.  The 
  input to sysfs files does not have to be a number.  For example, the 
  firmware loader used by hotplug utilizes sysfs entries for transfering 
  the firmware image from user space into the driver.

  The Intel(R) PRO/Wireless 3945ABG Network Connection driver for Linux 
  exposes sysfs entries at two levels -- driver level, which apply to all 
  instances of the driver (in the event that there is more than one device 
      installed) and device level, which applies only to the single specific 
  instance.


  4.3.1 Driver Level Sysfs Helper Files

  For the driver level files, look in /sys/bus/pci/drivers/ipw3945/

  If CONFIG_IPW3945_DEBUG is enabled:

  debug_level  

  This controls the same global as the 'debug' module parameter



  4.3.2 Device Level Sysfs Helper Files

  For the device level files, look in

  /sys/bus/pci/drivers/ipw3945/{PCI-ID}/

  For example:
  /sys/bus/pci/drivers/ipw3945/0000:02:01.0

  For the device level files, see /sys/bus/pci/drivers/ipw3945:

  rf_kill
  read - 
  0 = RF kill not enabled (radio on)
  1 = SW based RF kill active (radio off)
  2 = HW based RF kill active (radio off)
3 = Both HW and SW RF kill active (radio off)

  write -
  0 = If SW based RF kill active, turn the radio back on
  1 = If radio is on, activate SW based RF kill

  NOTE: If you enable the SW based RF kill and then toggle the HW
  based RF kill from ON -> OFF -> ON, the radio will NOT come back on

  led
  read -
  0 = LED code disabled
  1 = LED code enabled
  write -
  0 = Disable LED code
  1 = Enable LED code

  NOTE: The LED code has been reported to hang some systems when 
  running ifconfig and is therefore disabled by default.

  scan_age
  read -
  Maximum age of a usable network in milliseconds 

  write -
  Maximum age of a usable network in milliseconds.  For example:

# echo 15000 > /sys/bus/pci/drivers/ipw3945/*/scan_age

                                             will set a maximum age of 15 seconds.  The default as of 
                                             ieee80211-1.1.12 was 15 seconds.  Some users find setting this to
                                             60 seconds is more appropriate.

                                             channels
                                             read -

                                             Used to provide details on the channel capabilities enabled
                                             by the adapter.

                                             Example:   

                                             % cat /sys/bus/pci/drivers/ipw3945/*/channels

                                                                                 Displaying 13 channels in 2.4Ghz band (802.11bg):
                                                                                 1: 17dBm: BSS, IBSS, active/passive.
                                                                                 2: 17dBm: BSS, IBSS, active/passive.
                                                                                 ...
                                                                                 11: 17dBm: BSS, IBSS, active/passive.
                                                                                 12: 17dBm: BSS, passive only.
                                                                                 13: 17dBm: BSS, passive only.
                                                                                 Displaying 19 channels in 5.2Ghz band (802.11a):
                                                                                 36: 17dBm: BSS, IBSS, active/passive.
                                                                                 ...
                                                                                 48: 17dBm: BSS, IBSS, active/passive.
                                                                                 52: 17dBm: BSS (radar spectrum), passive only.
                                                                                 ...
                                                                                 136: 17dBm: BSS (radar spectrum), passive only.
                                                                                 140: 17dBm: BSS (radar spectrum), passive only.

                                                                                 For channels marked where ad-hoc is not supported (IBSS is not 
                                                                                 listed), you can neither join or create an IBSS (ad-hoc) network 
                                                                                 on that channel.

                                                                                 If CONFIG_IPW3945_PROMISCUOUS is enabled:

                                                                                 rtap_iface
                                                                                 Set to 1 to create a promiscuous radiotap interface.  This 
                                                                                 interface will be set to type ARPHRD_IEEE80211_RADIOTAP and will 
                                                                                 be passed every frame received over the air by the adapter.

                                                                                 Set to 0 to remove the created interface.

                                                                                 If an interface is configured, reading the entry will provide 
                                                                                 the name of the interface, for example 'rtap0'.  If no interface 
                                                                                 is created, -1 will be returned.  

                                                                                 If CONFIG_IPW3945_SIM_RX is enabled:

                                                                                 rx
                                                                                 This is a write-only entry.  The driver expects a binary blob
                                                                                 to be passed to this entry in radiotap header format.  The
                                                                                 driver will parse that format and configure an internal 
                                                                                 structure as if the frame had been received over the air.  It 
                                                                                 will then be passed to the driver, simulating reception of the 
                                                                                 frame.

                                                                                 For a sample application that writes to this file, see

                                                                                 http://ipw3945.sf.net/sim_rx.c


                                                                                 ===============================================
                                                                                 5. Wireless Tools Details
                                                                                 ===============================================

                                                                                 Due to an issue in handling 64-bit integers in the v28 based versions of 
                                                                                 the wireless tools, we recommend that only wireless tools based on v29 be 
                                                                                 used on 64-bit platforms.

                                                                                 5.1. iwlist
                                                                                 -----------------------------------------------

                                                                                 If a wireless tool command is not described below, please see the
                                                                                 iwlist man page for details.  

                                                                                 5.1.1. iwlist scan

                                                                                 The wireless tools default to only waiting 2 seconds between requesting
                                                                                 a scan and reporting the scan results.  In some hardware configurations,
                                                                                 two seconds is not long enough to rotate through all of the available
                                                                                 channels looking for valid networks.  As such, you may find better 
                                                                                 results by running iwlist scan once, then waiting a few seconds and 
  running it again.  For example:

  % iwlist scan 2>&1>/dev/null & sleep 3 ; iwlist scan

  While associated, the scan results can take substantially longer to return
  as the driver is limited on how long it can be away from the currently
  associated channel without impacting packet transmission.  As such,
  you may need to run the command several times to see all networks.  

  You can also try increasing the maximum age of a network reported by the
  ieee80211 subsystem via the scan_age sysfs entry.

  5.1.2. iwlist freq/channel

  This will list all of the channels that can be used 
  with the current hardware card.  There are various versions of the 
  Intel PRO/Wireless 3945ABG Network Connection for different geographies.  
  The results seen on one computer may not match the results seen on another
  computer with a different geography card.

  'iwlist freq' will show you the list of supported channels, but it does 
  not provide any indication of what type of spectrum management may be 
  enabled for a given channel.

  You can view the regulatory requirements for your adapter by examining 
  the contents of the 'channels' sysfs entry as described under 
  channels in the Device Level Sysfs Helper Files section of this document.

  5.1.3. iwlist bitrate/rate

  Returns the list of supported Tx data rates sorted by modulation and then
  speed.  Modulation is sorted by CCK rates first, then OFDM.

  5.1.4. iwlist power

  See section on Power Management.

  5.1.5. iwlist txpower

  See section on Tx Power.

  5.1.6. iwlist ap/accesspoints/peer

  Deprecated.  See iwlist man page.

  5.2. iwpriv
  -----------------------------------------------

  As an interface designed to handle generic hardware, there are certain 
  capabilities not exposed through the normal Wireless Tool interface.  As 
  such, a provision is provided for a driver to declare custom, or 
  private, methods.  The Intel(R) PRO/Wireless 3945ABG Network Connection 
  driver for Linux defines several of these to configure various settings.

  The general form of using the private wireless methods is:

  % iwpriv $IFNAME method parameters

  Where $IFNAME is the interface name the device is registered with 
  (typically eth1, customized via one of the various network interface
   name managers, such as ifrename)

  The supported private methods are:

  get_mode
  Can be used to report out which IEEE 802.11 mode the driver is 
  configured to support.  Example:

  % iwpriv eth1 get_mode
eth1  get_mode:802.11abg (7)

  set_mode
  Can be used to configure which IEEE 802.11 mode the driver will 
  support.  

  Usage:
  % iwpriv eth1 set_mode {mode}
  Where {mode} is a number in the range 1-7:
1 802.11a (ABG only)
  2 802.11b
3 802.11ab (ABG only)
  4 802.11g 
5 802.11ag (ABG only)
  6 802.11bg
7 802.11abg (ABG only)

  get_preamble
  Can be used to report configuration of preamble length.

  set_preamble
  Can be used to set the configuration of preamble length:

  Usage:
  % iwpriv eth1 set_preamble {mode}
  Where {mode} is one of:
  1 Long preamble only
0 Auto (long or short based on connection)

  set_power
  get_power

  See Power Management section.


  5.3. iwconfig
  -----------------------------------------------

  If a wireless tool command is not described below, please see the
  iwconfig man page for details.  

  5.3.1. iwconfig nwid/domain

  Not supported.

  5.3.2. iwconfig freq/channel

  See iwconfig man page for general description.

  Once configured, the adapter will only use the channel or frequency
  specified, if valid for the current hardware configuration.  You
  can set the adapter back to use any channel by specifying '0' as the 
  channel.

  5.3.3. iwconfig sens

  Not supported.

  5.3.4. iwconfig mode

  See iwconfig man page for general description.  

Current modes supported: Ad-Hoc and Managed (Auto)
  Current modes enabled but untested: Monitor
  Current modes unsupported: Master, Repeater, Secondary.

  If you configure the adapter to be locked to a specific channel or network
  while in one mode, those settings will remain in effect when you switch 
  modes.  For  example:

  % iwconfig eth1 mode ad-hoc channel 3 essid Flubox
  % iwconfig eth1 mode managed

  The device will still be configured to only associate with the network 
  'Flubox' on channel '3'.  You can reset this via:

  % iwconfig eth1 channel 0 essid any ap any

  5.3.5. iwconfig frag

  See iwconfig man page for general information.

  The 'auto' fragmentaton mode is not supported by the driver.
  You can set an explicit fragmentation threshold or turn fragmentation off.
  Attempts to set the fragmentation threshold to 'auto' will return an error
  from iwconfig.

  5.3.6. iwconfig power

  See Power Management section.

  5.3.7. iwconfig txpower

  See iwconfig man page for general information.

  If you wish to set an upper limit on the transmit power
  used by the adapter in dBm do not postfix a unit of measurement to the 
  parameter.  For example:

  % iwconfig eth1 txpower 10

  will set the upper limit to 10dBm.  If you provide the unit 'dBm', the 
  wireless tools will erroneously convert the value as if it were provided
  in watts.

  See Tx Power section for more details.

  5.3.8. iwconfig commit

  Not needed/supported.

  5.3.9. iwconfig rts

  Setting the RTS threshold value is configured to match the IEEE 802.11
  specification.

  Setting the RTS value to:

  * 0 will use RTS for all unicast data/mgmt packets.
  * greater than the maximum MSDU (2304) will not use RTS for any 
  unicast data/mgmt packets.
  * greater than 2347 or less than 0 will return an error.
  * all other values will result in RTS for unicast data/mgmt 
  frames if the MPDU is greater than the RTS.

  The RTS threshold defaults to 2347 (resulting in no RTS usage).

  6. Support
  -----------------------------------------------

  For general development information and support, go to:

  http://ipw3945.sf.net/

  Stable releases can be downloaded from:

  http://support.intel.com

  For installation support on the Intel PRO/Wireless 3945ABG Network Connection
  driver (stable versions) on Linux kernels 2.6.13 or later, email support is
  available from:  

  http://supportmail.intel.com


  7. License
  -----------------------------------------------

  With the exception of the file ipw3945_daemon.h, all of the files 
  in this archive are licensed under the terms of version 2 of the GNU 
  General Public License as published by the Free Software Foundation.

  The file ipw3945_daemon.h is provided under a dual BSD/GPLv2 license.
  When using or redistributing this file, you may do so under either 
  license.

  GPL LICENSE SUMMARY

  Copyright(c) 2005 - 2006 Intel Corporation. All rights reserved.

  This program is free software; you can redistribute it and/or modify 
  it under the terms of version 2 of the GNU General Public License as
  published by the Free Software Foundation.

  This program is distributed in the hope that it will be useful, but 
  WITHOUT ANY WARRANTY; without even the implied warranty of 
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
  General Public License for more details.

  You should have received a copy of the GNU General Public License 
  along with this program; if not, write to the Free Software 
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110, 
  USA

  The full GNU General Public License is included in this distribution 
  in the file called LICENSE.GPL.

  Contact Information:
  James P. Ketrenos <ipw2100-admin@linux.intel.com>
  Intel Corporation, 5200 N.E. Elam Young Parkway, Hillsboro, OR 97124-6497

  BSD LICENSE 

  Copyright(c) 2005 - 2006 Intel Corporation. All rights reserved.
  All rights reserved.

  Redistribution and use in source and binary forms, with or without 
  modification, are permitted provided that the following conditions 
  are met:

  * Redistributions of source code must retain the above copyright 
  notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright 
  notice, this list of conditions and the following disclaimer in 
  the documentation and/or other materials provided with the 
  distribution.
  * Neither the name of Intel Corporation nor the names of its 
  contributors may be used to endorse or promote products derived 
  from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
  AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
      LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
      DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

  ------------------------------
  Copyright (C) 2005 - 2006, Intel Corporation

  INFORMATION IN THIS DOCUMENT IS PROVIDED IN CONNECTION WITH INTEL PRODUCTS.  
  EXCEPT AS PROVIDED IN INTEL'S TERMS AND CONDITIONS OF SALE FOR SUCH PRODUCTS, 
  INTEL ASSUMES NO LIABILITY WHATSOEVER, AND INTEL DISCLAIMS ANY EXPRESS OR 
  IMPLIED WARRANTY RELATING TO SALE AND/OR USE OF INTEL PRODUCTS, INCLUDING 
  LIABILITY OR WARRANTIES RELATING TO FITNESS FOR A PARTICULAR PURPOSE, 
  MERCHANTABILITY, OR INFRINGEMENT OF ANY PATENT, COPYRIGHT, OR OTHER 
  INTELLECTUAL PROPERTY RIGHT. 

  This document is subject to change without notice. 

  * Other names and brands may be claimed as the property of others.


