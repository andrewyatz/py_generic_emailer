====================
Python Batch Emailer
====================

A reimplementation of `Perl generic-emailer <https://github.com/andrewyatz/generic-emailer>`. Combine a template with a CSV of values and substitute those values into the email. It's mail-merge.

Running
=======

   poetry run emailer --input input.csv --template input.template --config conf.ini

Other command line options include
* ``--verbose`` - emit lots of messages
* ``--live`` - send emails

What does it do?
================

The purpose of this code is to

- Take in a template of an email you wish to send
- Parse a given CSV of values (with at least one column called ``email``)
- Apply a dictionary of parsed CSV values to the template
- Send the resulting plain text email to the specified address

The key point is your CSV file and template placeholders must have the same name.

Configuration
=============

Config file
-----------

Configuration is given as an ini file like the following.

    [smtp]
    host=smtp.server.com
    port=25
    secure=False
    user=Username
    password=Password

    [template.defaults]
    default=Value

    [email]
    from=email@domain.com
    subject=Subject line $name

+---------+----------+-------------------+--------------------------------------------------------------------------------------+
| Section | Variable | Data type         | Description                                                                          |
+=========+==========+===================+======================================================================================+
| smtp    | host     | URI               | Host name of the SMTP server                                                         |
| smtp    | port     | Integer           | Port of the SMTP server                                                              |
| smtp    | secure   | Boolean           | Use a secure SMTP connection                                                         |
| smtp    | user     | String            | Username for SMTP                                                                    |
| smtp    | password | String            | Password for SMTP                                                                    |
| email   | from     | Email             | Who the email is from                                                                |
| email   | subject  | String (template) | Subject line for the email. Can have Python Template variables as defined by PEP 292 |
+---------+----------+-------------------+--------------------------------------------------------------------------------------+

The only special section is **template.defaults**. These variables are made available to each template evaluation run.

Template format
---------------

Templates should follow the `Template strings <https://docs.python.org/3/library/string.html#template-strings>` format as defined by PEP 292 where substitutions are performed using ``$-`` values. Substitutions are performed using the ``substitute`` operation meaning if placeholders are missing from your input, the program will fail. The same template format can be used for the configuration subject line to customise input.

CSV format
----------

You are free to specify any kind of data for your CSV with one exception. You **MUST** provide a column called ``email``. The code will use this field as the target email address of the message.
