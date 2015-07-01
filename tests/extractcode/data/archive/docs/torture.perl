#!/usr/local/bin/perl
#
# testdump.pl
# This program does horribly nasty things to a directory and then
# runs a backup program on it, usually playing with the directory at
# the same time. The point is to figure out what your backup program hates.
#
# Elizabeth D. Zwicky (zwicky@erg.sri.com)
# Copyright 1991 SRI International

$testdirname = "DumpTestDir";

while ($_ = $ARGV[0],/^-/){
    shift @ARGV;
    last if /^--$/;
    /^-a/ && ($activeonly++);
}

if (!$activeonly){
    &static;
}
&active;

sub static {
    $notok = 1;
    while ( -d $testdirname && $notok){
	if (&yornloop("Can I kill the existing directory $testdirname? ")){
	    $notok = 0;
	}
	else {
	    print "Please give me another name to use for a test directory: ";
	    chop($testdirname = <STDIN>);
	}
    }
    
    if ($notok) {
	mkdir($testdirname,0755) || die "Cannot create test directory $testdirname";
    }
    
# We make an output file to keep numbers in for comparison later.
    open(STATFILE,">$testdirname/statfile")|| 
	die "Cannot create statistics file $testdirname/statfile";
    
# We make a largish, unexceptional file to slow dump down and get
# stats from...
    
    open(PLAINFILE,">$testdirname/plainfile") || 
	die "Cannot create plain file $testdirname/plainfile";
    
    for ($i = 0; $i <= 10000; $i++){
	print PLAINFILE "This is a very dull file.\n";
    }
    
    ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $blocks) =  stat PLAINFILE;
    
    print STATFILE join("|","plainfile",$dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $block), "\n";
    
    close PLAINFILE;
    
# We create a file with a very, very big hole in it.
    
    open(HOLEYFILE,">$testdirname/filewithbighole") ||
	die "Cannot create file $testdirname/filewithbighole";
    select(HOLEYFILE);
    $| = 1; #unbuffer output to HOLEYFILE;
    select (STDOUT);
    
    seek(HOLEYFILE,10240000,0);
    print HOLEYFILE "After the hole.\n";
    
    ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $blocks) =  stat HOLEYFILE;

    print STATFILE join("|","filewithbighole",$dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $block), "\n";
    
    if (!defined($blksize)){
	print "Shoot - stat doesn't provide a blocksize. What do you think the blocksize on this filesystem is? ";
	$blocksize = <STDIN>;
    }
    else{
	$blocksize = $blksize;
    }
    
    
    if ($blocks * $blocksize == $size){
	die "My holey file had no holes!";
    }
    
    close HOLEYFILE;
    
# We create a file containing what we think is one hole and one hole's
# worth of nulls, the nulls coming first...
    
    open (DECEPTIVEHOLE, ">$testdirname/deceptivehole") || 
	die "Cannot create $testdirname/deceptivehole";
    
    select(DECEPTIVEHOLE);
    $| = 1; # Unbuffer output to deceptivehole
    select(STDOUT);
    
    for ($i = 0; $i < $blksize; $i++){
	print DECEPTIVEHOLE "\000";
    }
    
    seek(DECEPTIVEHOLE, $blksize, 1);
    
    print DECEPTIVEHOLE "After the hole.\n";
    
    ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $blocks) =  stat DECEPTIVEHOLE;
    
    if ($blocks * $blocksize == $size){
	die "My deceptively holey file had no holes!";
    }
    
    print STATFILE join("|","deceptivehole",$dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blksize, $block), "\n";
    
    close(DECEPTIVEHOLE);
    
# Now for fun with filenames...
    
    mkdir("$testdirname/longfilenames",0755);
    mkdir("$testdirname/longlinks", 0755);
    
    open(LONGNAME,">$testdirname/longfilenames/1");

long:    for ($length = 2; ; $length++){	
        $fullength = length("$testdirname/longfilenames/") + $length;
	# increase length until you get ENAMETOOLONG
	close(LONGNAME);
        if ($length > length("$length($fullength)")){
          $name = 
            "$length($fullength)" 
            . ("x" x ($length - (length("$length($fullength)") + 1))) . "!";
        }
        else {
          $name =
            $length . ("s" x ($length - (length($length) + 1))) . "!";
        }
	if (open(LONGNAME,">$testdirname/longfilenames/$name")){
	    print LONGNAME "This filename is $length characters long.\n";
	    chmod(0557, "$testdirname/longfilenames/$name");
	}
	else {
	    print STDERR "First guess at max component length is " .
($length -1) . "\n";
	    last long;
	}
    }

