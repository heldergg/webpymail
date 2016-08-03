![WebPyMail](https://raw.githubusercontent.com/heldergg/webpymail/master/logos/webpymail-logo-banner.png)

WebPyMail is a project that seeks to create a fully featured, [Python 3](https://docs.python.org/3/) and [Django](https://www.djangoproject.com/) based, webmail client.

Please note that I'm using Cyrus and Gmail to test, so if you try to use this on another kind of server the results may vary.

Bug reports and patches are welcome!

## Feature List

 * Same features as [squirrelmail](http://www.squirrelmail.org) without plugins (more or less):
    * **Folder list**:
        * Subscribed folders; :+1:
        * Expandable folder list; :+1:
        * Read/Existing number of messsages; :+1:
        * Refresh folder list;
        * Subscribe/unsubscribe IMAP folders;
        * Create, rename, move and delete IMAP folders;
    * **Message List**:
        * Paginated message list; :+1:
        * Identify the server capability and use the SORT or THREAD command, fall back to a simple view for simple servers; :+1:
        * Move messages; :+1:
        * Copy messages; :+1:
        * Mark message read; :+1:
        * Mark message unread; :+1:
        * Mark message deleted; :+1:
        * Mark message undeleted; :+1:
        * Show all messages; :+1:
        * Create interface for showing all messages (`page=all`);
    * **Message view**:
        * Show the message TEXT/PLAIN part; :+1:
        * Show the message TEXT/HTML part; :+1:
        * Ask the user for permission to see remote images (right now we have an all or nothing approach, system wide);
        * Maintain a list of allowed senders to display remote messages;
        * Show encapsulated messages; :+1:
        * Show attachments; :+1:
        * Reply, Reply All; :+1:
        * Forward, forward inline; :+1:
        * Identify URLs and render them as links :+1:
        * Identify special message parts and display them accordingly:
            * S/MIME Cryptographic Signature (APPLICATION/PKCS7-SIGNATURE);
            * MULTIPART/REPORT:
                * MESSAGE/DELIVERY-STATUS;
        * Display special in-line elements and display them accordingly:
            * PGP signatures;
    * **Compose view**:
        * Compose message in plain text; :+1:
        * Compose message in Markdown; :+1:
        * Traditional message delivery status (`Disposition-Notification-To`);
        * Alternative message delivery status (is this ethical?):
            * Create a web bug to know if the message was seen, from where and
              when;
            * Display this info to the user;
        * Add attachments; :+1:
        * Save message (as draft);
    * **Address book**:
        * List and manage contacts (create, edit and delete); :+1:
        * Create messages using the contacts; :+1:
        * User, server and site level address books, the user can only create/edit/delete on the user level; :+1:
        * Permissions for users to change the address books at these levels;
        * Interface to give permissions;
        * Auto save new mail addresses;

* Other features:
    * Multi server support; :+1:
    * Server admin interface (not Django's admin app):
        * Edit the configuration files;
        * Edit user permissions (address book permissions);
    * IMAP authentication back end:
    * Server list edited using the admin app; :+1:
    * Auto user creation if successfully authenticated by the IMAP server; :+1:
    * Authenticates always against the server, so no passwords on the db; :+1:
    * BODYSTRUCTURE parser; :+1:

### Possible features

* SOHO features:
    * System wide signatures, enforceable by the webmaster;
    * Ability to disable user signatures;
    * Common pool of harvested mail addresses from all the accounts, if the user chooses to make the address public every user will have access to the mail address;
    * Support for LDAP address books (read and write);
    * Support carddav address books (read and write);
    * Support for IMAP ACLs, so that a user can share his folders;
    * Message templates:
        * Message templates (including custom css);
        * Message templates with forms;
        * Allow or disallow message templates for the user;
        * Force a message template to a user;
    * Database index of messages with the ENVELOPE and BODYSTRUCTURE info;
    * Sieve filter interface;
    * Permit plugins.

# History

This is not a new project, this project was started in 2008 but, due to several
reasons, the development was stopped for a while. It was hosted at [google
code](https://code.google.com/archive/p/webpymail/).

# License

WebPyMail is licensed under the terms of the GNU General Public License Version
3. See `COPYING` for details.
