#!/usr/bin/perl
use strict;
use warnings;
use DateTime::Format::Strptime;
my $fmt = '%a %b  %d %H:%M:%S CST %Y';

my $last_time_string="";
my $time_string="";

my $parser = DateTime::Format::Strptime->new(pattern => $fmt, on_error=>'croak');

while (<STDIN>)
{
 if (/Testing @ (.*)/)
 {
  $time_string=$1;

  if($time_string ne "" && $last_time_string ne "")
  {
   my $dt1 = $parser->parse_datetime($last_time_string) or die; 
   my $dt2 = $parser->parse_datetime($time_string) or die; 
   my $diff = $dt2 - $dt1;
   print $diff->hours.":".$diff->minutes.":".$diff->seconds."\n";
  }
  $last_time_string=$time_string;
 }


}
