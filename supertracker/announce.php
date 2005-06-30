<?php
// WARNING: THIS ANNOUNCE.PHP IS EMULATED - IT WILL NOT PERFORM THE STANDARD
// FUNCTIONS OF A SCRAPE SCRIPT
// IT DOES NOT RETURN PONG
/*
    Anatomic P2P Wrapper script for old clients (ANNOUNCE.PHP) 0.1 BETA
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
// Current Project Status: Beta
// Current Mental Status: BORED
// This script has been tested with the following clients:
// BitTorrent NewofficialCVS (burst! backend 1.1.4)
// Shadowsc0re 5.7.6 (BitTornado predecessor)
  $handle = opendir('./hashes/');
                while (false !== ($file = readdir($handle)))
                {
                        if(strlen($file) == 40)
                        {
                        if((time() - fileatime($file)) >= 172800){ // 2 days of inactivity
                        unlink($file);
                                                       }
                        }
                }
 function er($txt)
{
        die('d14:failure reason' . strlen($txt) . ':' . $txt . 'e');
}
if($_GET['compact'] == 1 && isset($_GET['port']) && isset($_GET['info_hash'])){
// compact, port and hash are only the important parts - most other bits are junk
// info_hash redundancy checks from FBT2
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
// end of hash redundancy checks
$qstring = "";
if(isset($_GET['left'])){
         $qstring .= "&left=" . $_GET['left'];
         }
if(isset($_GET['event'])){
         $qstring .= "&event=" . $_GET['event'];
         }
if(isset($_GET['numwant'])){
         $qstring .= "&numwant=" . $_GET['numwant'];
         }
if(isset($_GET['ip'])){
         $qstring .= "&ip=" . $_GET['ip'];
         }
if(file_exists("hashes/$info_hash")){
        $url = @file_get_contents("hashes/$info_hash");
          $url = $url . "?" . "compact=1&" . "port=" . $_GET['port'] . "&info_hash=" . urlencode(pack("H*",$info_hash)) . $qstring ;
            header("Location: $url", TRUE, 302);
        }
    include "BDecode.php";
    $data = @file_get_contents("trackers.dat");
    $data = BDecode($data);
     $trackers = array();
      foreach ($data as $url => $value ){
                 $result = (array_keys($value, $info_hash));
                 if($result[0] != 0){
                      $trackers[] = urldecode($url);
                                 }
                                 }
      if(isset($trackers[0]) ){

            if(count($trackers) > 1)
            {
            shuffle($trackers);
            $handle = fopen("/hashes/$info_hash", "w");
            fwrite($handle, $trackers[0]);
            fclose($handle);
            $url = $trackers[0] . "?" . "compact=1&" . "port=" . $_GET['port'] . "&info_hash=" . urlencode(pack("H*",$info_hash)) . $qstring ;
              header("Location: $url", TRUE, 302);
            }else{
                   $url = $trackers[0] . "?" . "compact=1&" . "port=" . $_GET['port'] . "&info_hash=" . urlencode(pack("H*",$info_hash)) . $qstring ;
                   header("Location: $url", TRUE, 302);
              }
              }
              else
              {
// search other supernodes
$data = @file_get_contents("strackers.dat");
$status = 0;
foreach ($data as $stracker)
{
$stracker .= "?pull=" . urlencode(pack("H*",$info_hash));
  $fp = fopen($stracker, "rb");
              $stream = "";
                 if ($fp) {
                     while( !feof( $fp ) ) {
                          $stream .= @fread($fp, 128);
                          }
                          }
                          fclose($fp);
                 $returned = BDecode($stream);
                  if($returned == FALSE){
                          continue;
                          }
                  shuffle($returned);
                  $status = 1;
                  $tracker = $returned[0];
                  break;
                   }
                  if($status == 0){
                          er('No tracker can be found for the torrent');
                          }
                 // this block is executed if a tracker was (miraculously) found
                   $handle = fopen("/hashes/$info_hash", "w");
            fwrite($handle, $tracker);
            fclose($handle);
              $url = $tracker . "?" . "compact=1&" . "port=" . $_GET['port'] . "&info_hash=" . urlencode(pack("H*",$info_hash)) . $qstring ;
                   header("Location: $url", TRUE, 302);

}

      }else{
              er('Your client does not support the compact tracker protocol. Please upgrade to the
              latest version.');
              }


?>