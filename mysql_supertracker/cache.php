<?php
/*
    Supertracker 0.1 Beta MYSQL version
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
// This makes sure that the supertracker is alive
if($_GET["ping"] == 1)
{
    die("PONG");
}
// There is no point in including common.php if all the supertracker is going to do is pong back

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
if(isset($_GET["push"]))
{
    $stracker = urldecode($_GET["push"]);
    if(substr_count($stracker, "http://") != 1)
    {
        die("The url you requested is not a valid supertracker url. Remember to include http://");
    }
    if(substr_count($stracker, "/announce") != 0)
    {
        die("This is a standard tracker not a supertracker.");
    }
    $stracker = strtolower($stracker); // to stop problems with case
    $ponged = ping($stracker);
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf("SELECT url FROM strackers WHERE url = %s", quote_smart($stracker));
    $result = mysql_query($query);
    $row = mysql_fetch_row($result) ;
    if(!$row)
    {
        if(!$ponged)
        {
            mysql_close($db);
            die("The Supertracker is not alive. Please make sure the url ends in cache.php and starts with http://.");
        }
        else
        {
            $query = sprintf("INSERT INTO strackers values(%s, NOW(), 1)", quote_smart($stracker));
            mysql_query($query);
            mysql_close($db);
            die("The Supertracker is alive and was successfully added to the database.");
        }
    }
    else
    {
        if(!$ponged)
        {
            $query = sprintf("UPDATE strackers SET timestamp = timestamp, alive = 0 WHERE url = %s", quote_smart($stracker));
            mysql_query($query);
            mysql_close($db);
            die("The Supertracker was in the database but is not alive.");
        }
        else
        {
            $query = sprintf("UPDATE strackers SET timestamp = NOW(), alive = 1 WHERE url = %s ", quote_smart($stracker));
            mysql_query($query);
            mysql_close($db);
            die("The Supertracker was in the database and is alive.");
        }
    }
}
if($_GET["strackers"])
{
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $result = mysql_query("SELECT url FROM strackers WHERE alive = 1");
    $list = "l";
    while($row = mysql_fetch_row($result))
    {
        $list .= strlen($row[0]) . ":" . $row[0]; // it bencodes the data
    }
    $list .= "e";
    mysql_close($db);
    die($list);
}
if(isset($_GET['tpush']))
{
    $tracker = urldecode($_GET['tpush']); // for those browsers which do things the official way
    if(substr_count($tracker, "http://") != 1)
    {
        die("Not a valid tracker URL. Please include http://.");
    }
    if(substr_count($tracker, "/announce") != 1)
    {
        die("Not a valid tracker URL. Please make sure the url ends in /announce.");
    }
    $tracker = strtolower($tracker);
    $ponged = ping($tracker);
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf("SELECT trackerid, timestamp FROM trackers WHERE url = %s", quote_smart($tracker));
    $result = @mysql_query($query);
    $row = @mysql_fetch_row($result) ;
    if(!$ponged)
    {
        if(!$row)
        {
            mysql_close($db);
            if($_GET["client"])
            {
                  die("5:FALSE");
            } // or else
            die("The tracker is not alive.");
        }
        else
        {
              $query = sprintf("UPDATE trackers SET timestamp = timestamp, alive = 0 WHERE trackerid = %s", quote_smart($row[0]));
              mysql_query($query);
              mysql_close($db);
              if($_GET["client"])
              {
                    die("5:FALSE");
              } // or else
              die("The tracker is not alive.");
        }
    }
    else
    {
        $request = str_replace("/announce","/request", $tracker);
        $bdata = @file_get_contents($request);
        if(!$bdata)
        {
            mysql_close($db);
            die("5:Error"); // extremely unlikely error
        }
        if(substr($bdata, -1, 1) == "e" and substr($bdata, 0, 1) == "l")
        {
            // the bdecode library goes insane otherwise
            include "bdecode.php";
            $bdata = bdecode($bdata);
            if(!$row)
            {
                $query = sprintf("INSERT INTO trackers VALUES ('',%s, NOW(), 1)", quote_smart($tracker));
                mysql_query($query);
                $query = sprintf("SELECT trackerid FROM trackers WHERE url = %s", quote_smart($tracker));
                $result = mysql_query($query);
                $row = mysql_fetch_row($result);
            }
            else
            {
                $query = sprintf("UPDATE trackers SET timestamp = NOW(), alive = 1 WHERE url = %s ", quote_smart($tracker));
                mysql_query($query);
            }
            // build insert query
            if(isset($bdata[0]))
            {
                $query = "INSERT INTO `hashes` (`trackerid`, `infohash`) VALUES ";
                foreach($bdata as $hash)
                {
                    $query .= sprintf("(%s, %s),", $row[0] ,quote_smart(pack("H*", $hash)));
                }
                $query = trim($query , ","); // the last comma is not needed
                mysql_query($query);
            }
            mysql_close($db);
            if($_GET["client"] == 1)
            {
                die("4:TRUE");
            }     // or if it is not the client
            die("Tracker Successfully added to database");
        }
        else
        {
            mysql_close($db);
        }
    }
    die();
}
if($_GET["trackers"])
{
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $result = mysql_query("SELECT url FROM trackers AND alive = 1");
    $list = "l";
    while($row = mysql_fetch_row($result))
    {
        $list .= strlen($row[0]) . ":" . $row[0]; // it bencodes the data
    }
    $list .= "e";
    mysql_close($db);
    die($list);
}
if($_GET["plant"])
{
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf("SELECT url FROM trackers WHERE alive = 1 ORDER BY rand() LIMIT 3"); // 2 more just in case
    $result = mysql_query($query);
    $url = '';
    while($row = mysql_fetch_row($result))
    {
        if(ping($row[0]))
        {
            $url = strlen($row[0]) . ":" . $row[0];
            break;
        }
    }
    mysql_close($db);
    if($url == '')
    {
        die("5:FALSE");
    }
    // or else
    die($url);
}
if(isset($_GET["multiseed"]))
{
    $toplant = (int)$_GET["multiseed"] + 2; // 2 extras just in case
    if($_GET["multiseed"] > 4)
    {
       die("7:TOOHIGH");
    }
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf("SELECT url FROM trackers WHERE alive = 1 ORDER BY rand() LIMIT %s", quote_smart($toplant)); // 2 more just in case
    $result = mysql_query($query);
    $urls = array();
    while($row = mysql_fetch_row($result))
    {
        if(ping($row[0]))
        {
            $urls[] = $row[0];
        }
         if(count($urls )== (int)$_GET["multiseed"])
        {
            break;
        }
    }
    mysql_close($db);
    if(count($urls) != (int)$_GET["multiseed"])
    {
        die("5:FALSE");
    }
    // or else
    $bdata = "l";
    foreach($urls as $one)
    {
        $bdata .= strlen($one) . ":" . $one;
    }
    $bdata .= "e";
    die($bdata);
}
if(isset($_GET['pull']))
{
     $info_hash = $_GET['pull'];
     if(strlen($info_hash) != 20)
    {
        $info_hash = stripcslashes($_GET['pull']);
    }
    if(strlen($info_hash) != 20)
    {
        die('Invalid info_hash');
    }
    $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
    mysql_select_db($dbname,$db);
    $query = sprintf("SELECT trackers.url FROM trackers, hashes WHERE hashes.trackerid = trackers.trackerid AND hashes.infohash = %s", quote_smart($info_hash));
    $result = mysql_query($query);
    $bdata = "l";
    while($row = mysql_fetch_row($result))
    {
        $bdata .= strlen($row[0]) . ":" . $row[0];
    }
    mysql_close($db);
    $bdata .= "e";
    if($bdata == "le")
    {
        die("5:FALSE");
    }
    // or else
    die($bdata);
}
?>