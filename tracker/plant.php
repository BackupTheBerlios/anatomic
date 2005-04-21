<?php
error_reporting(1);
/*
FBT2 - Flippy's BitTorrent Tracker v2 (GPL)
in Anatomic P2P 0.2 BETA
http://anatomic.berlios.de/
kunky 'at' users.berlios 'dot' de
http://www.torrentz.com/fbt.html
flippy `at` ameritech `dot` net
*/
/*
    Anatomic P2P modified FBT Tracker 0.2 BETA
    Copyright (C) 2005 kunkie

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
// Current Project Status: Beta
// Current Mental Status: Bored with school. Need mental challenge.
// Parts Coded on the London Underground
function ping($url){
                $url = urldecode($url);       // To make sure that it is urldecoded
                $url .= "?ping=1";       // concatenates ?ping=1 to end
                    if(@file_get_contents($url) == "PONG"){
                                return TRUE; }
                                else {
                                return FALSE;
                                }
                                }
 function er($txt)
{
        die('d14:failure reason' . strlen($txt) . ':' . $txt . 'e');
}
 if(isset($_GET['multiplant']) && isset($_GET['url'])){
        $info_hash = $_GET["multiplant"];
         if(strlen($info_hash) != 20)
{
        $info_hash = stripcslashes($_GET['multiplant']);
}
if(strlen($info_hash) != 20)
{
        er('Invalid info_hash');
}
$info_hash = bin2hex($info_hash);
if(file_exists("multiseed/$info_hash") or file_exists($info_hash)){
        er('This torrent file has already been planted');
        }

// infohash redundancy check finished
if(substr($_GET["url"],0,7) != "http://"){
        er('Other URL is not correct');
        }
         $url = $_GET["url"];
         if(!ping($url)){
                 er('Other tracker not alive. Please Try Again');
                       }
        // or else plant as usual
        $handle = fopen($info_hash, "w");
fclose($handle);

$handle2 = fopen("multiseed/$info_hash", "w");
$times = time() . ":" . $url;
fwrite($handle2, $times);
fclose($handle2);
die("7:SUCCESS");
}

if(isset($_GET["plant"])){
// a one tracker plant
        $info_hash = $_GET['plant'];
        if(strlen($info_hash) != 20)
{
        $info_hash = stripcslashes($_GET['plant']);
}
if(strlen($info_hash) != 20)
{
        er('Invalid info_hash');
}
$info_hash = bin2hex($info_hash);
if(file_exists($info_hash))
{
        er('Torrent File already planted');

}
$handle = fopen($info_hash, "w");
fclose($handle);
die("25:File successfully planted");

}


?>