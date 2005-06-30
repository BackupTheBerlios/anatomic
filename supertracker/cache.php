<?php
/*
    Anatomic P2P Cache /(Super)node aka. superTracker 0.1 BETA
    Copyright (C) 2005  kunky

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
// Current Mental Status: Bored with school. (They know who they are(!)) Need mental challenge.
// Parts Coded in the London Underground
// Key variables
$nodemax = 20;    // Maximum supertrackers to be stored
$trackermax = 20;   // Maximum trackers to be stored
// End of Key variables

include "BDecode.php";
include "BEncode.php";
 // Returns a plain pong back to show it's alive
if($_GET['ping'] == 1){
echo "PONG";
die();
}

        function writedata($data, $filename){
                  if (!$handle = fopen($filename, 'w')) {
         echo "10:WRITEERROR";
         exit;
    }
    flock($handle, LOCK_EX);
     // flock not supported fully by Window$
    if (fwrite($handle, $data) === FALSE) {
        echo "15:NOWRITEDATABASE";
        exit;
    }
     flock($handle, LOCK_UN);
    fclose($handle); }

     // push is for sending supertrackers
   if(isset($_GET['push'])){
   $stracker = urldecode($_GET['push']);  // could possibly be encoded depending on browser
if(substr_count($stracker, "http://") != 1){
        die("Not a valid superTracker URL");
        }
         if(substr_count($stracker, "/announce") != 0){
        die("This is a standard tracker not a superTracker");
        }
        $filename = "strackers.dat";
$data = @file_get_contents($filename);
$bdata = BDecode($data);
$stracker3 = urlencode($stracker);
// This is where the code splits up - is the supertracker already known or not?
if(in_array($stracker3, $bdata)){
$search = array_search($stracker3, $bdata);  // Finds actual position of tracker URL not just a boolean value
                   if(ping($stracker) === FALSE){
                         unset($bdata[$search]);
                            $newdata = BEncode($bdata);
                         writedata($newdata, "strackers.dat");
                    die("superTracker is present in cache but inactive and so has been removed");
                   }else{
                    die("Already Present in cache and active");
                    }  // End of ping
                    } // End of in_array
                    if(count($bdata) > $nodemax){
        die("Cannot Accept Any More superTrackers");
        }
                   if(ping($stracker) === FALSE){
                           die("Supertracker did not PONG back");
                           }// or else

                $bdata[] = urlencode($stracker);

                $newdata = BEncode($bdata);

                writedata($newdata, "strackers.dat");
                die("superTracker alive and successfully added to database");

}



                function ping($url){
                $url = urldecode($url);       // To make sure that it is urldecoded
                $url .= "?ping=1";       // concatenates ?ping=1 to end
                    if(@file_get_contents($url) == "PONG"){
                                return TRUE; }
                                else {
                                return FALSE;
                                }
                                }
                     // This adds a tracker to the supertracker
                    if(isset($_GET['tpush'])){
                $tracker = urldecode($_GET['tpush']);
                $test = substr_count($tracker, "http://");
                           if(substr_count($tracker, "http://") != 1){
        die("Not a valid tracker URL");
        }
        if(substr_count($tracker, "/announce") != 1){
        die("Not a valid tracker URL");
        }
                $filename = "trackers.dat";
$data = @file_get_contents($filename);
$tdata = BDecode($data);
$tracker3 = urlencode($tracker);
if(array_key_exists($tracker3, $tdata)){
  if(ping($tracker) === FALSE){
                         unset($tdata[$tracker3]);
                           $data2 = BEncode($tdata);
                         writedata($data2, "trackers.dat");
                         if($_GET["client"] = 1)
                         {
                                 die("5:FALSE");
                                 }
                                 // or else
                    die("Tracker is present in cache but inactive and so has been removed");
                   }
                   else
                   {    if($_GET["client"] = 1)
                         {
                                 # do nothing
                                 }else{
                     echo "Tracker Already Present in cache and active<BR>";
                     }
                      $request = str_replace("/announce","/request", $tracker);
   $pdata = @file_get_contents($request);
     if($pdata === FALSE){
     if($_GET["client"] = 1)
                         {
                                 die("6:2FALSE");
                                 }
           die("No response from tracker 2nd time round. Please Try Again");
           }
       unset($tdata[$tracker3]);   // completely remove the old data and add new data
   $pdata = BDecode($pdata);
   $tdata[$tracker3] = array();
    foreach ($pdata as $hash) {
   $tdata[$tracker3][] = $hash;
   }
           $newdata = &$tdata;
 // Odd behaviour
   $newdata2 = BEncode($newdata); // BEncoding $bdata does not work

   writedata($newdata2, "trackers.dat");
   if($_GET["client"] = 1)
                         {
                                 die("4:TRUE");
                                 }

                    }
                    }
                     if(ping($tracker) === FALSE){
                             if($_GET["client"] = 1)
                         {
                                 die("5:FALSE");
                                 }
 die("Tracker Not Alive");
 }
 else
 {
 $request = str_replace("/announce","/request", $tracker);
    $pdata = @file_get_contents($request);
      if($pdata === FALSE){
      if($_GET["client"] = 1)
                         {
                                 die("5:FALSE");
                                 }
           die("No response from tracker. Please Try Again");
           }
   $pdata = BDecode($pdata);
   $tdata[$tracker3] = array();
    foreach ($pdata as $hash) {
   $tdata[$tracker3][] = $hash;
   }
           $newdata = &$tdata;
 // Odd behaviour
   $newdata3 = BEncode($newdata); // BEncoding $tdata does not work

   writedata($newdata3, "trackers.dat");
     if($_GET["client"] = 1)
                         {
                                 die("4:TRUE");
                                 }     // or if it is not the client
     die("Tracker Successfully added to database");

         }
        }
           // pull is used by the client to find out about thes tracker(s)
        if(isset($_GET['pull'])) {
           $info_hash = $_GET['pull'];
        if(strlen($info_hash) != 20)
{
        $info_hash = stripcslashes($_GET['pull']);
}
if(strlen($info_hash) != 20)
{
        die('Invalid info_hash');
}
$info_hash = bin2hex($info_hash);
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
                                $trackers = BEncode($trackers);
                                echo $trackers;
                                      }else{
echo "5:FALSE";
}

                }             // plant returns one tracker
                              if($_GET["plant"]){
                               $data = @file_get_contents("trackers.dat") ;
                        $data = BDecode($data);
                       $urls = array_keys($data);      // to do something random
                        shuffle($urls);
                     foreach ($urls as $url ){
                                 $value = $data[$url];
                       if(count($value) < $trackermax){
                               $tracker = BEncode(urldecode($url));
                               die($tracker);
                               }
                               }
                               // so if nothing is found
                               die("5:FALSE");
                               }
                                 if(isset($_GET["multiseed"])){
                                $multiseed = (int)$_GET["multiseed"];
                                 if($_GET["multiseed"] > 3){
                                  die("7:TOOHIGH");
                                  }
                         $data = @file_get_contents("trackers.dat") ;
                        $data = BDecode($data);
                       $urls = array_keys($data);      // to do something random
                        shuffle($urls);
                        $trackers = array();
                     foreach ($urls as $url ){
                     $value = $data[$url];

                       if(count($value) < $trackermax){
                              $trackers[] = urldecode($url);
                                  }
                                if(count($trackers) == $multiseed){
                                          die(BEncode($trackers));
                                           }

                               }
                               die("5:FALSE");   // so if nothing is found
                               }

                                if($_GET['trackers']){
                               $data = @file_get_contents("trackers.dat");
                               $data = BDecode($data);
                               $array = array();
                               foreach ($data as $url => $value ){
                               $array[] = urldecode($url);
                               }
                               $array = BEncode($array);
                               die($array);
                               }
                               // This is used in anaupdatesnodes.py
                                    if($_GET['strackers']){
                               $data = @file_get_contents("strackers.dat");
                               $data = BDecode($data);
                               $array = array();
                               foreach ($data as $url){

                                 $array[] = urldecode($url);

                               }
                               $array = BEncode($array);
                               echo $array;
     $random2 = array_rand($data, 1);
  $random = $data[$random2];
   // Checks a random supertracker is alive
  if(ping($random) === FALSE){
         unset($data[$random2]);
           $data = BEncode($data);
               writedata($data, "strackers.dat");
         }
                 die();
                               }









?>