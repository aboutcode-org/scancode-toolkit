<?php
/***********************************************************
 Copyright (C) 2010-2013 Hewlett-Packard Development Company, L.P.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 version 2 as published by the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
***********************************************************/
/**
 * \file nomos-diff.php 
 * \brief Compare License Browser, list license histogram
 */

define("TITLE_ui_nomos_diff", _("Compare License Browser"));

class ui_nomos_diff extends FO_Plugin
{
  var $Name       = "nomosdiff";
  var $Title      = TITLE_ui_nomos_diff;
  var $Version    = "1.0";
  // var $MenuList= "Jobs::License";
  var $Dependency = array("browse","view");
  var $DBaccess   = PLUGIN_DB_READ;
  var $LoginFlag  = 0;
  var $ColumnSeparatorStyleL = "style='border:solid 0 #006600; border-left-width:2px;padding-left:1em'";


  /**
   * \brief Create and configure database tables
   */
  function Install()
  {
    global $PG_CONN;
    if (empty($PG_CONN)) {
      return(1);
    } /* No DB */

    return(0);
  } // Install()

  /**
   * \brief Customize submenus.
   */
  function RegisterMenus()
  {
    /* at this stage you have to call this plugin with a direct URL
     that displays both trees to compare.
    */
    return 0;
  } // RegisterMenus()


  /**
   * \brief This is called before the plugin is used.
   * It should assume that Install() was already run one time
   * (possibly years ago and not during this object's creation).
   *
   * \return true on success, false on failure.
   * A failed initialize is not used by the system.
   * \note This function must NOT assume that other plugins are installed.
   */
  function Initialize()
  {
    global $_GET;

    if ($this->State != PLUGIN_STATE_INVALID) {
      return(1);
    } // don't re-run
    if ($this->Name !== "") // Name must be defined
    {
      global $Plugins;
      $this->State=PLUGIN_STATE_VALID;
      array_push($Plugins,$this);
    }
    return($this->State == PLUGIN_STATE_VALID);
  } // Initialize()

  /**
   * \brief get an array with uploadtree record and agent_pk
   */
  function GetTreeInfo($Uploadtree_pk)
  {
    $TreeInfo = GetSingleRec("uploadtree", "WHERE uploadtree_pk = $Uploadtree_pk");
    $TreeInfo['agent_pk'] = LatestAgentpk($TreeInfo['upload_fk'], "nomos_ars");

    // Get the uploadtree table
    $UploadRec = GetSingleRec("upload", "where upload_pk=$TreeInfo[upload_fk]");
    $TreeInfo['uploadtree_tablename'] = $UploadRec['uploadtree_tablename'];
    return $TreeInfo;
  }


