# Warning

Webpymail is still on its early development stages, it's not yet feature complete and could possibly cause damage to you data.

# Dependencies

To test webpymail you need:

  * Django 1.9.1
  * Python 3.5 (it might work with versions bellow 3.5 but I haven't tested)

# Installation

  * Get python working;

  * Choose a suitable folder and checkout webpymail source code:

```
git clone https://github.com/heldergg/webpymail.git
```

  * Install the requirements:

```
$ cd webpymail/
$ pip install -r requirements.txt
$ pip install -r requirements-optional.txt
```

  * Add the webpymail folder to your PYTHONPATH

```
$ export PYTHONPATH=`pwd`:$PYTHONPATH
```

  * Do not change the Django's settings file. Instead create the `webpymail/webpymail/local_settings.py` file according to your needs. The defaults should be enough to get you going.

```
$ touch webpymail/webpymail/local_settings.py
```

  * Edit the file servers.conf in `webpymail/config/servers.conf` and add your server. A server entry is something like:

```
[macavity]
name = Macavity
host = example.org
port = 993
ssl  = true
```

By default gmail's IMAP server is defined.

  * Define a smtp server use a `[smtp]` section. This can be done in `webpymail/config/defaults.conf` for a system wide configuration:

```
[smtp]
host   = smtp.example.com
port   = 25
user   = a_user
passwd = a_pass
security = tls
```

The security can be tls, ssl or none.

If you wish to have different configurations by server you will have to define these settings in the specific server configuration file that lives in `webpymail/config/servers/<hostname>.conf`. Take a look at the config directory README for information about configuration file precedences.

Gmail's imap SMTP server is defined in
`webpymail/config/servers/imap.gmail.com.conf`.

  * Go to the webpymail django folder and create the database:

```
$ cd webpymail
$ python manage.py migrate --run-syncdb
```

  * Start Django's web server:

```
$ python3 manage.py runserver
```

  * You can access the webmail app, just go to: http://127.0.0.1:8000/ . Login with a valid user on the IMAP server.

