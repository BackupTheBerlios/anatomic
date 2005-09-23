<?php
/*
    Anatomic P2P MySQL Tracker 0.1 RC1 (announce.php)
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
// This makes sure that the tracker is alive
if($_GET["ping"] == 1)
{
    die("PONG");
}
/*
$_GET['info_hash'] = pack("H*", sha1(1));
$_GET['port'] = 6993;
$_GET['left'] = rand(0, 3);
$_GET['compact'] = 1;
if(false)
{
	$_GET['event'] = 'stopped';
}
$_GET['numwant'] = 50;
$_GET['ip'] = "123.123.123.123"; // it would be good to randomise this for debug
*/
// There is no point in including common.php and bothering about the rest if all the tracker is going to do is pong back
include "common.php";
function mysql_date_parser($indate)
{
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
function er($txt)
{
    die('d14:failure reason' . strlen($txt) . ':' . $txt . 'e');
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
if($_GET['compact'] != 1)
{
    er('This tracker requires the new compact tracker protocol. Please check your client for updates.');
}
// It is rather suprising how many clients appear without a port
if(!isset($_GET['port']))
{
    er('Please include a port.');
}
$ip = $_SERVER["REMOTE_ADDR"];
// This is to get round my ISP really but it is applicable for other isps.
if(isset($_SERVER["HTTP_X_FORWARDED_FOR"]))
{
    foreach(explode(",",$_SERVER["HTTP_X_FORWARDED_FOR"]) as $address)
    {
        $addr = ip2long(trim($address));
        if ($addr != -1 && $addr != 0)
        {
            if ($addr >= -1062731776 && $addr <= -1062666241)
            {
               // 192.168.x.x
            }
            else if ($addr >= -1442971648 && $addr <= -1442906113)
            {
               // 169.254.x.x
            }
            else if ($addr >= 167772160 && $addr <= 184549375)
            {
               // 10.x.x.x
            }
            else if ($addr >= 2130706432 && $addr <= 2147483647)
            {
               // 127.0.0.1
            }
            else if ($addr >= -1408237568 && $addr <= -1407188993)
            {
                 // 172.[16-31].x.x
            }
            else
            {
                 // Finally, we can accept it as a "real" ip address.
                 $ip = long2ip($addr);
                 break;
            }
        }
    }
}
// Not sure about this override???
if (isset($_GET["ip"]))
{
    // compact check: valid IP address:
    if (ip2long($_GET["ip"]) == -1 or ip2long($_GET["ip"]) == 0)
    {
        er('Invalid IP address given. Must be standard dotted decimal (hostnames not allowed)');
    }
    $ip = $_GET["ip"];
}
// This bit is from FBT2
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
// This is to stop the pack function being used many times (acts as anti-spoof measure instead of using original data)
$binfo_hash = pack('H*' , $info_hash);
$peer_ip = explode('.', $ip);
$peer_ip = pack("C*", $peer_ip[0], $peer_ip[1], $peer_ip[2], $peer_ip[3]);
$peer_port = pack("n*", (int)$_GET['port']);
// The peer_ip and peer_port is packed just like in the compact tracker spec
$db = mysql_connect($dbhost, $dbuname, $dbpasswd);
mysql_select_db($dbname,$db);
// SHOW TABLE STATUS LIKE does not seem to work on some versions of MYSQL
// This query loops through the tables to find the matching one and also purges it if necessary
$query = sprintf('SHOW TABLE STATUS LIKE %s', quote_smart($info_hash . '%'));
$result = mysql_query($query);
while($row = mysql_fetch_row($result))
{
    // there should be no other reason to have a 40 byte table name
    // checking if the table has no peers or seeds
    if($_GET['left'] == 0)
    {
       // a seed keeps the torrent alive
       // this is a really bad hack because the expression ($_GET['left'] != 0 ) fails
    }
    else
    {
    	if($row[3] == "0" ) 
    	{
        	if(mysql_date_parser($row[11]) <= (time() - 86400))
       		{
       		     mysql_query('DROP TABLE IF EXISTS ' . $row[0]);
      		     $query = sprintf('DELETE FROM `multiseed` WHERE info_hash = %s ', quote_smart($binfo_hash));
        	     @mysql_query($query);
       		     mysql_close();
         	     er('The torrent is dead. Nobody has accessed this torrent for two days or more.');
     		}
    	}
    }
    $found = True;
}
if(!$found)
{
    er('Please plant the torrent file on the network. The torrent may have expired.');
}
$query = sprintf('SELECT `url`, UNIX_TIMESTAMP(timestamp) FROM multiseed WHERE info_hash = %s ', quote_smart($binfo_hash));
$result = mysql_query($query);
// might not be multiseed at all so best keep it quiet with @
$row = @mysql_fetch_row($result);
if(is_array($row))
{
    if(time() - (int)$row[1] >= 900) // 15 minutes old
    {
        // run cleanup
        $query = sprintf('DELETE FROM `%s` WHERE UNIX_TIMESTAMP(timestamp) <= %s ', mysql_real_escape_string($info_hash), time() - 2400);
        $result = mysql_query($query);
        // if it has changed to zero peers don't bother
        $query = sprintf('SELECT COUNT(*) FROM `%s`',  mysql_real_escape_string($info_hash));
        $result = mysql_query($query);
        $row2= mysql_fetch_row($result);
        if((int)$row2[0] == 0)
        {
     	   // not sure why (int)$row2[0] != 0 does not work
        }
        else
        {  
            if((int)$row2[0] > 500)
            {
                // take a random slice instead
                $rand = @mt_rand(0, (int)$row2[0]-20);
                $query = sprintf('SELECT `ip_and_port`, UNIX_TIMESTAMP(timestamp), `seed_or_peer` FROM `%s` LIMIT %s,%s)', mysql_real_escape_string($info_hash), $rand, $rand + 20);
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
            $url = str_replace("/announce", "/multiseed", $row[0]);
            $url .= "?info_hash=" . urlencode(pack("H*", $info_hash)) . "&data=" . urlencode($peers);
            $fp = fopen($url, "rb");
            $stream = '';
            if ($fp)
            {
                while( !feof( $fp ) )
                {
                      $stream .= @fread($fp, 128);
                }
            }
            fclose($fp);
            if($stream == 'EXPIRED')
            { // keeps the single tracker torrent going
                $query = sprintf('DELETE FROM `multiseed` WHERE info_hash = %s', quote_smart($binfo_hash));
                mysql_query($query);
            }
            elseif($stream == 'ACCEPTED')
            {
                $query = sprintf('UPDATE `multiseed` WHERE info_hash = %s SET timestamp = NOW()' , quote_smart($binfo_hash));
                mysql_query($query);
            }
        }
    }
}
if($_GET['left'] == 0)
{
    $seedorpeer = 1;
}
else
{
    $seedorpeer = 0;
}
$query = sprintf('INSERT INTO `%s` values(%s, %s, NOW())', mysql_real_escape_string($info_hash), quote_smart($peer_ip . $peer_port), $seedorpeer);
mysql_query($query);
if(mysql_errno() == 1062)
{
    if($_GET['event'] == 'stopped')
    {
        $query = sprintf('DELETE FROM `%s` WHERE `ip_and_port` = %s' , mysql_real_escape_string($info_hash), quote_smart($peer_ip . $peer_port));
    }
    else
    {
        $query = sprintf('UPDATE `%s` SET `timestamp` = NOW(), `seed_or_peer` = %s WHERE ip_and_port = %s', mysql_real_escape_string($info_hash), $seedorpeer , quote_smart($peer_ip . $peer_port));
    }
    mysql_query($query);
}
if($_GET['event'] == 'stopped' || $_GET['numwant'] === 0)
{
    mysql_close();
    die('d8:intervali900e5:peers' . strlen('') . ':' . '' . 'e');
}
// counting rows is really quick
// code snippets from PHPBTTRACKER
$query = sprintf('SELECT COUNT(*) FROM `%s` ', mysql_real_escape_string($info_hash));
$result = mysql_query($query);
$peercount = mysql_result($result, 0,0);
// ORDER BY RAND() is a computationally expensive function
if((int)$peercount  > 500) // mysql returns a string for count()
{
    // Instead of using order by rand a slice of the table will be extracted
    $rand = @mt_rand(0, (int)$peercount-50);
    $query = sprintf('SELECT `ip_and_port` FROM `%s`  LIMIT %s,%s)', mysql_real_escape_string($info_hash), $rand, $rand + 50);
}
else
{
    $query = sprintf('SELECT `ip_and_port` FROM `%s` ORDER BY RAND() LIMIT 50 ' , mysql_real_escape_string($info_hash));
}
$result = mysql_query($query);
$return = '';
while($row = mysql_fetch_row($result))
{
    if(strlen($row[0]) == 6) // the length should equal 6 (for some reason the db may return 5)
    {
        $return .= $row[0];
    }
}
mysql_close();
die('d8:intervali1800e5:peers' . strlen($return) . ':' . $return . 'e');
?>
