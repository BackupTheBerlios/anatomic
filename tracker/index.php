<?
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
// Current Project Status: BETA
// Current Mental Status: Bored intellectually...Need mental challenge.
// Parts Coded on the London Underground

// Something Important...
// This should not have an effect on expiring torrents because no writes are made at all
function getstat($file)
{
        global $time;
        $handle = fopen($file, "rb+");
        flock($handle, LOCK_EX);
        $x = fread($handle, filesize($file));
        flock($handle, LOCK_UN);
        fclose($handle);
        $no_peers = intval(strlen($x) / 7);
        for($j=0;$j<$no_peers;$j++)
        {
                $t_peer_seed = join('', unpack("C", substr($x, $j * 7, 1)));
                if($t_peer_seed >= 128)
                {
                        $complete++;
                }
                else
                {
                        $incomplete++;
                }
        }
        return '<TR BGCOLOR="#FFFFFF"><TD><A HREF="./index.php?info_hash=' . $file . '">' . $file . '</A></TD><TD ALIGN="RIGHT">' . number_format($complete) . '</TD><TD ALIGN="RIGHT">' . number_format($incomplete) . '</TD></TR>';
}



?>
<HTML>
<HEAD>
<TITLE>Anatomic P2P 0.2 BETA Powered By FBT2 - BitTorrent Tracker</TITLE>
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
<BODY TEXT="#867C68" LINK="#800000" ALINK="#800000" VLINK="#800000">
<?
$info_hash = $_GET['info_hash'];

if($info_hash && file_exists($info_hash))
{
        echo '<TABLE ALIGN="CENTER" WIDTH="400" CELLSPACING="1" CELLPADDING="2" BORDER="0" BGCOLOR="#867C68"><TR BGCOLOR="#EAE7E2"><TH WIDTH="30%">IP</TH><TH WIDTH="20%">Status</TH><TH WIDTH="20%">Port</TH><TH WIDTH="30%">Last Action</TH></TR>';
        $handle = fopen($info_hash, "rb+");
        flock($handle, LOCK_EX);
        $x = fread($handle, filesize($info_hash));
        flock($handle, LOCK_UN);
        fclose($handle);
        $no_peers = intval(strlen($x) / 7);
        for($j=0;$j<$no_peers;$j++)
        {
                $ip = unpack("C*", substr($x, $j * 7 + 1, 4));
                $ip = $ip[1] . '.' . $ip[2] . '.' . $ip[3] . '.*';
                $port = join('', unpack("n*", substr($x, $j * 7 + 5, 2)));
                $t_peer_seed = join('', unpack("C", substr($x, $j * 7, 1)));
                if($t_peer_seed >= 128)
                {
                        $what = '<FONT COLOR="#008000"><B>seeder</B></FONT>';
                        $t_time = $t_peer_seed - 128;
                }
                else
                {
                        $what = 'leecher';
                        $t_time = $t_peer_seed;

                }
                $time = intval((time() % 7680) / 60);
                echo '<TR BGCOLOR="#FFFFFF"><TD>' . $ip . '</TD><TD ALIGN="CENTER">' . $what . '</TD><TD ALIGN="RIGHT">' . $port . '</TD><TD ALIGN="RIGHT">' . number_format($time - $t_time) . ' min ago</TD></TR>';
        }
        echo '</TABLE>';
        //echo '<TABLE ALIGN="CENTER" CELLSPACING="10" CELLPADDING="0" BORDER="0"><TR><TD><A HREF="http://www.google.com/search?q=site%3A+www.torrentz.com+' . $info_hash . '">Search for this torrent</A></TD></TR></TABLE>';
}
else
{
?><TABLE ALIGN="CENTER" WIDTH="400" CELLSPACING="1" CELLPADDING="2" BORDER="0" BGCOLOR="#867C68">
<TR BGCOLOR="#EAE7E2">
<TH WIDTH="80%">Hash</TH>
<TH WIDTH="10%">UL</TH>
<TH WIDTH="10%">DL</TH>
</TR><?
$handle = opendir('.');
while (false !== ($file = readdir($handle)))
{
        if(strlen($file) == 40)
        {
        	if(time() - filemtime($file)) >= 108000 && filesize($file) == 0){ // 1.25 days of inactivity
                        unlink($file);
                if(file_exists("multiseed/$file")){
                        unlink("multiseed/$file");
                }
                // keep this hidden
		// should not reactivate dying torrents
                }else{
                echo getstat($file);
                }
        }
}
closedir($handle);?>
</TABLE>
<?
}
?>
<TABLE ALIGN="CENTER" CELLSPACING="10" CELLPADDING="0" BORDER="0"><TR><TD ALIGN="CENTER">Anatomic P2P Powered By FBT2 - Flippy's BitTorrent Tracker v2 (GPL)<BR>http://www.torrentz.com/fbt.html</TD></TR></TABLE>
</BODY>
</HTML>
