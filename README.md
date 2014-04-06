extract-timemachine
===================

Apple's TimeMachine backup software produces full-system backups of OS X
machines on HFS+ volumes. These backups can be restored by OS X machines;
however, no official software exists to extract the backup image from a non-OS
X operating system.

Linux is capable of mounting HFS+ volumes (at least in read-only mode), but its
view of TimeMachine backups is muddled by the backups' use of directory
hardlinks.

This script is designed to extract a full image of a TimeMachine backup
painlessly. It can be used as follows (assuming /dev/sdb2 is the HFS+ partition
on your TimeMachine backup drive):

$ ./extract.sh /dev/sdb2 my-mac-name /tmp/backup-restore

History
=======

This script was hacked together on 2014-04-05 by Chris Fallin
<cfallin@c1f.net>. I developed this after experiencing general flakiness on a
four-year-old OS X laptop, deciding to migrate to a new (non-OS X) machine, and
realizing that my backup would need some un-munging to be readable.

I hereby release this script into the public domain.
