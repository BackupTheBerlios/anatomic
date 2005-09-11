<!-- doctype html public "-//W3C//DTD HTML 4.0 Transitional//EN"-->
<HTML>
<HEAD>
<TITLE>Anatomic P2P MySQL Supertracker</TITLE>
<STYLE TYPE="text/css">
<!--
BODY, TD, TH {
        font-family: Verdana;
        font-size: 11px;
        color: #867C68;
}

A {
        text-decoration: none;
}

A:HOVER {
        color: #FF0000;
        text-decoration: underline;
}
-->
</STYLE>
</HEAD>
<BODY>
<?php

/*
    Anatomic P2P 0.1 BETA - Monitor Station MySQL
    Copyright (C) 2005 kunkie

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
// error_reporting(0);
include "common.php";
$serversig = $_SERVER['SERVER_SIGNATURE'];
echo "Anatomic P2P Supertracker 0.1 Beta MySQL on: <br> $serversig.<br> This script lists the status of some of the other nodes on the network registered with this supertracker.<BR>This page may take some time to load as nodes on the network synchronise with each other.<BR><BR>";
ob_flush();
flush();
// start of functions
function ping($url)
{
    $url = urldecode($url);
    $url .= "?ping=1";
    $pull = @file_get_contents($url);
    if($pull === "PONG")
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    }
}
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
// End of functions
$db = mysql_connect($dbhost, $dbuname, $dbpasswd);
mysql_select_db($dbname,$db);
$result = mysql_query("SELECT url FROM strackers WHERE alive = 1");
echo "<b>Supernodes / Supertrackers</b><br>The following supertrackers are known to be live:<br>";
$no = 0;
$alive = 0;
while($row = mysql_fetch_row($result))
{
    $no++;
    if(!ping($row[0]))
    {
    echo "<font color=\"red\"> $no: " . $row[0] . " - Did not reply</font><br>";
    $query = sprintf("UPDATE strackers SET timestamp = timestamp, alive = 0  WHERE url = %s", quote_smart($row[0]));
    mysql_query($query);
    }
    else
    {
    $alive++;
    echo "$no: ". $row[0] . "<br>";
    }
}
echo "<br> $alive supertrackers are alive out of $no.<br>";
// doing some cleanup
$weekold = time() - 86400; // it was a week originally but that time is too little
$result = mysql_query("SELECT url, UNIX_TIMESTAMP(timestamp) FROM strackers WHERE alive = 0" );
while($row = mysql_fetch_row($result))
{
    if($row[1] < $weekold)
    {
        $query = sprintf("DELETE FROM strackers WHERE url = %s", quote_smart($row[0]));
        mysql_query($query);
        echo "One dead supertracker was cleaned up.<br>";
    }
    elseif(ping($row[0])) // it might have suffered from a bit of downtime
    {
        $query = sprintf("UPDATE strackers SET timestamp = NOW(), alive = 1 WHERE url = %s", quote_smart($row[0]));
        mysql_query($query);
        echo "A supertracker that was thought to be dead is alive.<br>";
    }
}
echo "<p>If you want to submit a <b>supertracker/(super)node</b> to the current supertracker please use the form below:<p>
<form name=\"push\" action=\"cache.php\" method=\"get\">
Supertracker URL: <input name=\"push\" type=\"text\" size=55 value=\"http://\"><input type=\"submit\" value=\"Submit\"></form>";
echo "<br><br><b>Trackers</b><br>The following trackers are known to be alive: <br>";
$result = mysql_query("SELECT url, UNIX_TIMESTAMP(timestamp), trackerid FROM trackers WHERE alive = 1");
$no = 0;
$alive = 0;
$twodaysold = time() - 172800;
include "bdecode.php";
while($row = mysql_fetch_row($result))
{
    $no++;
    if(!ping($row[0]))
    {
    echo "<font color=\"red\"> $no: " . $row[0] . " - Did not reply</font><br>";
    $query = sprintf("UPDATE trackers SET timestamp = timestamp, alive = 0  WHERE url = %s", quote_smart($row[0]));
    mysql_query($query);
    }
    elseif($row[1] < $twodaysold)
    {
        $request = str_replace("/announce","/request", $row[0]);
        $bdata = @file_get_contents($request);
        if(substr($bdata, -1, 1) == "e" and substr($bdata, 0, 1) == "l")
        {
            // the bdecode library goes insane otherwise
            $bdata = bdecode($bdata);
            // build insert query
            $query = sprintf("DELETE FROM hashes WHERE trackerid = %s", quote_smart($row[2]));
            mysql_query($query);
            if(isset($bdata[0]))
            {
                $query = "INSERT INTO `hashes` (`trackerid`, `infohash`) VALUES ";
                foreach($bdata as $hash){
                    $query .= sprintf("(%s, %s),", $row[2] ,quote_smart(pack("H*", $hash)));
                }
                $query = trim($query , ","); // the last comma is not needed.
                mysql_query($query);
                $query = sprintf("UPDATE trackers SET timestamp = NOW(), alive = 1 WHERE url = %s ", quote_smart($row[0]));
                mysql_query($query);
            }
        $alive++;
        echo "<font color=\"green\"> $no: " . $row[0] . " - Data Updated</font><br>";
        }
    }
    else
    {
    $alive++;
    echo "$no: ". $row[0] . "<br>";
    }
}
echo "<br> $alive trackers are alive out of $no.<br>";
// more cleanup
$result = @mysql_query("SELECT url, UNIX_TIMESTAMP(timestamp), trackerid FROM trackers WHERE alive = 0 ORDER BY rand() LIMIT 2" );
while($row = mysql_fetch_row($result))
{
    if($row[1] < $weekold)
    {
        $query = sprintf("DELETE FROM trackers WHERE trackerid = %s", quote_smart($row[2]));
        mysql_query($query);
        $query = sprintf("DELETE FROM hashes WHERE trackerid = %s", quote_smart($row[2]));
        mysql_query($query);
        echo "Dead tracker cleaned up.<br>";
    }
    elseif(ping($row[0])) // it might have suffered from a bit of downtime
    {
        $query = sprintf("UPDATE trackers SET timestamp = NOW(), alive = 1 WHERE url = %s ", quote_smart($row[0]));
        mysql_query($query);
        $request = str_replace("/announce","/request", $row[0]);
        $bdata = @file_get_contents($request);
        if(substr($bdata, -1, 1) == "e" and substr($bdata, 0, 1) == "l")
        {
            // the bdecode library goes insane otherwise
            $bdata = bdecode($bdata);
            // build insert query
            $query = sprintf("DELETE FROM hashes WHERE trackerid = %s", quote_smart($row[2]));
            mysql_query($query);
            if(isset($bdata[0]))
            {
                $query = "INSERT INTO `hashes` (`trackerid`, `infohash`) VALUES ";
                foreach($bdata as $hash){
                    $query .= sprintf("(%s, %s),", $row[2] ,quote_smart(pack("H*", $hash)));
                }
                $query = trim($query , ","); // the last comma is not needed.
                mysql_query($query);
            }
            echo "A tracker that was thought to be dead is alive.<br>";
        }
    }
}
mysql_close($db);
echo "<p>If you want to submit a <b>tracker</b> to the current supertracker please use the form below:<p>
<form name=\"tpush\" action=\"cache.php\" method=\"get\">
Tracker URL: <input name=\"tpush\" type=\"text\" size=60 value=\"http://\"><input type=\"submit\" value=\"Submit\"></form>";
?>
</BODY>
</HTML>