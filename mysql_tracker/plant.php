<?php
//error_reporting(1);
/*
    Anatomic P2P MySQL tracker 0.1 Beta (based on FBT2)
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
function ping($url)
{
    $url .= "?ping=1";       // concatenates ?ping=1 to end
    if(@file_get_contents($url) == "PONG")
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    }
} // End of ping
// quote_smart is a security check from php.net
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
if(isset($_GET['plant']))
{
    $info_hash = $_GET['plant'];
    // a one tracker plant
    if(strlen($info_hash) != 20)
    {
       $info_hash = stripcslashes($info_hash);
    }
    if(strlen($info_hash) != 20)
    {
        er('Invalid info_hash');
    }
    $info_hash = bin2hex($info_hash);
    // set up the database
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf('CREATE TABLE `%s` (`ip_and_port` TINYBLOB NOT NULL, `seed_or_peer` TINYINT NOT NULL, `timestamp` TIMESTAMP NOT NULL , UNIQUE (ip_and_port(6))) ', mysql_real_escape_string($info_hash));
    mysql_query($query);
    if(mysql_errno() == 1050)
    {
        mysql_close();
        er('The torrent file has already been planted on the network.');
    }
    elseif(mysql_errno())
    {
        mysql_close();
        er('There was a database error: ' . mysql_error()); // will this be any use to the user???
    }
    else
    {
        mysql_close();
        die('25:File successfully planted');
    }
}
if(isset($_GET['multiplant']) && isset($_GET['url']))
{
    // more than one tracker plant
    $info_hash = $_GET["multiplant"];
    if(strlen($info_hash) != 20)
    {
        $info_hash = stripcslashes($_GET['multiplant']);
    }
    if(strlen($info_hash) != 20)
    {
        er('Invalid info_hash');
    }
    $info_hash = bin2hex($info_hash);
    // set up the database
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf('SHOW TABLE STATUS LIKE %s', quote_smart($info_hash . '%'));
    $result = @mysql_query($query);
    $row = @mysql_fetch_row($result);
    if(is_array($row))
    {
        mysql_close();
        er('This torrent file has already been planted');    
    }
    if(substr($_GET['url'],0,7) != 'http://' && substr_count($stracker, '/announce') != 1) // only http protocol and ends with /announce
    {
        mysql_close();
        er('The URL of the other tracker is not correct. Make sure http:// and /announce are included.');
    }
    $url = $_GET['url'];
    if(!ping($url))
    {
        mysql_close();
        er('Other tracker not alive. Please Try Again');
    }
    // creation of the table goes AFTER the ping
    // it is true to say that there is a LOT of pinging involved but it IS important
    $query = sprintf('CREATE TABLE `%s` (`ip_and_port` TINYBLOB NOT NULL, `seed_or_peer` TINYINT NOT NULL, `timestamp` TIMESTAMP NOT NULL , UNIQUE (ip_and_port(6))) ', mysql_real_escape_string($info_hash));
    mysql_query($query);
    $query = sprintf('INSERT INTO `multiseed` VALUES ( %s , %s ,  NOW())', quote_smart(pack('H*', $info_hash)), quote_smart($url));
    mysql_query($query);
    if(mysql_errno() == 1146)
    {
        // create the table
        // i've decided to have the info_hash in binary to save a bit of space
        mysql_query('CREATE TABLE `multiseed` (`info_hash` TINYBLOB NOT NULL, `url` TEXT NOT NULL, `timestamp` TIMESTAMP NOT NULL , UNIQUE (info_hash(20)) ');
        mysql_query($query);
       	die('7:SUCCESS');   
    }
    elseif(mysql_errno())
    {
	mysql_close();
       er('There was a database error: ' . mysql_error()); // I doubt a mysql error is any use to the user but anyway
    }
    else
    {
    	mysql_close();
  	die('7:SUCCESS');
    }
}
