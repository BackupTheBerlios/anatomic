<?php
/*
    Anatomic P2P FBT Peer sharing script 0.2 beta2
    Copyright (C) 2005  kunky
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
// Current Project Status: Beta
// Current Mental Status: Bored with lessons. (They know who they are(!)) Need mental challenge.
include "BDecode.php";
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
die("HASHFAIL");
}
$info_hash = bin2hex($info_hash);
if(!file_exists($info_hash) && !file_exists("./multiseed/$info_hash"))
{
die("EXPIRED");
}
$data = urldecode($_GET['data']);
$bdata = @BDecode($data);
// $bdata is an array of ip addresses:ports:time
if(!$bdata)
{
die("CORRUPT") ;
}
$handle = fopen($info_hash, "rb+");
flock($handle, LOCK_EX);
$peer_num = intval(filesize($info_hash) / 7);
$data = fread($handle, $peer_num * 7);
$peer = array();
foreach ($bdata as $ip)
{
      $iparray = explode(":",$ip);
      $ip2 = $iparray[0];
      $port = $iparray[1];
      $time = $iparray[2];
      $peer_ip = explode('.', $ip2);
      $peer_ip = pack("C*", $peer_ip[0], $peer_ip[1], $peer_ip[2], $peer_ip[3]);
      $peer_port = pack("n*", (int)$port);
      $time = pack("C", (int)$time);
      $updated = 0;
for($i=0;$i<$peer_num;$i++)
{
        if($peer_ip . $peer_port == substr($data, $i * 7 + 1, 6))
        {
                $updated = 1;
                $peer[$i] = $time . $peer_ip . $peer_port;
        }
        else
        {
                // WOOHOO I FINALLY FIXED THAT BUG
                if(($addr = substr($data, $i * 7, 7)) != false)
                {
                    $peer[$i] = $addr;
                }
        }
}
if($updated == 0)
{
        $peer[] = $time . $peer_ip . $peer_port;
        $peer_num++;
}

}
rewind($handle);
ftruncate($handle, 0);
fwrite($handle, join('', $peer), $peer_num * 7);
flock($handle, LOCK_UN);
fclose($handle);
        die("ACCEPTED");
        }

?>