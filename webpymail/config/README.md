= Webpymail configuration files =

== Format ==

The configuration files use the python ConfigParser module, because of this they
follow the same format used on windows ini files, that is:

[section name]

option_1 = value
option_2 = value

etc...

== Files used ==

The following files are used:

* <factory base>/factory.conf - this is supposed to be the factory defaults. You
  should not change this file;
* <config base>/defaults.conf - Here you can set system wide defaults, these can
  be overridden;
* <config base>/users/<user name>.conf - here we have user specific settings
* <config base>/servers/<server name>.conf - here we have server specific
  settings;
* <config base>/system.conf - this file contains the system wide configuration
  files. For instance if you define an option 'signature' in the [identity]
  section the users will not be able to change their signatures. The settings
  here can not be overridden;

* <config base>/servers.conf - here we define the available server to connect
  to. Each server will live on it's own section.

== How the files are read ==

The files are read on the following order:

1. factory.conf
2. defaults.conf
3. users/<user name>.conf
4. servers/<server name>.conf
5. system.conf

The servers.conf file is only read when logging in.

By reading the files on this order a system admin can override the user
preferences easily.

Please consult the factory.conf file to view all the available options.

$Id$