  /**
   * \brief get history info for the directory BY LICENSE.
   * \param $Uploadtree_pk - Uploadtree_pk
   * \return a string with the histogram for the directory BY LICENSE.
   */
  function UploadHist($Uploadtree_pk, $TreeInfo)
  {
    global $PG_CONN;

    $VLic = '';
    $lft = $TreeInfo['lft'];
    $rgt = $TreeInfo['rgt'];
    $upload_pk = $TreeInfo['upload_fk'];
    $agent_pk = $TreeInfo['agent_pk'];

    /*  Get the counts for each license under this UploadtreePk*/
    $sql = "SELECT distinct(rf_shortname) as licname,
                   count(rf_shortname) as liccount, rf_shortname
              from license_ref,license_file,
                  (SELECT distinct(pfile_fk) as PF from $TreeInfo[uploadtree_tablename]
                     where upload_fk=$upload_pk 
                       and {$TreeInfo['uploadtree_tablename']}.lft BETWEEN $lft and $rgt) as SS
              where PF=pfile_fk and agent_fk=$agent_pk and rf_fk=rf_pk
              group by rf_shortname 
              order by liccount desc";
    $result = pg_query($PG_CONN, $sql);
    DBCheckResult($result, $sql, __FILE__, __LINE__);

    /* Write license histogram to $VLic  */
    $LicCount = 0;
    $UniqueLicCount = 0;
    $NoLicFound = 0;
    $VLic .= "<table border=1 id='lichistogram'>\n";

    $text = _("Count");
    $VLic .= "<tr><th >$text</th>";

    $text = _("Files");
    $VLic .= "<th >$text</th>";

    $text = _("License Name");
    $VLic .= "<th align=left>$text</th></tr>\n";

    while ($row = pg_fetch_assoc($result))
    {
      $UniqueLicCount++;
      $LicCount += $row['liccount'];

      /*  Count  */
      $VLic .= "<tr><td align='right'>$row[liccount]</td>";

      /*  Show  */
      $ShowTitle = _("Click Show to list files with this license.");
      $VLic .= "<td align='center'><a href='";
      $VLic .= Traceback_uri();

      $text = _("Show");
      $VLic .= "?mod=license_list_files&napk=$agent_pk&item=$Uploadtree_pk&lic=" . urlencode($row['rf_shortname']) . "' title='$ShowTitle'>$text</a></td>";

      /*  License name  */
      $VLic .= "<td align='left'>";
      $rf_shortname = rawurlencode($row['rf_shortname']);
      $VLic .= "<a id='$rf_shortname' onclick='FileColor_Get(\"" . Traceback_uri() . "?mod=ajax_filelic&napk=$agent_pk&item=$Uploadtree_pk&lic=$rf_shortname\")'";
      $VLic .= ">$row[licname] </a>";
      $VLic .= "</td>";
      $VLic .= "</tr>\n";
      if ($row['licname'] == "No_license_found") $NoLicFound =  $row['liccount'];
    }
    pg_free_result($result);
    $VLic .= "</table>\n";
    $VLic .= "<p>\n";

    return($VLic);
  } // UploadHist()


  /**
   * \brief get the entire <td> ... </td> for $Child file listing table
   * License differences are highlighted.
   */
  function ChildElt($Child, $agent_pk, $OtherChild)
  {
    $UniqueTagArray = array();
    $licstr = $Child['licstr'];

    /* If both $Child and $OtherChild are specified,
     * reassemble licstr and highlight the differences
     */
    if ($OtherChild and $OtherChild)
    {
      $licstr = "";
      $DiffLicStyle = "style='background-color:#ffa8a8'";  // mid red pastel
      foreach ($Child['licarray'] as $rf_pk => $rf_shortname)
      {
        if (!empty($licstr)) $licstr .= ", ";
        if (@$OtherChild['licarray'][$rf_pk])
        {
          /* license is in both $Child and $OtherChild */
          $licstr .= $rf_shortname;
        }
        else
        {
          /* license is missing from $OtherChild */
          $licstr .= "<span $DiffLicStyle>$rf_shortname</span>";
        }
      }
    }

    $ColStr = "<td id='$Child[uploadtree_pk]' align='left'>";
    $ColStr .= "$Child[linkurl]";
    /* show licenses under file name */
    $ColStr .= "<br>";
    $ColStr .= "<span style='position:relative;left:1em'>";
    $ColStr .= $licstr;
    $ColStr .= "</span>";
    $ColStr .= "</td>";

    /* display item links */
    $ColStr .= "<td valign='top'>";
    $uploadtree_tablename = GetUploadtreeTableName($Child['upload_fk']);
    $ColStr .= FileListLinks($Child['upload_fk'], $Child['uploadtree_pk'], $agent_pk, $Child['pfile_fk'], True, $UniqueTagArray, $uploadtree_tablename);
    $ColStr .= "</td>";
    return $ColStr;
  }  /* ChildElt() */


