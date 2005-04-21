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
$time = intval((time() % 7680) / 60);
function getstat($file)
{
	global $time;
        $handle = fopen($file, "rb+");
        flock($handle, LOCK_EX);
        $x = fread($handle, filesize($file));
        $no_peers = intval(strlen($x) / 7);
        for($j=0;$j<$no_peers;$j++)
        {
                $t_peer_seed = join('', unpack("C", substr($x, $j * 7, 1)));
                if($t_peer_seed >= 128)
                {
                        $complete++;
                        $t_time = $t_peer_seed - 128;
                }
                else
                {
                        $incomplete++;
                        $t_time = $t_peer_seed;

                }
                if($time - 40 <= $t_time && $time >= $t_time || $time + 88 < $t_time)
                {
                        $new_data .= substr($x, $j * 7, 7);
                }
        }

        if($complete + $incomplete > 0)
        {
                $o .= '20:' . pack("H*", $file) . 'd8:completei' . (int)$complete . 'e10:incompletei' . (int)$incomplete . 'ee';
        }

        rewind($handle);
        ftruncate($handle, 0);
        fwrite($handle, $new_data);
        flock($handle, LOCK_UN);
        fclose($handle);
        return $o;
}


if($_GET['info_hash'])
{
        echo 'd5:filesd';
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
        if(file_exists($info_hash))
	{
	if(filesize($info_hash) == 0)
	{
		if((time() - filemtime($info_hash)) >= 86400)
			{ // 1 day of inactivity
				unlink($info_hash);
				if(file_exists("multiseed/$info_hash")){
				unlink("multiseed/$info_hash");
                        }
			// keep this hidden
			// 1 days inactive if
			}
			else
			{
			// getstat is not run so that the filemtime is not changed
			// a filesize of 0 has to have 0 seeds and 0 peers
			$o .= '20:' . pack("H*", $info_hash) . 'd8:completei' . (int)0 . 'e10:incompletei' . (int)0 . 'ee';
			}
	}
	else
	{
	echo getstat($info_hash);
        }
        die('ee');
}
}
else
{
        if(file_exists('scrape') && filemtime('scrape') > (time() - 60))
        {
                readfile('scrape');
                die();
        }
        else
        {
                $o = 'd5:filesd';
                $handle = opendir('.');
                while (false !== ($file = readdir($handle)))
                {
                        if(strlen($file) == 40)
                        {
                        if(filesize($file) == 0)
			{
			if((time() - filemtime($file)) >= 86400)
				{ // 1 day of inactivity
				unlink($file);
				if(file_exists("multiseed/$file"))
				{
				unlink("multiseed/$file");
				}
				// keep this hidden
				// 1 days inactive if
			}
			else
			{
			// getstat is not run so that the filemtime is not changed
				$o .= '20:' . pack("H*", $file) . 'd8:completei' . (int)0 . 'e10:incompletei' . (int)0 . 'ee';
			}			  
			}else{
                                $o .= getstat($file);
                               }
                        }
                }
                closedir($handle);
                $o .= 'ee';
                $handle1 = fopen('scrape', "w");
                flock($handle1, LOCK_EX);
                fwrite($handle1, $o);
                flock($handle1, LOCK_UN);
                fclose($handle1);
                die($o);
        }
}
?>
