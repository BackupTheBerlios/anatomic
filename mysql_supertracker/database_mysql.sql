# phpMyAdmin MySQL-Dump
# version 2.2.0
# http://phpwizard.net/phpMyAdmin/
# http://phpmyadmin.sourceforge.net/ (download page)
# Please execute this sql file on your mysql server
# before uploading the PHP files
# --------------------------------------------------------

#
# Table structure for table `hashes`
#

CREATE TABLE `hashes` (
  `trackerid` smallint(6) NOT NULL default '0',
  `infohash` blob NOT NULL
) TYPE=MyISAM COMMENT='This database contains the hashes and the matching trackers.';
# --------------------------------------------------------

#
# Table structure for table `strackers`
#

CREATE TABLE `strackers` (
  `url` text NOT NULL,
  `timestamp` timestamp(14) NOT NULL,
  `alive` tinyint(4) NOT NULL default '0'
) TYPE=MyISAM COMMENT='This table has supertrackers stored in it.';
# --------------------------------------------------------

#
# Table structure for table `trackers`
#

CREATE TABLE `trackers` (
  `trackerid` smallint(6) NOT NULL auto_increment,
  `url` text NOT NULL,
  `timestamp` timestamp(14) NOT NULL,
  `alive` tinyint(4) NOT NULL default '0',
  PRIMARY KEY  (`trackerid`)
) TYPE=MyISAM COMMENT='This database contains tracker urls.';