  /**
   * \brief get a string with the html table rows comparing the two file lists. \n 
   * Each row contains 5 table fields.
   * The third field is just for a column separator.
   * If files match their fuzzyname then put on the same row.
   * Highlight license differences.
   * Unmatched fuzzynames go on a row of their own.
   */
  function ItemComparisonRows($Master, $agent_pk1, $agent_pk2)
  {
    $TableStr = "";
    $RowStyle1 = "style='background-color:#ecfaff'";  // pale blue
    $RowStyle2 = "style='background-color:#ffffe3'";  // pale yellow
    $RowNum = 0;

    foreach ($Master as $key => $Pair)
    {
      $RowStyle = (++$RowNum % 2) ? $RowStyle1 : $RowStyle2;
      $TableStr .= "<tr $RowStyle>";

      $Child1 = GetArrayVal("1", $Pair);
      $Child2 = GetArrayVal("2", $Pair);
      if (empty($Child1))
      {
        $TableStr .= "<td></td><td></td>";
        $TableStr .= "<td $this->ColumnSeparatorStyleL>&nbsp;</td>";
        $TableStr .= $this->ChildElt($Child2, $agent_pk2, $Child1);
      }
      else if (empty($Child2))
      {
        $TableStr .= $this->ChildElt($Child1, $agent_pk1, $Child2);
        $TableStr .= "<td $this->ColumnSeparatorStyleL>&nbsp;</td>";
        $TableStr .= "<td></td><td></td>";
      }
      else if (!empty($Child1) and !empty($Child2))
      {
        $TableStr .= $this->ChildElt($Child1, $agent_pk1, $Child2);
        $TableStr .= "<td $this->ColumnSeparatorStyleL>&nbsp;</td>";
        $TableStr .= $this->ChildElt($Child2, $agent_pk2, $Child1);
      }

      $TableStr .= "</tr>";
    }

    return($TableStr);
  } // ItemComparisonRows()



  /**
   * \brief Add license array to Children array.
   */
  function AddLicStr($TreeInfo, &$Children)
  {
    if (!is_array($Children)) return;
    $agent_pk = $TreeInfo['agent_pk'];
    foreach($Children as &$Child)
    {
      /** do not get duplicated licenses */
      $Child['licarray'] = GetFileLicenses($agent_pk, 0, $Child['uploadtree_pk']);
      $Child['licstr'] = implode(", ", $Child['licarray']);
    }
  }


  /**
   * \brief removes identical files
   * If a child pair are identical remove the master record
   */
  function filter_samehash(&$Master)
  {
    if (!is_array($Master)) return;

    foreach($Master as $Key =>&$Pair)
    {
      if (empty($Pair[1]) or empty($Pair[2])) continue;
      if (empty($Pair[1]['pfile_fk'])) continue;
      if (empty($Pair[2]['pfile_fk'])) continue;

      if ($Pair[1]['pfile_fk'] == $Pair[2]['pfile_fk'])
      unset($Master[$Key]);
    }
    return;
  }  /* End of samehash */


  /**
   * \brief removes files that have the same name and license list.
   */
  function filter_samelic(&$Master)
  {
    foreach($Master as $Key =>&$Pair)
    {
      if (empty($Pair[1]) or empty($Pair[2])) continue;
      if (($Pair[1]['ufile_name'] == $Pair[2]['ufile_name'])
      && ($Pair[1]['licstr'] == $Pair[2]['licstr']))
      unset($Master[$Key]);
    }
    return;
  }  /* End of samelic */


  /**
   * \brief removes files that have the same fuzzyname, and same license list.
   */
  function filter_samelicfuzzy(&$Master)
  {
    foreach($Master as $Key =>&$Pair)
    {
      if (empty($Pair[1]) or empty($Pair[2])) continue;
      if (($Pair[1]['fuzzyname'] == $Pair[2]['fuzzyname'])
      && ($Pair[1]['licstr'] == $Pair[2]['licstr']))
      unset($Master[$Key]);
    }
    return;
  }  /* End of samelic */


  /**
   * \brief removes pairs of "No_license_found"
   * Or pairs that only have one file and "No_license_found"
   * Uses fuzzyname.
   */
  function filter_nolics(&$Master)
  {
    $NoLicStr = "No_license_found";

    foreach($Master as $Key =>&$Pair)
    {
      $Pair1 = GetArrayVal("1", $Pair);
      $Pair2 = GetArrayVal("2", $Pair);

      if (empty($Pair1))
      {
        if ($Pair2['licstr'] == $NoLicStr)
        unset($Master[$Key]);
        else
        continue;
      }
      else if (empty($Pair2))
      {
        if ($Pair1['licstr'] == $NoLicStr)
        unset($Master[$Key]);
        else
        continue;
      }
      else if (($Pair1['licstr'] == $NoLicStr)
      and ($Pair2['licstr'] == $NoLicStr))
      unset($Master[$Key]);
    }
    return;
  }  /* End of nolics */

