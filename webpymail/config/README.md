# Webpymail configuration files

WebPyMail is configured using text files.

## Format

The configuration files use the python ConfigParser module, because of this they
follow the same format used on windows ini files, that is:

```
[section name]
option_1 = value
option_2 = value
etc...
```

## Files used

The following files are used:

* `<factory base>/factory.conf` - these are supposed to be the factory defaults. You should not change this file;
* `<config base>/defaults.conf` - Here you can set system wide defaults, these can be overridden;
* `<config base>/users/<user name>@<server address>.conf` - here we have user specific settings;
* `<config base>/servers/<server name>.conf` - here we have server specific settings;
* `<config base>/system.conf` - this file contains the system wide configuration files. For instance if you define an option 'signature' in the [identity] section the users will not be able to change their signatures. The settings here can not be overridden;
* `<config base>/servers.conf` - here we define the available server to connect to. Each server will live on it's own section.

## How the files are read

The files are read on the following order:

1. `factory.conf`
2. `defaults.conf`
3. `users/<user name>.conf`
4. `servers/<server name>@<server address>.conf`
5. `system.conf`

The `servers.conf` file is only read when logging in.

By reading the files in this order a system admin can override the user
preferences easily.

Please consult the `factory.conf` file to view all the available options.

The paths to these files are defined on the `settings.py` file. You can change this paths according to your needs.

## Configuration Options

### Identities

The user can customize one or more identities. Usually these are defined on the per user configuration file in *USERCONFDIR/`<user name>@<host>.conf`*. Each identity must have its own section. The identity section must be named in the form *identity-##* where ## is an integer. Right now the available configuration parameters are:

* **user_name**
* **mail_address**

An identity configuration example might be:

```
[identity-00]
user_name       = Helder Guerreiro
mail_address    = helder@example.com

[identity-01]
user_name       = Helder Guerreiro
mail_address    = postmaster@example.com
```

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

```
[smtp]
host = smtp.googlemail.com
port = 465
user = a_user@gmail.com
passwd = XXXXXXXXXX
security = SSL
```

Or (SSL support):

```
[smtp]
host = smtp.googlemail.com
port = 465
security = SSL
use_imap_auth = True
```

Or (TLS support):

```
[smtp]
host = smtp.gmail.com
port = 587
security = TLS
use_imap_auth = True
```