#and, just to see if we can do it...
    
    $vlongdir = "d" x ($length - 2);
    $vlongname = $vlongdir;
    while (mkdir("$testdirname/longfilenames/$vlongdir", 0755)){
	$vlongdir = $vlongdir . "/" . $vlongname;
    }
    
    @vlongdirbits =  split("/",$vlongdir);
    pop @vlongdirbits;
    $vlongdir = join("/",@vlongdirbits);
    open(LONGNAME,">$testdirname/longfilenames/$vlongdir/1");
    chmod(0557, "$testdirname/longfilenames/$vlongdir/1");
    $! = " ";

longer:    for ($length = 2; ; $length++){	
        $fullength = length("$testdirname/longfilenames/$vlongdir/") + $length;
	# increase length until you get ENAMETOOLONG
	close(LONGNAME);
        if ($length > length("$length($fullength)")){
          $name = 
            "$length($fullength)" 
            . ("x" x ($length - (length("$length($fullength)"
) + 1))) . "!";
        }
        else {
          $name =
            $length . ("s" x ($length - (length($length) + 1))) . "!";
        }
	if (open(LONGNAME,">$testdirname/longfilenames/$vlongdir/$name")){
	    print LONGNAME "This filename is $length characters
long.\n";
            chmod(0557, "$testdirname/longfilenames/$vlongfir/$name");
	}
	else {
            print STDERR "max path length appears to be " . (length("$testdirname/longfilenames/$vlongdir/$name")
- 1) . "\n";
	    last longer;
	}
    }


# And now for horrible symlinks...

symlink("1", "$testdirname/longlinks/1");

for ($length = 2; $length <= 1025; $length++){
  $name = $length . ("x" x ($length - (length($length) + 1))) . "!";
  symlink("$name", "$testdirname/longlinks/$length");
}

# We will use odd names to simultaneously test 3 things; handling of
# bizarre characters in various positions in file and directory names,
# handling oodles  of hard links, and handling of symbolic links to
# bizarre places. I ignore error codes right and left, because I know 
# that a lot of these are ill-formed
    
    if (! -d "$testdirname/funnynames"){
	mkdir("$testdirname/funnynames", 0755) || 
	    die "Cannot create directory for weird names";
    }
    if (! -d "$testdirname/hardlinks"){
	mkdir("$testdirname/hardlinks", 0755) ||
	    die	"Cannot create directory for hard links";
    }
    if (! -d "$testdirname/softlinks"){
	mkdir("$testdirname/softlinks", 0755) ||
	    die "Cannot create directory for soft links";
    }

    foreach $pos1 (0 .. 3){
	foreach $pos2 (0 .. 7){
	    foreach $pos3 (1 .. 7){
		# we create a file with a name that has only this character
		eval "open(FUNNYNAME, \"> $testdirname/funnynames/\\$pos1$pos2$pos3\0\");";
		print FUNNYNAME "$pos1$pos2$pos3";
		close(FUNNYNAME);
		# And a hard link to it.
		eval " link (\"$testdirname/funnynames/\\$pos1$pos2$pos3\0\", \"$testdirname/hardlinks/$pos1$pos2$pos3\");";
		
		# we create a file with a name that ends in this character
		eval "open(FUNNYNAME, \">$testdirname/funnynames/ends\$pos1\$pos2\${pos3}\\$pos1$pos2$pos3\0\");";
		print FUNNYNAME "$pos1$pos2$pos3";
		close(FUNNYNAME);
		# And a hard link to it.
		eval " link (\"$testdirname/funnynames/ends\$pos1\$pos2\${pos3}\\$pos1$pos2$pos3\0\", \"$testdirname/hardlinks/ends\$pos1\$pos2\${pos3}$pos1$pos2$pos3\");";
		
		# we create a file with a name that begins with this character
		eval "open(FUNNYNAME, \">$testdirname/funnynames/\\$pos1$pos2${pos3}begins\$pos1\$pos2\$pos3\");";
		print FUNNYNAME "$pos1$pos2$pos3";
		close(FUNNYNAME);
		# And a hard link to it.
		eval " link (\"$testdirname/funnynames/\\$pos1$pos2${pos3}begins\$pos1\$pos2\$pos3\", \"$testdirname/hardlinks/$pos1$pos2${pos3}begins\$pos1\$pos2\$pos3\");";
		
		# we create a directory with this character in the middle 
		# of its name
		eval "mkdir(\"$testdirname/funnynames/\$pos1\$pos2\$pos3(\\$pos1$pos2$pos3)dir\", 0755);";
		
		# and we put 10 files in it.
		foreach $i (1..10){
		    eval "open(FUNNYNAME, \">$testdirname/funnynames/\$pos1\$pos2\$pos3(\\$pos1$pos2$pos3)dir/file$i\");";
		    close (FUNNYNAME);
		    # each with a hard link to it.
		    eval " link (\"$testdirname/funnynames/\$pos1\$pos2\$pos3(\\$pos1$pos2$pos3)dir/file$i\", \"$testdirname/hardlinks/\$pos1\$pos2\$pos3($pos1$pos2$pos3)dir-file$i\");";
		}
		
		# we create a symbolic link to this character...
		eval "symlink(\"\\$pos1$pos2$pos3\", \"$testdirname/softlinks/\$pos1\$pos2\$pos3\");";
	    }
	}
    }
    
    
    foreach $link (1..1024){
	link("$testdirname/plainfile", "$testdirname/hardlinks/plain-$link");
    }
    
