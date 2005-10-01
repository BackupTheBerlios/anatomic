<?php
/*
    Anatomic P2P MySQL Tracker 0.1 RC1 (request.php)
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
include "common.php";
// set up the database
$db = mysql_connect($dbhost, $dbuname, $dbpasswd);
mysql_select_db($dbname,$db);
// the big long list of underscores means length of 40bytes
$result = mysql_query("SHOW TABLE STATUS LIKE '________________________________________'");
// start the list
$list = "l";
/* If a different version (to mine) of MySQL is used the results can be different for SHOW TABLE STATUS
    So, mysql_fetch_array() is used */
while($row = mysql_fetch_array($result))
{
    if($row["Rows"] == "0") // returns a string??
    {
        if(mysql_date_parser($row["Update_time"]) <= (time() - 86400))
        {
            mysql_query('DROP TABLE IF EXISTS ' . $row["Name"]);
            $query = sprintf("DELETE FROM `multiseed` WHERE info_hash = '%s' ", mysql_real_escape_string(pack('H*' , $row["Name"])));
            @mysql_query($query);
        }
        else
        {
            $list .= '40' . ':' . $row["Name"];
        }
    }
    else
    {
        $list .= '40' . ':' . $row["Name"];
    }
}
$list .= "e";
mysql_close();
die($list);

?>