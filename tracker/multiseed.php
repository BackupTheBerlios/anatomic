<?php
/*
    Anatomic P2P FBT Peer sharing script 0.1 BETA
    Copyright (C) 2005  kunky
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
// Current Project Status: Beta
// Current Mental Status: Bored with lessons. (They know who they are(!)) Need mental challenge.
// The data format is BEncode(array( hash => array( xxx.xxx.xxx.xxx:port:$t_time, xxx... )))
include "BDecode.php";
if(isset($_GET['info_hash']) && isset($_GET['data'])){
$info_hash = $_GET['info_hash'];
        if(strlen($info_hash) != 20)
{
        $info_hash = stripcslashes($_GET['info_hash']);
}
if(strlen($info_hash) != 20)
{
                die("HASHFAIL");
}
$info_hash = bin2hex($info_hash);
if(!file_exists($info_hash)){
        die("NOPLANT");
        }
$data = $_GET['data'];
$data = @BDecode($data);
if(!$data){
        die("CORRUPT") ;
        }
foreach ($data as $ip){
        $iparray = explode(":",$ip);
        $ip2 = $iparray[0];
        $port = $iparray[1];
         $time = $iparray[2];
                $peer_ip = explode('.', $ip2);
$peer_ip = pack("C*", $peer_ip[0], $peer_ip[1], $peer_ip[2], $peer_ip[3]);
$peer_port = pack("n*", (int)$port);
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
                }
        die("ACCEPTED");
        }

?>