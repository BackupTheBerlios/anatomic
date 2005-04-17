<?
error_reporting(1);
/*
FBT2 - Flippy's BitTorrent Tracker v2 (GPL)
http://www.torrentz.com/fbt.html
flippy `at` ameritech `dot` net

in Anatomic P2P 0.1 BETA
http://anatomic.berlios.de/
kunky `at` mail.berlios `dot` de

    Anatomic P2P modified FBT Tracker 0.1 BETA
    Copyright (C) 2005 Kunkie
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
// Current Project Status: Beta
// Current Mental Status: Bored.
// Parts Coded on the London Underground
// Simulator of a BT client (for debug only)
// This tracker has been modified to use $_SERVER["HTTP_X_FORWARDED_FOR"]
// and $_GET['ip']. It also supports peer sharing
/*
$_GET['info_hash'] = pack("H*", sha1(rand(0, 1)));
$_GET['port'] = rand(20, 120);
$_GET['left'] = rand(0, 3);
$_GET['compact'] = 1;
if(false)
{
        $_GET['event'] = 'stopped';
}
$_GET['numwant'] = 50;
*/
if($_GET['ping'] == 1){
die("PONG");
}

// Code from PHPBTTRACKER

$ip = $_SERVER["REMOTE_ADDR"];

if (isset($_SERVER["HTTP_X_FORWARDED_FOR"]))
        {
      foreach(explode(",",$_SERVER["HTTP_X_FORWARDED_FOR"]) as $address)
      {
                $addr = ip2long(trim($address));

                if ($addr != -1)
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

        if (isset($_GET["ip"]))
        {
                // compact check: valid IP address:
                if (ip2long($_GET["ip"]) == -1)
                        er("Invalid IP address given. Must be standard dotted decimal (hostnames not allowed)");
                $ip = long2ip($_GET["ip"]);
        }

function er($txt)
{
        die('d14:failure reason' . strlen($txt) . ':' . $txt . 'e');
}
if($_GET['compact'] != 1)
{
        er('This tracker requires new tracker protocol. Please check your client for updates. Latest Generic, BitTornado or Azureus client recommended.');
}

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

 if(!file_exists($info_hash))
{
        er("Please plant the torrent file on the Network. Torrent may be dead by now.");

}
if((time() - filemtime($info_hash)) >= 172800 && $_GET['left'] != 0){ // seeds keep the torrent going
                unlink($info_hash);
        if(file_exists("multiseed/$info_hash")){
                unlink("multiseed/$info_hash");
                }
        er("Torrent is dead. Nobody has accessed this torrent for two days or more. ");
        }
  // Peer sharing code starts here
  if(file_exists("multiseed/$info_hash")){   // checks to see if multiseed file is present
  $data = @file_get_contents("multiseed/$info_hash");  // reads data from multiseed file
   $data2 = explode(":",$data, 2); // $data2[0] is the timestamp
   if((time() - (int)$data2[0]) >= 900){  // every 15 mins
       // THIS CODE REMOVES DYING PEERS
      $time = intval((time() % 7680) / 60);
         $handle = fopen($info_hash, "rb+");
            flock($handle, LOCK_EX);
        $x = fread($handle, filesize($info_hash));
        $no_peers = intval(strlen($x) / 7);
        for($j=0;$j<$no_peers;$j++)
        {
                $t_peer_seed = join('', unpack("C", substr($x, $j * 7, 1)));
                if($t_peer_seed >= 128)
                {
                           $t_time = $t_peer_seed - 128;
                }
                else
                {
                        $t_time = $t_peer_seed;

                }
                if($time - 40 <= $t_time && $time >= $t_time || $time + 88 < $t_time)
                {
                        $new_data .= substr($x, $j * 7, 7);
                }
        }
        rewind($handle);
        ftruncate($handle, 0);
        fwrite($handle, $new_data);
        flock($handle, LOCK_UN);
        fclose($handle);

     require("BEncode.php"); // I cannot avoid it :-(.  I am a lazy coder
         $handle2 = fopen($info_hash, "rb+");
        flock($handle2, LOCK_EX);
        $x = fread($handle2, filesize($info_hash));
        flock($handle2, LOCK_UN);
        fclose($handle2);
         $no_peers = intval(strlen($x) / 7);
          if($no_peers != 0){
              $peers = array();
          for($j=0;$j<$no_peers;$j++)
        {

                $ip = unpack("C*", substr($x, $j * 7 + 1, 4));
                $ip = $ip[1] . '.' . $ip[2] . '.' . $ip[3] . '.' . $ip[4];
                $tempdata = $ip;
                $port = join('', unpack("n*", substr($x, $j * 7 + 5, 2)));
                $tempdata .= ':' . $port;
                $t_peer_seed = join('', unpack("C", substr($x, $j * 7, 1)));
                $tempdata .= ':' . $t_peer_seed ;

                                   $peers[] = $tempdata;

                }
                if(count($peers) < 20){
                 shuffle($peers);
                }else{
                        $peers = array_rand($peers, 20);
                        }
                        $peers = BEncode($peers);
                        $url = str_replace("announce", "multiseed", $data2[1]);
               $url .= "?info_hash=" . urlencode(pack("H*", $info_hash)) . "&data=" . urlencode($peers);
        $fp = fopen($url, "rb");
              $stream = "";
                 if ($fp) {
                     while( !feof( $fp ) ) {
                          $stream .= @fread($fp, 128);
                          }
                          }
                          fclose($fp);

                        $minfo = fopen("multiseed/$info_hash", "rb+");
                        ftruncate($minfo, 0);
                        $times = time() . ":" . $data2[1];
                        fwrite($minfo, $times);
                         fclose($minfo);

        }else{
              // do nothin'
                        }

     }
     }
  // Peer sharing code ends here





$peer_ip = explode('.', $ip);
$peer_ip = pack("C*", $peer_ip[0], $peer_ip[1], $peer_ip[2], $peer_ip[3]);
$peer_port = pack("n*", (int)$_GET['port']);
$time = intval((time() % 7680) / 60);
if($_GET['left'] == 0)
{
        $time += 128;
}
$time = pack("C", $time);

$handle = fopen($info_hash, "rb+");
flock($handle, LOCK_EX);
$peer_num = intval(filesize($info_hash) / 7);
$data = fread($handle, $peer_num * 7);
$peer = array();
$updated = false;
for($i=0;$i<$peer_num;$i++)
{
        if($peer_ip . $peer_port == substr($data, $i * 7 + 1, 6))
        {
                $updated = true;
                if($_GET['event'] == 'stopped')
                {
                        $peer_num--;
                }
                else
                {
                        $peer[$i] = $time . $peer_ip . $peer_port;
                }

        }
        else
        {
                $peer[$i] = substr($data, $i * 7, 7);
        }
}
if($updated == false)
{
        $peer[] = $time . $peer_ip . $peer_port;
        $peer_num++;
}

rewind($handle);
ftruncate($handle, 0);
fwrite($handle, join('', $peer), $peer_num * 7);
flock($handle, LOCK_UN);
fclose($handle);

if($_GET['event'] == 'stopped' || $_GET['numwant'] === 0)
{
        $o .= '';
}
else
{
        if($peer_num > 50)
        {
                $key = array_rand ($peer, 50);
                foreach($key as $val)
                {
                        $o .= substr($peer[$val], 1, 6);
                }
        }
        else
        {
                for($i=0;$i<$peer_num;$i++)
                {
                        $o .= substr($peer[$i], 1, 6);
                }
        }
}

die('d8:intervali1800e5:peers' . strlen($o) . ':' . $o . 'e');



?>
