<?php
// WARNING: THIS ANNOUNCE.PHP IS EMULATED - IT WILL NOT PERFORM THE STANDARD
// FUNCTIONS OF A SCRAPE SCRIPT
// IT DOES NOT RETURN PONG
/*
    Anatomic P2P Wrapper script for old clients (ANNOUNCE.PHP) 0.1 BETA MySQL
    Copyright (C) 2005  kunkie

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
// This no longer searches other supernodes (it's unlikely that they can do anything)
function quote_smart($value)
{
   // Stripslashes
   if (get_magic_quotes_gpc())
   {
       $value = stripslashes($value);
   }
   // Quote if not integer
   if (!is_numeric($value))
   {
       $value = "'" . mysql_real_escape_string($value) . "'";
   }
   return $value;
}
 function er($txt)
{
        die('d14:failure reason' . strlen($txt) . ':' . $txt . 'e');
}

if($_GET['compact'] == 1 && isset($_GET['port']) && isset($_GET['info_hash']))
{
    // compact, port and hash are only the important parts - most other bits are junk
    // info_hash redundancy checks from FBT2
    $info_hash = $_GET['info_hash'];
    if(strlen($info_hash) != 20)
    {
        $info_hash = stripcslashes($_GET['info_hash']);
    }
    if(strlen($info_hash) != 20)
    {
        er('Invalid info_hash');
    }
    $info_hash = bin2hex($info_hash);
    $qstring = "";
    // the other query strings are not going to be used
    if(isset($_GET['left']))
    {
         $qstring .= "&left=" . $_GET['left'];
    }
    if(isset($_GET['event']))
    {
         $qstring .= "&event=" . $_GET['event'];
    }
    if(isset($_GET['numwant']))
    {
         $qstring .= "&numwant=" . $_GET['numwant'];
    }
    if(isset($_GET['ip']))
    {
         $qstring .= "&ip=" . $_GET['ip'];
    }
    include "common.php";
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf("SELECT trackers.url FROM trackers, hashes WHERE hashes.trackerid = trackers.trackerid AND hashes.infohash = %s LIMIT 1", quote_smart(pack("H*",$info_hash)));
    $qresult = mysql_query($query);
    $result = @mysql_fetch_row($qresult);
    mysql_close($db);
    if(isset($result[0]))
    {
        $url = $result[0] . "?" . "compact=1&" . "port=" . $_GET['port'] . "&info_hash=" . urlencode(pack("H*",$info_hash)) . $qstring ;
        header("Location: $url", TRUE, 302);
    }
    else
    {
        er('No tracker could be allocated to your torrent. It may have expired.');
    }

}
else
{
 er('Your client does not support the compact tracker protocol. Please upgrade to the latest version.');
}
?>