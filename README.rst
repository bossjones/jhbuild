== ROS clone of jhbuild ==

This is a clone of the GNOME jhbuild project.
http://developer.gnome.org/jhbuild/
cloned from git://git.gnome.org/jhbuild


== 5 minute tutorial ==

We will do everything in one local folder, so you can clean up by deleting that::

  ~ $ mkdir jhbuild_tutorial
  ~ $ cd jhbuild_tutorial

Note the folder name is what is used in the file ``jhbuildrc.ros`` later.

Get the fork of rosbuild with one patch and a base ros moduleset and example config for this tutorial::

  jhbuild_tutorial $ git clone https://github.com/tkruse/jhbuild.git --branch=ros

Create the jhbuild binary in the local folder::

  jhbuild_tutorial $ cd jhbuild
  jhbuild $ ./autogen.sh --prefix=`pwd`/../jhbuild_install
  jhbuild $ make
  jhbuild $ make install
  jhbuild $ cd ..

Build ros_base from the definitions in the given files::

  jhbuild_tutorial $ jhbuild_install/bin/jhbuild -f jhbuild/examples/jhbuildrc.ros -m jhbuild/modulesets/ros.modules
