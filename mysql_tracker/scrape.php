<?php
/*
    Anatomic P2P MySQL Tracker 0.1 Beta (scrape.php)
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
    // the first thing to do is to remove the dead users who have not said to stop
    // It removes all peers that have not replied for over 40 minutes
    $query = sprintf('DELETE FROM `%s` WHERE UNIX_TIMESTAMP(timestamp) <= %s ', mysql_real_escape_string($info_hash), time() - 2400);
    $result = mysql_query($query);
    $query = sprintf('SELECT SUM(`seed_or_peer`), COUNT(*) - SUM(`seed_or_peer`) FROM `%s`', mysql_real_escape_string($info_hash));
    $result = mysql_query($query);
    $row = mysql_fetch_row($result);
    $complete = $row[0];
    $incomplete = $row[1];
    // the way it works is that the sum of `seed_or_peer` is equal to seeds because the value for seed is 1
    $o .= '20:' . pack("H*", $info_hash) . 'd8:completei' . (int)$complete . 'e10:incompletei' . (int)$incomplete . 'ee';
    return $o;
}
if(isset($_GET['info_hash']))
{
    // this block does cleanup too
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
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    echo 'd5:filesd';
    $query = sprintf('SHOW TABLE STATUS LIKE %s', quote_smart($info_hash . '%'));
    $result = mysql_query($query);
    $ok = False;
    while($row = mysql_fetch_row($result))
    {
        if($row[3] == "0") // for some reason it returns a string
        {
            // check date of table if no modifcations have been made for 86400 seconds (i.e one day)
            if(mysql_date_parser($row[11]) <= (time() - 864000))
            {
                mysql_query('DROP TABLE IF EXISTS ' . $row[0]);
                $query = sprintf('DELETE FROM `multiseed` WHERE info_hash = %s ', mysql_real_escape_string(pack('H*' , $row[0])));
                @mysql_query($query);
            }
            else
            {
                $ok = True;
            }
            break;
        }
        else
        {
            $ok = True;
            break;
        }
    }
    if($ok)
    {
        echo getstat($info_hash);
    }
    mysql_close();
    die('ee');
}
if($wholescrape)
{
    $o = 'd5:filesd';
    // SHOW TABLES LIKE does not seem to work on some versions of MYSQL
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $result = mysql_query("SHOW TABLE STATUS LIKE '________________________________________'");
    while($row = mysql_fetch_row($result))
    {
        // there should be no other reason to have a 40 byte table name
        if($row[3] == "0") // returns a string??
        {
            if(mysql_date_parser($row[11]) <= (time() - 864000))
            {
                mysql_query('DROP TABLE IF EXISTS ' . $row[0]);
                $query = sprintf('DELETE FROM `multiseed` WHERE info_hash = %s ', mysql_real_escape_string(pack('H*' , $row[0])));
                @mysql_query($query);
            }
            else
            {
                $o .= getstat($row[0]);
            }
        }
        else
        {
            $o .= getstat($row[0]);
        }
    }
    mysql_close();
    $o .= 'ee';
    die($o);
}
else
{
    er('Please specify an info_hash.');
}