  /**
   * \brief filter children through same license, same hash, no license, same fuzzy license
   *
   * \param $filter - none, samelic, samehash
   * An empty or unknown filter is the same as "none"
   */
  function FilterChildren($filter, &$Master)
  {
    switch($filter)
    {
      case 'samehash':
        $this->filter_samehash($Master);
        break;
      case 'samelic':
        $this->filter_samehash($Master);
        $this->filter_samelic($Master);
        break;
      case 'samelicfuzzy':
        $this->filter_samehash($Master);
        $this->filter_samelicfuzzy($Master);
        break;
      case 'nolics':
        $this->filter_samehash($Master);
        $this->filter_nolics($Master);
        $this->filter_samelicfuzzy($Master);
        break;
      default:
        break;
    }
  }


  /**
   * \brief HTML output, returns HTML as string.
   */
  function HTMLout($Master, $uploadtree_pk1, $uploadtree_pk2, $in_uploadtree_pk1, $in_uploadtree_pk2, $filter, $TreeInfo1, $TreeInfo2)
  {
    /* Initialize */
    $FreezeText = _("Freeze Path");
    $unFreezeText = _("Frozen, Click to unfreeze");
    $OutBuf = '';

    /******* javascript functions ********/
    $OutBuf .= "\n<script language='javascript'>\n";
    /* function to replace this page specifying a new filter parameter */
    $OutBuf .= "function ChangeFilter(selectObj, utpk1, utpk2){";
    $OutBuf .= "  var selectidx = selectObj.selectedIndex;";
    $OutBuf .= "  var filter = selectObj.options[selectidx].value;";
    $OutBuf .= '  window.location.assign("?mod=' . $this->Name .'&item1="+utpk1+"&item2="+utpk2+"&filter=" + filter); ';
    $OutBuf .= "}";

    /* Freeze function (path list in banner)
     FreezeColNo is the ID of the column to freeze: 1 or 2
    Toggle Freeze button label: Freeze Path <-> Unfreeze Path
    Toggle Freeze button background color: white to light blue
    Toggle which paths are frozen: if path1 freezes, then unfreeze path2.
    Rewrite urls: eg &item1 ->  &Fitem1
    */
    $OutBuf .= "function Freeze(FreezeColNo) {";
    $OutBuf .=  "var FreezeElt1 = document.getElementById('Freeze1');";
    $OutBuf .=  "var FreezeElt2 = document.getElementById('Freeze2');";

    /* change the freeze labels to denote their new status */
    $OutBuf .=  "if (FreezeColNo == '1')";
    $OutBuf .=  "{";
    $OutBuf .=    "if (FreezeElt1.innerHTML == '$unFreezeText') ";
    $OutBuf .=    "{";
    $OutBuf .=      "FreezeElt1.innerHTML = '$FreezeText';";
    $OutBuf .=      "FreezeElt1.style.backgroundColor = 'white';";
    $OutBuf .=    "}";
    $OutBuf .=    "else {";
    $OutBuf .=      "FreezeElt1.innerHTML = '$unFreezeText';";
    $OutBuf .=      "FreezeElt1.style.backgroundColor = '#EAF7FB';";
    $OutBuf .=      "FreezeElt2.innerHTML = '$FreezeText';";
    $OutBuf .=      "FreezeElt2.style.backgroundColor = 'white';";
    $OutBuf .=    "}";
    $OutBuf .=  "}";
    $OutBuf .=  "else {";
    $OutBuf .=    "if (FreezeElt2.innerHTML == '$unFreezeText') ";
    $OutBuf .=    "{";
    $OutBuf .=      "FreezeElt2.innerHTML = '$FreezeText';";
    $OutBuf .=      "FreezeElt2.style.backgroundColor = 'white';";
    $OutBuf .=    "}";
    $OutBuf .=    "else {";
    $OutBuf .=      "FreezeElt1.innerHTML = '$FreezeText';";
    $OutBuf .=      "FreezeElt1.style.backgroundColor = 'white';";
    $OutBuf .=      "FreezeElt2.innerHTML = '$unFreezeText';";
    $OutBuf .=      "FreezeElt2.style.backgroundColor = '#EAF7FB';";
    $OutBuf .=    "}";
    $OutBuf .=  "}";

    /* Alter the url to add freeze={column number}  */
    $OutBuf .=  "var i=0;";
    $OutBuf .=  "var linkid;";
    $OutBuf .=  "var linkelt;";
    $OutBuf .=  "var UpdateCol;";
    $OutBuf .=  "if (FreezeColNo == 1) UpdateCol=2;else UpdateCol=1;";
    $OutBuf .=  "var numlinks = document.links.length;";
    $OutBuf .=  "for (i=0; i < numlinks; i++)";
    $OutBuf .=  "{";
    $OutBuf .=    "linkelt = document.links[i];";
    $OutBuf .=    "if (linkelt.href.indexOf('col='+UpdateCol) >= 0)";
    $OutBuf .=    "{";
    $OutBuf .=      "linkelt.href = linkelt.href + '&freeze=' + FreezeColNo;";
    $OutBuf .=    "}";
    $OutBuf .=  "}";
    $OutBuf .= "}";
    $OutBuf .= "</script>\n";
    /******* END javascript functions  ********/


    /* Select list for filters */
    $SelectFilter = "<select name='diff_filter' id='diff_filter' onchange='ChangeFilter(this,$uploadtree_pk1, $uploadtree_pk2)'>";
    $Selected = ($filter == 'none') ? "selected" : "";
    $SelectFilter .= "<option $Selected value='none'>0. Remove nothing";
    $Selected = ($filter == 'samehash') ? "selected" : "";
    $SelectFilter .= "<option $Selected value='samehash'>1. Remove duplicate (same hash) files";
    $Selected = ($filter == 'samelic') ? "selected" : "";
    $SelectFilter .= "<option $Selected value='samelic'>2. Remove duplicate files (different hash) with unchanged licenses";
    $Selected = ($filter == 'samelicfuzzy') ? "selected" : "";
    $SelectFilter .= "<option $Selected value='samelicfuzzy'>2b. Same as 2 but fuzzy match file names";
    $Selected = ($filter == 'nolics') ? "selected" : "";
    $SelectFilter .= "<option $Selected value='nolics'>3. Same as 2b. but also remove files with no license";
    $SelectFilter .= "</select>";


    $StyleRt = "style='float:right'";
    $OutBuf .= "<a name='flist' href='#histo' $StyleRt > Jump to histogram </a><br>";

    /* Switch to bucket diff view */
    $text = _("Switch to bucket view");
    $BucketURL = Traceback_uri();
    $BucketURL .= "?mod=bucketsdiff&item1=$uploadtree_pk1&item2=$uploadtree_pk2";
    $OutBuf .= "<a href='$BucketURL' $StyleRt > $text </a> ";


    //    $TableStyle = "style='border-style:collapse;border:1px solid black'";
    $TableStyle = "";
    $OutBuf .= "<table border=0 id='dirlist' $TableStyle>";

    /* Select filter pulldown */
    $OutBuf .= "<tr><td colspan=5 align='center'>Filter: $SelectFilter<br>&nbsp;</td></tr>";

    /* File path */
    $OutBuf .= "<tr>";
    $Path1 = Dir2Path($uploadtree_pk1, $TreeInfo1['uploadtree_tablename']);
    $Path2 = Dir2Path($uploadtree_pk2, $TreeInfo2['uploadtree_tablename']);
    $OutBuf .= "<td colspan=2>";
    $OutBuf .= Dir2BrowseDiff($Path1, $Path2, $filter, 1, $this);
    $OutBuf .= "</td>";
    $OutBuf .= "<td $this->ColumnSeparatorStyleL colspan=3>";
    $OutBuf .= Dir2BrowseDiff($Path1, $Path2, $filter, 2, $this);
    $OutBuf .= "</td></tr>";

    /* File comparison table */
    $OutBuf .= $this->ItemComparisonRows($Master, $TreeInfo1['agent_pk'], $TreeInfo2['agent_pk']);

    /*  Separator row */
    $ColumnSeparatorStyleTop = "style='border:solid 0 #006600; border-top-width:2px; border-bottom-width:2px;'";
    $OutBuf .= "<tr>";
    $OutBuf .= "<td colspan=5 $ColumnSeparatorStyleTop>";
    $OutBuf .= "<a name='histo' href='#flist' style='float:right'> Jump to top </a>";
    $OutBuf .= "</a>";
    $OutBuf .= "</tr>";

    /* License histogram */
    $OutBuf .= "<tr>";
    $Tree1Hist = $this->UploadHist($uploadtree_pk1, $TreeInfo1);
    $OutBuf .= "<td colspan=2 valign='top' align='center'>$Tree1Hist</td>";
    $OutBuf .= "<td $this->ColumnSeparatorStyleL>&nbsp;</td>";
    $Tree2Hist = $this->UploadHist($uploadtree_pk2, $TreeInfo2);
    $OutBuf .= "<td colspan=2 valign='top' align='center'>$Tree2Hist</td>";
    $OutBuf .= "</tr></table>\n";

    $OutBuf .= "<a href='#flist' style='float:right'> Jump to top </a><p>";

    return $OutBuf;
  }


