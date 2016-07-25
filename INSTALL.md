For the latest version of this file go to:

http://code.google.com/p/webpymail/wiki/Installation

= Warning =
 
Webpymail is still on its early development stages, it's not yet feature complete and could possibly cause damage to you data.

= Dependencies =

To test webpymail you need:

  # Django svn
  # Python 2.5 (>= 2.6.5 for SSL SMTP server support)

= Installation =

  * Get python and django working;
  * Choose a suitable folder and checkout webpymail source code:

{{{
svn checkout http://webpymail.googlecode.com/svn/trunk/ webpymail-source
}}}

  * Add the webpymail-source dir to your PYTHONPATH

{{{
cd webpymail-source
export PYTHONPATH=`pwd`:$PYTHONPATH
}}}

  * Create or edit the webpymail/local_settings.py file according to your needs. The local_settings.py is imported from the main settings file. This way you don't have to reconfigure each time you update you svn working copy.

 I'll try to shift all the needed configurations to the configuration files.

  * Edit the file servers.conf in webpymail/config/servers.conf and add your server. A server entry must be something like:

{{{
[macavity]

name = Macavity
host = paxjulia.com
port = 993
ssl  = true
}}}

  * Define a smtp server use a [smtp] section. This can be done in webpymail/config/defaults.conf for a system wide configuration:

{{{
[smtp]

host   = smtp.example.com
port   = 25
user   = auser
passwd = apass
security = tls
}}}

 The security can be tls, ssl or none.

 If you wish to have different configurations by server you will have to define these settings in the specific server configuration file that lives in webpymail/config/servers/`<hostname>`.conf. Take a look at the next section for information about configuration file precedences.

  * Go to the webpymail dir and create the data base:

{{{
$ cd webpymail
$ python manage.py syncdb
[... snip ...]
Creating table mailapp_userprofile

You just installed Django's auth system, which means you don't have
any superusers defined.
Would you like to create one now? (yes/no): yes
Username (Leave blank to use 'helder'):
E-mail address: helder@paxjulia.com
Password:
Password (again):
Superuser created successfully.
[... snip ...]
}}}

  * Start the Django included web server:

{{{
$ python manage.py runserver
}}}

  * Finally you can access the webmail app, just go to: http://127.0.0.1:8000/ . Login with a valid user on the IMAP server.

= Configuration =

The client configuration is made using text files.

There are a number of configuration files:

 * *FACTORYCONF* - this configuration file stores the factory settings, it should not be changed by the user;
 * *DEFAULTCONF* - here we can define settings that are valid system wide and can be overridden by the user or at the server level. The settings defined here override the factory settings;
 * *USERCONFDIR/`<user name>@<host>.conf`* - user settings. The settings defined here override the DEFAULTCONF settings on a per user base;
 * *SERVERCONFDIR/`<host>.conf`* - server settings. The settings defined here override all the other files except for the ones defined in *SYSTEMCONF*;
 * *SYSTEMCONF* - system wide settings. The settings defined here override all the ones defined in any other file.

This arrangement will afford extreme flexibility when customizing the system.

Additionally we have also the configuration file *SERVERCONF* where the connection settings to the IMAP servers are defined.

The paths to these files are defined on the settings.py file. You can change this paths according to your needs.

== Configuration Options ==

=== Identities ===

The user can customize one or more identities. Usually these are defined on the per user configuration file in *USERCONFDIR/`<user name>@<host>.conf`*. Each identity must have its own section. The identity section must be named in the form *identity-##* where ## is an integer. Right now the available configuration parameters are:

 * *user_name*
 * *mail_address*

An identity configuration example might be:

{{{
[identity-00]

user_name       = Helder Guerreiro
mail_address    = helder@example.com

[identity-01]

user_name       = Helder Guerreiro
mail_address    = postmaster@example.com
}}}

=== smtp ===

Define the SMTP server to connect to in order to send mail. The available options are:

 * *host* - SMTP server
 * *port* - (default: 25)
 * *user* - If specified an attempt to login will be made
 * *passwd* - password for the SMTP server
 * *security* - the available options are:
   * TLS
   * SSL
   * none
 * *use_imap_auth* - (default: False) - if true the imap user/pass pair will be used to authenticate against the smtp server.

For example we may have:

{{{
[smtp]

host = smtp.googlemail.com
port = 465
user = a_user@gmail.com
passwd = XXXXXXXXXX
security = SSL
}}}

Or (SSL support):

{{{
[smtp]

host = smtp.googlemail.com
port = 465
security = SSL
use_imap_auth = True
}}}

Or (TLS support):

{{{
[smtp]

host = smtp.gmail.com
port = 587
security = TLS
use_imap_auth = True
}}}


$Id$
