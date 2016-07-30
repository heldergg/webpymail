This directory is needed to store the user configuration. This path can be
changed in Django's `settings.py`. If you do so make sure the directory exists.

Each new user has a configuration file named `<email address>@<server host>`.

# Defining identities

Each user can have severall identities. Each identity is configured with:

```
[identity-00]
# You can have additional identities by adding
# [identity-##] where ## is an integer
user_name       =
mail_address    =
# Not used yet: signature       = ""
# Not used yet: use_signature   = Yes
# Not used yet: use_double_dash = Yes
# Not used yet: time_zone       = Europe/Lisbon
# Not used yet: citation_start  = ""
# Not used yet: citation_end    = ""
```

The second identity would be identified by [identity-01], and so on.
