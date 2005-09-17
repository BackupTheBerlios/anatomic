<?php
/*
    Anatomic P2P MySQL Tracker (multiseed.php)
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
include "bdecode.php";
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
if(isset($_GET['info_hash']) && isset($_GET['data']))
{
    $info_hash = $_GET['info_hash'];
    // Checks hash is ok
    if(strlen($info_hash) != 20)
    {
        $info_hash = stripcslashes($_GET['info_hash']);
    }
    if(strlen($info_hash) != 20)
    {
      die('HASHFAIL'); // that's virtually impossible
    }
    $info_hash = bin2hex($info_hash);
    $data = @gzuncompress($_GET['data']);
    if(substr($data, -1, 1) == "e" and substr($data, 0, 1) == "l")
    {
      /* this is done so that the bdecode library does not go insane and crash the server
        when it finds data that is not bencoded */
      $data = bdecode($data); // now the data is an array
      $db = mysql_connect($dbhost, $dbuname, $dbpasswd);
      mysql_select_db($dbname,$db);
      foreach($data as $peerinfo)
      {
          $iparray = explode(":",$peerinfo);
          $ip2 = $iparray[0];
          $port = $iparray[1];
          (int)$seedorpeer = $iparray[2];
          $time = $iparray[3];
          $peer_ip = explode('.', $ip2);
          $peer_ip = pack("C*", $peer_ip[0], $peer_ip[1], $peer_ip[2], $peer_ip[3]);
          $peer_port = pack("n*", (int)$port);
          // What we have here is the same as announce.php
          $query = sprintf('INSERT INTO `%s` values(%s, %s, NOW())', mysql_real_escape_string($info_hash), quote_smart($peer_ip . $peer_port), $seedorpeer);
          mysql_query($query);
          if(mysql_errno() == 1062)
          {
              $query = sprintf('UPDATE `%s` SET `timestamp` = NOW(), `seed_or_peer` = %s WHERE ip_and_port = %s', mysql_real_escape_string($info_hash), quote_smart($peer_ip . $peer_port), $seedorpeer );
              mysql_query($query);
          }
          elseif(mysql_errno() == 1146)
          {
              mysql_close();
              die('EXPIRED');
          }
      }
      mysql_close();
      die('ACCEPTED');
    }
    // Errors are pretty unlikely apart from expired







}