<?php
error_reporting(1);
/*
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/
if($_GET['ping'] == 1){
die("PONG");
}
           // no need for BEncode.php
          $array = "l" ;
   $handle = opendir('.');
                while (false !== ($file = readdir($handle)))
                {
                        if(strlen($file) == 40)
                        {
                        if((time() - filemtime($file)) >= 172800){ // 2 days of inactivity
                        unlink($file);
                        if(file_exists("multiseed/$file")){
                        unlink("multiseed/$file");
                        }
                        // keep this hidden
                                }else{
                                $array .= 40 . ":" . $file;
                                }
                        }
                }
                $array .= "e" ;
                echo $array;





?>