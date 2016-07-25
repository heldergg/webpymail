# Warning

Webpymail is still on its early development stages, it's not yet feature complete and could possibly cause damage to you data.

# Dependencies

To test webpymail you need:

  * Django 1.9.1
  * Python 3.5 (it might work with versions bellow 3.5 but I haven't tested)

# Installation

  * Get python working;
  * Install the requirements:

    pip install -r requirements.txt
    pip install -r requirements-optional.txt

  * Choose a suitable folder and checkout webpymail source code:

    git clone https://github.com/heldergg/webpymail.git

  * Add the webpymail folder to your PYTHONPATH

    cd webpymail-source
    export PYTHONPATH=`pwd`:$PYTHONPATH

  * Create the `webpymail/webpymail/local_settings.py` file according to your needs.

  * Edit the file servers.conf in `webpymail/webpymail/config/servers.conf` and add your server. A server entry must be something like:

    [macavity]

    name = Macavity
    host = example.org
    port = 993
    ssl  = true

  * Define a smtp server use a `[smtp]` section. This can be done in `webpymail/webpymail/config/defaults.conf` for a system wide configuration:

    [smtp]

    host   = smtp.example.com
    port   = 25
    user   = a_user
    passwd = a_pass
    security = tls

 The security can be tls, ssl or none.

 If you wish to have different configurations by server you will have to define these settings in the specific server configuration file that lives in `webpymail/webpymail/config/servers/<hostname>.conf`. Take a look at the next section for information about configuration file precedences.

  * Go to the webpymail django folder and create the database:

    $ cd webpymail
    $ python manage.py migrate

  * Start Django's web server:

    $ python3 manage.py runserver

  * Finally you can access the webmail app, just go to: http://127.0.0.1:8000/ . Login with a valid user on the IMAP server.

# Configuration

The client configuration is made using text files.

There are a number of configuration files:

 ** **FACTORYCONF** - this configuration file stores the factory settings, it should not be changed by the user;
 ** **DEFAULTCONF** - here we can define settings that are valid system wide and can be overridden by the user or at the server level. The settings defined here override the factory settings;
 ** **USERCONFDIR/<user name>@<host>.conf** - user settings. The settings defined here override the DEFAULTCONF settings on a per user base;
 ** **SERVERCONFDIR/<host>.conf** - server settings. The settings defined here override all the other files except for the ones defined in **SYSTEMCONF**;
 ** **SYSTEMCONF** - system wide settings. The settings defined here override all the ones defined in any other file.

Additionally we have also the configuration file *SERVERCONF* where the connection settings to the IMAP servers are defined.

The paths to these files are defined on the settings.py file. You can change this paths according to your needs.

## Configuration Options

### Identities

The user can customize one or more identities. Usually these are defined on the per user configuration file in *USERCONFDIR/`<user name>@<host>.conf`*. Each identity must have its own section. The identity section must be named in the form *identity-##* where ## is an integer. Right now the available configuration parameters are:

 * **user_name**
 * **mail_address**

An identity configuration example might be:

    [identity-00]
    user_name       = Helder Guerreiro
    mail_address    = helder@example.com

    [identity-01]
    user_name       = Helder Guerreiro
    mail_address    = postmaster@example.com

### smtp

Define the SMTP server to connect to in order to send mail. The available options are:

 * **host** - SMTP server
 * **port** - (default: 25)
 * **user** - If specified an attempt to login will be made
 * **passwd** - password for the SMTP server
 * **security** - the available options are:
   * TLS
   * SSL
   * none
 * **use_imap_auth** - (default: False) - if true the imap user/pass pair will be used to authenticate against the smtp server.

For example we may have:

    [smtp]
    host = smtp.googlemail.com
    port = 465
    user = a_user@gmail.com
    passwd = XXXXXXXXXX
    security = SSL

Or (SSL support):

    [smtp]
    host = smtp.googlemail.com
    port = 465
    security = SSL
    use_imap_auth = True

Or (TLS support):

    [smtp]
    host = smtp.gmail.com
    port = 587
    security = TLS
    use_imap_auth = True
