This is fork of Django
======================

Django is a high-level Python Web framework that encourages rapid development
and clean, pragmatic design. Thanks for checking it out.

All documentation is in the "docs" directory and online at
https://docs.djangoproject.com/en/stable/. If you're just getting started,
here's how we recommend you read the docs:

* First, read docs/intro/install.txt for instructions on installing Django.

* Next, work through the tutorials in order (docs/intro/tutorial01.txt,
  docs/intro/tutorial02.txt, etc.).

* If you want to set up an actual deployment server, read
  docs/howto/deployment/index.txt for instructions.

* You'll probably want to read through the topical guides (in docs/topics)
  next; from there you can jump to the HOWTOs (in docs/howto) for specific
  problems, and check out the reference (docs/ref) for gory details.

* See docs/README for instructions on building an HTML version of the docs.

Docs are updated rigorously. If you find any problems in the docs, or think
they should be clarified in any way, please take 30 seconds to fill out a
ticket here: https://code.djangoproject.com/newticket

To get more help:

* Join the #django channel on irc.freenode.net. Lots of helpful people hang out
  there. Read the archives at http://django-irc-logs.com/.

* Join the django-users mailing list, or read the archives, at
  https://groups.google.com/group/django-users.

To contribute to Django:

* Check out https://docs.djangoproject.com/en/dev/internals/contributing/ for
  information about getting involved.

To run Django's test suite:

* Follow the instructions in the "Unit tests" section of
  docs/internals/contributing/writing-code/unit-tests.txt, published online at
  https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/#running-the-unit-tests


What's changed in fork
----------------------

Original framework is beautiful, it is convenient to make sites, but not
business applications. Here we try to correct this deficiency. Many of
these developments will never be accepted in the mainline, but we hope...

Incomplete list of changes:


1. By default shall have the permissions of **"CRUD"**: "add"(C), "view"(R),
   "change"(U), "delete"(D). And all permissions are created on the project
   language specified in settings.LANGUAGE_CODE.

2. Integrated field **"JSONField"** with automatic installation type for
   different DBMS. And **"StrictJSONField"** designed to work with PostgreSQL.

3. In the model the auth.User added fields: **"last_activity"** and **"settings"**.
   This solution allows to increase the speed in business applications,
   where the user object is always present and there are a lot of things
   tied. Also, added decorator for views that need to save the last user activity.

4. Added filters **"has_perm"** & **"has_module_perms"** to check user rights directly
   in the template (contrib.auth).

5. Added **"UniqueSessionMiddleware"** in contrib.auth. Prohibited work under
   one login from multiple devices simultaneously.

6. Added a **collection of abstract models** that are in demand in our view.

7. JSONEncoder can handle objects of the pending translate.

8. Displays the username from request in the mail for admins.

9. Added demand functions for working with time in **"utils.datetimes"**.

10. Added function get_object_or_none by analogy with get_object_or_404.


