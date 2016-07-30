![WebPyMail](https://raw.githubusercontent.com/heldergg/webpymail/master/logos/webpymail-logo-banner.png)

WebPyMail is a project that seeks to create a fully featured, [Python 3](https://docs.python.org/3/) and [Django](https://www.djangoproject.com/) based, webmail client.

Please note that I'm using Cyrus and Gmail to test, so if you try to use this on another kind of server the results may vary.

Bug reports and patches are welcome!

## Feature List

 * Same features as [squirrelmail](http://www.squirrelmail.org) without plugins (more or less):
   * Folder list:
     * Subscribed folders; *DONE*
     * Expandable folder list; *DONE*
     * Read/Existing number of messsages; *DONE*
     * Refresh folder list;
     * Subscribe/unsubscribe;
   * Message List:
     * Paginated message list; *DONE*
     * Identify the server capability and use the SORT or THREAD command, fall back to a simple view for simple servers; *DONE*
     * Move messages; *DONE*
     * Copy messages; *DONE*
     * Mark message read; *DONE*
     * Mark message unread; *DONE*
     * Mark message deleted; *DONE*
         * Mark message undeleted; *DONE*
     * Show all messages; *DONE* (Missing interface, use page=all in the folder URL)
   * Message view:
     * Show the message TEXT/PLAIN part; *DONE*
     * Show encapsulated messages; *DONE*
     * Show attachments; *DONE*
     * Reply, Reply All; *DONE*
     * Forward, forward inline; *DONE*
     * Identify URLs and render them as links *DONE* - the message should be sent through a generic filter, then we could add features at will;
   * Compose view:
     * Compose message in plain text; *DONE*
     * Compose message in restructured text;
         * Compose message in Markdown; *DONE*
     * Add attachments; *DONE*
     * Save message (as draft);
   * Address book:
         * List and manage contacts (create, edit and delete); *DONE*
     * Create messages using the contacts; *DONE*
         * User, server and site level address books, the user can only create/edit/delete on the user level; *DONE*
     * Auto save new mail addresses;
     * LDAP access (read);
     * LDAP access (write);

 * Other features:
   * Multi server support; *DONE*
   * IMAP authentication back end:
     * Server list edited using the admin app; *DONE*
     * Auto user creation if successfully authenticated by the IMAP server; *DONE*
     * Authenticates always against the server, so no passwords on the db; *DONE*
   * BODYSTRUCTURE parser; *DONE*

### Possible features

 * SOHO features:
   * System wide signatures, enforceable by the webmaster;
   * Ability to disable user signatures;
   * Common pool of harvested mail addresses from all the acounts, if the user chooses to make the address public every user will have access to the mail address;
   * Support for LDAP address books (read and write);
   * Support for IMAP ACLs, so that a user can give access to his folders;
   * Message templates;
   * Allow or disallow message templates for the user;
   * Force a message template to a user;
   * Database index of messages with the ENVELOPE and BODYSTRUCTURE info;

# History

This is not a new project, this project was started in 2008 but, due to several
reasons, the development was stopped for a while. It was hosted at [google
code](https://code.google.com/archive/p/webpymail/).

# License

WebPyMail is licensed under the terms of the GNU General Public License Version
3. See `COPYING` for details.