# Fun with permissions
    
    open(BADPERM,">$testdirname/unreadablefile");
    print BADPERM "You can't read this.\n";
    close(BADPERM);
    chmod(000, "$testdirname/unreadablefile");
    
    mkdir("$testdirname/unreadabledirectory", 0755);
    open(BADPERM,">$testdirname/unreadabledirectory/readablefile");
    print BADPERM "You can read this.\n";
    close(BADPERM);
    chmod(000, "$testdirname/unreadabledirectory");
    
    open(BADPERM,">$testdirname/unwriteablefile");
    print BADPERM "You can't write this \n";
    close(BADPERM);
    chmod(0555, "$testdirname/unwriteablefile");
    
    mkdir("$testdirname/unwriteabledirectory", 0755);
    open(BADPERM, ">$testdirname/unwriteabledirectory/writeablefile");
    print BADPERM "You can write this.\n";
    close(BADPERM);
    chmod(0555, "$testdirname/unwriteabledirectory");
    
# And a device
    
    system "/usr/etc/mknod $testdirname/chardevice c 17 2";
    system "/usr/etc/mknod $testdirname/blockdevice b 17 4";
    
# And a named pipe
    
    system "/usr/etc/mknod $testdirname/namedpipe p";
    
    close(STATFILE);
} # End of static sub

sub active {
# Now for some action...
    
# We make a file
    open(CHANGE,">$testdirname/z.deleted");
    print CHANGE "This file was deleted after the dump began.";
    close(CHANGE);
    open (CHANGE, ">$testdirname/z.becomesdir");
    close(CHANGE);
    
    mkdir("$testdirname/z.becomesfile", 0755);
    
    open(LONGER,">$testdirname/z.zgrows");
    open(SLOWLONGER, ">$testdirname/z.slow");
    open(SHORTER,">$testdirname/z.shrinks");
    select(LONGER); $| = 1; select(STDOUT);
    select(SLOWLONGER); $| = 1; select(STDOUT);

    for $i (0..10000){
	print SHORTER ("Shrinking" x 10) . "\n";
	$shortlength = $shortlength + 91;
    } 
# This apparently redundant open insures a flush
    open(SHORTER,">$testdirname/z.shrinks");
    
    
    print STDOUT "Type a command line which will run a backup program on the dump test directory: \n";
    chop($backupcommand = <STDIN>);
    
    if ($pid = fork){
	# We are in the parent. We start the backup process here, so we can
	# kill the children that are shrinking and growing files when it 
	# finishes.
	$clockstart = time;
	$cpustart = (times)[0];
	system $backupcommand;
	$cpuend = (times)[0];
	$clockend = time;
	kill $pid;
	printf ("Backup took %.2f seconds of clock time and %.2f seconds of cpu time\n", $clockend-$clockstart, $cpuend-$cpustart);
	
    }
    elsif (defined $pid){
	# We are in child1...
	print "Child 1 \n";
	sleep 5;
	open(CHANGE, ">$testdirname/z.created");
	close(CHANGE);
	unlink("$testdirname/z.deleted");
	unlink("$testdirname/z.becomesdir");
	mkdir("$testdirname/z.becomesdir", 0755);
	rmdir("$testdirname/z.becomesfile");
	open(CHANGE, ">$testdirname/z.becomesfile");
	close(CHANGE);
	while (1){
	    print LONGER "Growing, ";
	    $shortlength--;
	    eval 'truncate(SHORTER,$shortlength);';
	    print LONGER "growing, ";
	    print SLOWLONGER "a";
	    print LONGER "grown.\n";
	}
	exit;
    }
    else {
	warn "Can't fork child: $!\n";
    }
}

sub yornloop { # this subroutine takes a single argument, a string; it
  # prints the string, reads an answer from stdin, returns 1 if the
  # answer begins with y or Y, 0 if it begins with n or N, and asks
  # again if neither is true

  local($question) = $_[0];
  local($answer) = "foo";

  while ($answer !~ /[yYnN]/){
    
    print $question;
    $answer = <STDIN>;
    if ($answer =~ /[yY]/){
      return (1);
    }
    elsif ($answer =~ /[nN]/){
      return (0);
    }
    else {
      print "Please answer \"yes\" or \"no\"\n";
    }
  }
}
