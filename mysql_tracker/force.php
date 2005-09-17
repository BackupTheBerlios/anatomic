<?php
/*
    Anatomic P2P MySQL Tracker (announce.php)
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
// this is a debug script that forces a peer transfer
include 'common.php';
if(isset($_GET['info_hash']))
{
    $info_hash = $_GET['info_hash'];
    if(strlen($info_hash) != 40)
    {
        die('Invalid info hash');
    }
    $binfo_hash = pack('H*' , $info_hash); // this is the info_hash in binary
    echo 'This script forces a peer transfer (multiseed) <br />';
    echo 'The info hash of the torrent is: ' . $info_hash . '<br />';
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf('SELECT `url` FROM `multiseed` WHERE `info_hash` = \'%s\' ', mysql_real_escape_string($binfo_hash));
    $result = mysql_query($query);
    if(mysql_errno() == 1054)
    {
        die('Error: The info hash cannot be found.');
        mysql_close();
    }
    // the else is implied
    $row = mysql_fetch_row($result);
    $url = $row[0];
    $url = trim($url, "'");
    // run cleanup
    $query = sprintf('DELETE FROM `%s` WHERE UNIX_TIMESTAMP(timestamp) <= %s ', mysql_real_escape_string($info_hash), time() - 2400);
    mysql_query($query);
    // if it has changed to zero peers don't bother
    $query = sprintf('SELECT COUNT(*) FROM `%s`',  mysql_real_escape_string($info_hash));
    $result = mysql_query($query);
    $row2= mysql_fetch_row($result);
    if($row2[0] == "0")
    {
        die('Error: The torrent no longer has any peers to synchronise.');
        mysql_close();
    }
    echo "There are $row2[0] peers active on this torrent. <br />";
    echo "The tracker to synchronise with is: $url <br />";
    if((int)$row2[0] > 500)
    {
        // take a random slice instead
        $rand = @mt_rand(0, (int)$row2[0]-20);
        $query = sprintf('SELECT `ip_and_port`, UNIX_TIMESTAMP(timestamp), `seed_or_peer` FROM %s LIMIT %s,%s)', mysql_real_escape_string($info_hash), $rand, $rand + 20);
    }
    else
    {
        $query = sprintf('SELECT `ip_and_port`, UNIX_TIMESTAMP(timestamp), `seed_or_peer` FROM `%s` ORDER BY RAND() LIMIT 20', mysql_real_escape_string($info_hash));
    }
    $result = mysql_query($query);
    $peers = 'l'; // this string is going to be populated
    while($ips = mysql_fetch_row($result))
    {
        $ip = unpack("C*", substr($ips[0], 0, 4));
        $ip = $ip[1] . '.' . $ip[2] .'.' . $ip[3] . '.' . $ip[4] ;
        $port = join('',unpack("n*", substr($ips[0], 4, 2)));
        $peers .= strlen($ip . ':' . $port . ':' . $ips[2] . ':' . $ips[1]) . ':' . $ip . ':' . $port . ':' . $ips[2] . ':' . $ips[1];
    }
    $peers .= 'e';
    $url = str_replace("/announce", "/multiseed", $url);
    $url .= "?info_hash=" . urlencode(pack("H*", $info_hash)) . "&data=" . urlencode(gzcompress($peers));
    echo "The data to be sent is: $url <br />";
    $fp = fopen($url, "rb");
    $stream = "";
    if ($fp)
    {
        while( !feof( $fp ) )
        {
            $stream .= @fread($fp, 128);
        }
    }
    fclose($fp);
    echo "The response from the other tracker was: $fp";
    if($fp == "EXPIRED")
    { // keeps the single tracker torrent going
        $query = sprintf('DELETE FROM `multiseed` WHERE info_hash = %s', mysql_real_escape_string($info_hash));
        mysql_query($query);
    }
    elseif($fp == "ACCEPTED")
    {
        $query = sprintf('UPDATE `multiseed` WHERE info_hash = %s SET timestamp = NOW()' , mysql_real_escape_string($binfo_hash));
        mysql_query($query);
    }
    mysql_close();

}
else
{
die('Please include an info hash');
}
