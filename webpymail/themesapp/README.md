# Themes Application

## Introduction

This application is used to allow the use of different themes in Webpymail. For this application purposes a _theme_ is nothing more than a collection of Django template files and the media files associated to it. Because we can change the templates we can go beyond a mere new styling of the application and do really different applications without the need of changing the views code at all.

Examples where this is capability is a necessity are:

* Adapt the layouts (eg. mobile phones, tablet, pcs, etc), we can adapt the CSS applied to a template but some times we want completely different controls, besides this, for this same devices some times it's necessary to minimize the template sizes, with a theme capability we can do this easily;

* This let us concentrate on the code by making a minimalistic theme and then we can let others, more competent and willing, do the layout and interface work;

The implemented theme mechanism is rather simple and easy to use.

There is a Django feature that let us provide a template name list from which the displayed template will be chosen. For instance in the `post_comment` view of `django.contrib.comments` we have:

```python
    if form.errors or preview:
        template_list = [
            # These first two exist for purely historical reasons.
            # Django v1.0 and v1.1 allowed the underscore format for
            # preview templates, so we have to preserve that format.
            "comments/%s_%s_preview.html" % (model._meta.app_label, model._meta.module_name),
            "comments/%s_preview.html" % model._meta.app_label,
            # Now the usual directory based template heirarchy.
            "comments/%s/%s/preview.html" % (model._meta.app_label, model._meta.module_name),
            "comments/%s/preview.html" % model._meta.app_label,
            "comments/preview.html",
        ]
        return render_to_response(
            template_list, {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "next": next,
            },
            RequestContext(request, {})
```

When selecting the template Django will go through the `TEMPLATE_DIRS` list and then test each template name from the list, it will choose the first one that exists (this behavior is dependent also of the selected template loaders list, in WebPyMail we only use the `filesystem` loader so this holds true). In this application we make use of this behavior to load the templates.

We transform the request for templates into lists for a given `<theme name>` and `<template name>` we'll try to find:

1. `<theme name>/<template name>`
1. `<default theme>/<template name>`
1. `<template name>`

This way we get can always fall back to existing templates and also reuse parts of other templates. For instance we may want to change only the `base` template which we extend on the other templates.

In this application we implement only enough to have the described behaviour. This would be much simpler to do by changing Django it self to support this feature.

## Components

This application has the following components:

  * `theme_name` context processor: will create a template variable named `theme` that will be made available to the templates. This variable contains the `<theme name>`.

  * Reimplemented `render_to_response` shortcut. The behaviour of the standard shortcut is changed so that if the fed `template` argument is changed to a list of template names, in the way described on the previous section of this document. Note that if the `template` argument is a list or tuple in the fist place the behaviour will not be changed.

 * A few modifications to the django's default tags `extends` and `include` in order for them to use the same template searching described above. On Django's version the `extends` tag will raise an exception if it's not the first tag on the template. We had to change this since the new tags must be loaded before being used and because of that we have to allow the `load` tag to exist befor the `extends` tag.


## Configure Themes Application

* Add the `themesapp`to the `INSTALLED_APPS` application list (the themesapp must be present in the `PYTHONPATH`);

* Optionally add the context processor to `TEMPLATE_CONTEXT_PROCESSORS`, for instance:

```python
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'themesapp.context_processors.theme_name')
```

* Define the default theme (defaults to `default`):

```python
DEFAULT_THEME = 'some_theme'
```

* Each theme must live as a sub-directory of a `TEMPLATE_DIRS` directory, the directory name of the theme must be equal to the `<theme name>`.

## Using the Themes Application

To use the themes application we have to use the `render_to_response` shortcut defined by this application, simply do:

```python
from themesapp.shortcuts import render_to_response
```

On the template side the only change is to load the newly define `loader_tags` at the beginning of the template:

```
{% load loader_tags %}
```

## Define the current theme

The current theme can be defined in several ways:

* Define DEFAULT_THEME in settings.py (Default: "default")
* Use the configuration files, section 'general', option 'theme'
* Pass the new theme in a GET request: `?theme=foo`

The chosen theme is stored on the django's session. Note that the themes engine
tries to determine the theme to use in the following order:

1. Check the GET request for `?theme=foo`;
2. Check the Django's session, key `theme`;
3. Check WebPyMail's `general → theme` configuration option.
4. Return the theme defined in `DEFAULT_THEME` defined in Django's
   `settings.py`.

The first method to return a theme name is used.
