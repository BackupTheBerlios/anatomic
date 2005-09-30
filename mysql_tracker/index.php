<?php
/*
    Anatomic P2P MySQL Tracker 0.1 RC1 (index.php)
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
include "common.php";
$db = mysql_connect($dbhost, $dbuname, $dbpasswd);
mysql_select_db($dbname,$db);
function mysql_date_parser($indate){
  //YYYY-MM-DD HH:mm:ss.splits
  $indate      = explode(" ", $indate);
  $dateArr    = explode("-", $indate[0]);
  $timeArr    = explode(":", $indate[1]);
  $timeArr[2] = substr($timeArr[2],0, strpos($timeArr[2],"."));
  $outdate = mktime(
     $timeArr[0],
     $timeArr[1],
     $timeArr[2],
     $dateArr[1],
     $dateArr[2],
     $dateArr[0]
  );
  return $outdate;
}
function getstat($info_hash)
{
    // The info_hash is a 40 byte hex string at this stage
    // the first thing to do is to remove the dead seeds
    // see scrape.php for more info about this code
    $query = sprintf('DELETE FROM `%s` WHERE UNIX_TIMESTAMP(timestamp) <= %s ', mysql_real_escape_string($info_hash), time() - 2400);
    mysql_query($query);
    $query = sprintf('SELECT SUM(`seed_or_peer`), COUNT(*) - SUM(`seed_or_peer`) FROM `%s`', mysql_real_escape_string($info_hash));
    $result = mysql_query($query);
    $row = mysql_fetch_row($result);
    $complete = $row[0];
    $incomplete = $row[1];
    return '<TR BGCOLOR="#FFFFFF"><TD><A HREF="index.php?info_hash=' . $info_hash. '">' . $info_hash . '</A></TD><TD ALIGN="RIGHT">' . number_format($complete) . '</TD><TD ALIGN="RIGHT">' . number_format($incomplete) . '</TD></TR>';
}
?>
<HTML>
<HEAD>
<TITLE>Anatomic P2P Tracker based on FBT2 - BitTorrent Tracker MySQL</TITLE>
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
<BODY TEXT="#867C68" LINK="#800000" ALINK="#800000" VLINK="#800000">
<?
if(isset($_GET['info_hash']))
{
    $info_hash = $_GET['info_hash'];
    echo '<TABLE ALIGN="CENTER" WIDTH="400" CELLSPACING="1" CELLPADDING="2" BORDER="0" BGCOLOR="#867C68"><TR BGCOLOR="#EAE7E2"><TH WIDTH="30%">IP</TH><TH WIDTH="20%">Status</TH><TH WIDTH="20%">Port</TH><TH WIDTH="30%">Last Action</TH></TR>';
    // count seeds and count peers
    $query = sprintf('SELECT `ip_and_port`, `seed_or_peer`, UNIX_TIMESTAMP(timestamp) FROM `%s`' , mysql_real_escape_string($info_hash));
    $result = mysql_query($query);
    while($row = mysql_fetch_row($result))
    {
        $ip = unpack("C*", substr($row[0], 0, 4));
        $ip = $ip[1] . '.' . $ip[2] .'.' . $ip[3] . '.' . "*" ;
        $port = join('',unpack("n*", substr($row[0], 4, 2)));
        if($row[1] == "1")
        {
            $what = '<FONT COLOR="#008000"><B>seeder</B></FONT>';
        }
        else
        {
            $what = 'leecher';
        }
        echo '<TR BGCOLOR="#FFFFFF"><TD>' . $ip . '</TD><TD ALIGN="CENTER">' . $what . '</TD><TD ALIGN="RIGHT">' . $port . '</TD><TD ALIGN="RIGHT">' . number_format((time() - (int)$row[2]) / 60) . ' min ago</TD></TR>';
    }
    echo '</TABLE>';
}
else
{
?><TABLE ALIGN="CENTER" WIDTH="400" CELLSPACING="1" CELLPADDING="2" BORDER="0" BGCOLOR="#867C68">
<TR BGCOLOR="#EAE7E2">
<TH WIDTH="80%">Hash</TH>
<TH WIDTH="10%">UL</TH>
<TH WIDTH="10%">DL</TH>
</TR>
<?
$result = mysql_query("SHOW TABLE STATUS LIKE '________________________________________'");
while($row = mysql_fetch_row($result))
{
    // there should be no other reason to have a 40 byte table name
    if($row[3] == "0") // returns a string??
    {
        if(mysql_date_parser($row[11]) <= (time() - 86400))
        {
            mysql_query('DROP TABLE ' . $row[0] );
            $query = sprintf("DELETE FROM `multiseed` WHERE info_hash = '%s' ", mysql_real_escape_string(pack('H*' , $row[0])));
            @mysql_query($query);
        }
        else
        {
            echo getstat($row[0]);
        }
    }
    else
    {
        echo getstat($row[0]);
    }
}
mysql_close();
?>
</TABLE>
<?
}
?>
<TABLE ALIGN="CENTER" CELLSPACING="10" CELLPADDING="0" BORDER="0"><TR><TD ALIGN="CENTER">Anatomic P2P Tracker 0.1 RC1 based on FBT2 - Flippy's BitTorrent Tracker v2 (GPL)<BR>http://www.torrentz.com/fbt.html</TD></TR></TABLE>
</BODY>
</HTML>
