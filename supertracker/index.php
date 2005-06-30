<HEAD>
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
<?php

/*
    Anatomic P2P 0.1 BETA - Monitor Station
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
$serversig = $_SERVER['SERVER_SIGNATURE'];
echo "Anatomic P2P Supertracker HTML Frontend Version 0.1 BETA on: <br> $serversig.<br><br>
This script lists the status of some of the other supertrackers registered with this supertracker<BR><BR>";
include "BDecode.php";

function ping($url){
        $url = urldecode($url);
        $url .= "?ping=1";
        $pull = @file_get_contents($url);
        if($pull === "PONG"){
                return TRUE;
                }
                else
                {
                        return FALSE;

                        }
        }

$data = @file_get_contents("strackers.dat");
$data = BDecode($data);
if(is_array($data) != 1){
        die("Corrupted Tracker Data");
        }

$number = count($data);
  if($number != 0){
          $counter = 0 ;
foreach ($data as $tracker){
$counter += "1";
        $tracker = urldecode($tracker);   // might be neccessary
                if(ping($tracker) === FALSE){
                $number -= "1";
                echo "$counter.  ";
                 echo $tracker;
                 print "         NO VALID RESPONSE RECEIVED";
                 echo "<br>";
                }
                elseif(ping($tracker) === TRUE)
                {
                 echo "$counter.  ";
                 echo $tracker;
                 print "         ALIVE";
                 echo "<br>";
                        }
                }
                echo "<BR>";
                if($number === count($data)){
                        echo "<B>SYSTEM FULLY ACTIVE</B>";
                        }
                  elseif($number == 1){
                           echo "$number supertracker alive";
                                 }

                         else
                       {
                             echo  "$number supertrackers alive";
                        }
                        }
                        else
                        {
                   echo "<b>There are no supertrackers to query</b>";
                   }

?>

<br>
<p>If you want to submit a <b>tracker</b> to the current supertracker please use the form below:<p>
<form name="tpush" action="cache.php" method="get">
Tracker URL: <input name="tpush" type="text" size=60 value=""><input type="submit" value="Submit"></form>
<br>
<p>If you want to submit a <b>supertracker/(super)node</b> to the current supertracker please use the form below:<p>
<form name="push" action="cache.php" method="get">
Supertracker URL: <input name="push" type="text" size=55 value=""><input type="submit" value="Submit"></form>