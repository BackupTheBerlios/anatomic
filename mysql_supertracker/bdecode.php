<?php
//---------------------------------------------------------
// litephpBTT - lightning fast PHP based BT tracker
// bdecode.php 20050612
// "The fastest or money back guarantee"
//---------------------------------------------------------

function bdecode($data) {
	global $pos;
	
	$pos = 0;
	$length = strlen($data);
	
	while ($pos < $length)
	{
		$return[] = bdec_entry($data);
	}
	
	return count($return) ? $return[0] : $return;
}

function bdec_entry($data) {
	global $pos;
	
	switch ($data{$pos})
	{
		case 'i': // Integer
			$pos++;
			$delim_pos = strpos($data, 'e', $pos);
			$return = (int)substr($data, $pos, $delim_pos-$pos); // intval()?
			$pos = $delim_pos + 1;
			return $return;
		
		case 'l': // List
			return bdec_array($data, 'l');
		
		case 'd': // Dictionary
			return bdec_array($data, 'd');
		
		default: // String, validate using is_numeric?
			$delim_pos = strpos($data, ':', $pos);
			$str_len = substr($data, $pos, $delim_pos-$pos);
			$pos = $delim_pos + 1 + $str_len;
			return substr($data, $delim_pos+1, $str_len);
	}
}

function bdec_array($data, $mode) {
	global $pos;
	$pos++;
	
	while (true)
	{
		$type = $data{$pos};
		
		if ($type == 'e' or empty($type))
		{
			$pos++;
			break;
		}
		
		if ($mode == 'd')
		{
			$return[bdec_entry($data)] = bdec_entry($data);
		}
		else
		{
			$return[] = bdec_entry($data);
		}
	}
	
	return $return;
}

?>