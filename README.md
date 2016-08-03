![WebPyMail](https://raw.githubusercontent.com/heldergg/webpymail/master/logos/webpymail-logo-banner.png)

WebPyMail is a project that seeks to create a fully featured, [Python 3](https://docs.python.org/3/) and [Django](https://www.djangoproject.com/) based, webmail client.

Please note that I'm using Cyrus and Gmail to test, so if you try to use this on another kind of server the results may vary.

Bug reports and patches are welcome!

## Feature List

 * Same features as [squirrelmail](http://www.squirrelmail.org) without plugins (more or less):
    * **Folder list**:
        * :white_check_mark: Subscribed folders;
        * :white_check_mark: Expandable folder list;
        * :white_check_mark: Read/Existing number of messsages;
        * :white_medium_square: Refresh folder list;
        * :white_medium_square: Subscribe/unsubscribe IMAP folders;
        * :white_medium_square: Create, rename, move and delete IMAP folders;
    * **Message List**:
        * :white_check_mark: Paginated message list;
        * :white_check_mark: Identify the server capability and use the SORT or THREAD command, fall back to a simple view for simple servers;
        * :white_check_mark: Move messages;
        * :white_check_mark: Copy messages;
        * :white_check_mark: Mark message read;
        * :white_check_mark: Mark message unread;
        * :white_check_mark: Mark message deleted;
        * :white_check_mark: Mark message undeleted;
        * :white_check_mark: Show all messages;
        * :white_medium_square: Create interface for showing all messages (`page=all`);
    * **Message view**:
        * :white_check_mark: Show the message TEXT/PLAIN part;
        * :white_check_mark: Show the message TEXT/HTML part;
        * :white_medium_square: Ask the user for permission to see remote images (right now we have an all or nothing approach, system wide);
        * :white_medium_square: Maintain a list of allowed senders to display remote messages;
        * :white_check_mark: Show encapsulated messages;
        * :white_check_mark: Show attachments;
        * :white_check_mark: Reply, Reply All;
        * :white_check_mark: Forward, forward inline;
        * :white_check_mark: Identify URLs and render them as links
        * Identify special message parts and display them accordingly:
            * :white_medium_square: S/MIME Cryptographic Signature (APPLICATION/PKCS7-SIGNATURE);
            * MULTIPART/REPORT:
                * :white_medium_square: MESSAGE/DELIVERY-STATUS;
        * Display special in-line elements and display them accordingly:
            * :white_medium_square: PGP signatures;
    * **Compose view**:
        * :white_check_mark: Compose message in plain text;
        * :white_check_mark: Compose message in Markdown;
        * :white_medium_square: Traditional message delivery status (`Disposition-Notification-To`);
        * Alternative message delivery status (is this ethical?):
            * :white_medium_square: Create a web bug to know if the message was seen, from where and when;
            * :white_medium_square: Display this info to the user;
        * :white_check_mark: Add attachments;
        * :white_medium_square: Save message (as draft);
    * **Address book**:
        * :white_check_mark: List and manage contacts (create, edit and delete);
        * :white_check_mark: Create messages using the contacts;
        * :white_check_mark: User, server and site level address books, the user can only create/edit/delete on the user level;
        * :white_medium_square: Permissions for users to change the address books at these levels;
        * :white_medium_square: Interface to give permissions;
        * :white_medium_square: Auto save new mail addresses;

* Other features:
    * :white_check_mark: Multi server support;
    * Server admin interface (not Django's admin app):
        * :white_medium_square: Edit the configuration files;
        * :white_medium_square: Edit user permissions (address book permissions);
    * :white_check_mark: IMAP authentication back end;
    * :white_check_mark: Server list edited using the admin app;
    * :white_check_mark: Auto user creation if successfully authenticated by the IMAP server;
    * :white_check_mark: Authenticates always against the server, so no passwords on the db;
    * :white_check_mark: BODYSTRUCTURE parser;

### Possible features

* SOHO features:
    * :white_medium_square: System wide signatures, enforceable by the webmaster;
    * :white_medium_square: Ability to disable user signatures;
    * :white_medium_square: Common pool of harvested mail addresses from all the accounts, if the user chooses to make the address public every user will have access to the mail address;
    * :white_medium_square: Support for LDAP address books (read and write);
    * :white_medium_square: Support carddav address books (read and write);
    * :white_medium_square: Support for IMAP ACLs, so that a user can share his folders;
    * Message templates:
        * :white_medium_square: Message templates (including custom css);
        * :white_medium_square: Message templates with forms;
        * :white_medium_square: Allow or disallow message templates for the user;
        * :white_medium_square: Force a message template to a user;
    * :white_medium_square: Database index of messages with the ENVELOPE and BODYSTRUCTURE info;
    * :white_medium_square: Sieve filter interface;
    * :white_medium_square: Permit plugins.

# History

This is not a new project, this project was started in 2008 but, due to several
reasons, the development was stopped for a while. It was hosted at [google
code](https://code.google.com/archive/p/webpymail/).

# License

WebPyMail is licensed under the terms of the GNU General Public License Version
3. See `COPYING` for details.