  /**
   * \brief generate output information \n 
   * filter: optional filter to apply \n
   * item1:  uploadtree_pk of the column 1 tree \n
   * item2:  uploadtree_pk of the column 2 tree \n
   * newitem1:  uploadtree_pk of the new column 1 tree \n
   * newitem2:  uploadtree_pk of the new column 2 tree \n
   * freeze: column number (1 or 2) to freeze
   */
  function Output()
  {
    if ($this->State != PLUGIN_STATE_READY) {
      return(0);
    }
    $V="";

    $uTime = microtime(true);
    /* */
    $updcache = GetParm("updcache",PARM_INTEGER);

    /* Remove "updcache" from the GET args.
     * This way all the url's based on the input args won't be
     * polluted with updcache
     * Use Traceback_parm_keep to ensure that all parameters are in order */
    $CacheKey = "?mod=" . $this->Name . Traceback_parm_keep(array("item1","item2", "filter"));
    if ($updcache)
    {
      $_SERVER['REQUEST_URI'] = preg_replace("/&updcache=[0-9]*/","",$_SERVER['REQUEST_URI']);
      unset($_GET['updcache']);
      $V = ReportCachePurgeByKey($CacheKey);
    }
    else
    {
      $V = ReportCacheGet($CacheKey);
    }

    if (empty($V) )  // no cache exists
    {
      $filter = GetParm("filter",PARM_STRING);
      if (empty($filter)) $filter = "samehash";
      $FreezeCol = GetParm("freeze",PARM_INTEGER);
      $in_uploadtree_pk1 = GetParm("item1",PARM_INTEGER);
      $in_uploadtree_pk2 = GetParm("item2",PARM_INTEGER);

      if (empty($in_uploadtree_pk1) && empty($in_uploadtree_pk2))
        Fatal("Bad input parameters.  Both item1 and item2 must be specified.", __FILE__, __LINE__);

      /* Check item1 and item2 upload permissions */
      $Item1Row = GetSingleRec("uploadtree", "WHERE uploadtree_pk = $in_uploadtree_pk1");
      $UploadPerm = GetUploadPerm($Item1Row['upload_fk']);
      if ($UploadPerm < PERM_READ)
      {
        $text = _("Permission Denied");
        echo "<h2>$text item 1<h2>";
        return;
      }

      $Item2Row = GetSingleRec("uploadtree", "WHERE uploadtree_pk = $in_uploadtree_pk2");
      $UploadPerm = GetUploadPerm($Item2Row['upload_fk']);
      if ($UploadPerm < PERM_READ)
      {
        $text = _("Permission Denied");
        echo "<h2>$text item 2<h2>";
        return;
      }

      $in_newuploadtree_pk1 = GetParm("newitem1",PARM_INTEGER);
      $in_newuploadtree_pk2 = GetParm("newitem2",PARM_INTEGER);
      $uploadtree_pk1  = $in_uploadtree_pk1;
      $uploadtree_pk2 = $in_uploadtree_pk2;

      if (!empty($in_newuploadtree_pk1))
      {
        if ($FreezeCol != 2)
        $uploadtree_pk2  = NextUploadtree_pk($in_newuploadtree_pk1, $in_uploadtree_pk2);
        $uploadtree_pk1  = $in_newuploadtree_pk1;
      }
      else
      if (!empty($in_newuploadtree_pk2))
      {
        if ($FreezeCol != 1)
        $uploadtree_pk1 = NextUploadtree_pk($in_newuploadtree_pk2, $in_uploadtree_pk1);
        $uploadtree_pk2 = $in_newuploadtree_pk2;
      }

      $newURL = Traceback_dir() . "?mod=" . $this->Name . "&item1=$uploadtree_pk1&item2=$uploadtree_pk2";
      if (!empty($filter)) $newURL .= "&filter=$filter";

      // rewrite page with new uploadtree_pks */
      if (($uploadtree_pk1 != $in_uploadtree_pk1)
      || ($uploadtree_pk2 != $in_uploadtree_pk2))
      {
        print <<< JSOUT
<script type="text/javascript">
  window.location.assign('$newURL');
</script>
JSOUT;
      }

      $TreeInfo1 = $this->GetTreeInfo($uploadtree_pk1);
      $TreeInfo2 = $this->GetTreeInfo($uploadtree_pk2);
      $ErrText = _("No license data for");
      $ErrText2 = _("Use Jobs > Agents to schedule a license scan.");
      $ErrMsg= '';
      if ($TreeInfo1['agent_pk'] == 0)
      {
        $ErrMsg = "$ErrText $TreeInfo1[ufile_name].<br>$ErrText2<p>";
      }
      else
      if ($TreeInfo2['agent_pk'] == 0)
      {
        $ErrMsg = "$ErrText $TreeInfo2[ufile_name].<br>$ErrText2<p>";
      }
      else
      {
        /* Get list of children */
        $Children1 = GetNonArtifactChildren($uploadtree_pk1);
        $Children2 = GetNonArtifactChildren($uploadtree_pk2);

        /* Add fuzzyname to children */
        FuzzyName($Children1);  // add fuzzyname to children
        FuzzyName($Children2);  // add fuzzyname to children

        /* add element licstr to children */
        $this->AddLicStr($TreeInfo1, $Children1);
        $this->AddLicStr($TreeInfo2, $Children2);

        /* Master array of children, aligned.   */
        $Master = MakeMaster($Children1, $Children2);

        /* add linkurl to children */
        FileList($Master, $TreeInfo1['agent_pk'], $TreeInfo2['agent_pk'], $filter, $this,
        $uploadtree_pk1, $uploadtree_pk2);

        /* Apply filter */
        $this->FilterChildren($filter, $Master);
      }

      switch($this->OutputType)
      {
        case "XML":
          break;
        case "HTML":
          if ($ErrMsg)
          $V .= $ErrMsg;
          else
          $V .= $this->HTMLout($Master, $uploadtree_pk1, $uploadtree_pk2, $in_uploadtree_pk1, $in_uploadtree_pk2, $filter, $TreeInfo1, $TreeInfo2);
          break;
        case "Text":
          break;
        default:
      }
      $Cached = false;
    }
    else
    $Cached = true;

    if (!$this->OutputToStdout) {
      return($V);
    }
    print "$V";
    $Time = microtime(true) - $uTime;  // convert usecs to secs
    $text = _("Elapsed time: %.2f seconds");
    printf( "<small>$text</small>", $Time);

    /**/
    if ($Cached)
    {
      $text = _("cached");
      $text1 = _("Update");
      echo " <i>$text</i>   <a href=\"$_SERVER[REQUEST_URI]&updcache=1\"> $text1 </a>";
    }
    else
    {
      //  Cache Report if this took longer than 1/2 second
      if ($Time > 0.5) ReportCachePut($CacheKey, $V);
    }
    /**/
    return;
  }  /* End Output() */

}  /* End Class */

$NewPlugin = new ui_nomos_diff;
$NewPlugin->Initialize();

?>
