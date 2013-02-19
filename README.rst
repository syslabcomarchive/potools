potools
=======

This package contains command line tools to help manage translations.

* *podiff*: Shows the differences between po files in the current subdirectory tree and their counterparts in a source repository. Only cares about msgid and msgstr, not about position in the file, comments, etc.

* *pogetnew*: Compares two po files and return all new entries that need to be translated. Output is printed to stdout, in the format as a valid po file, so that it can be sent to translator.

Installation
============

Simply run::
    
    pip install potools

or if you are using easy_install::
    
    easy_install potools

Buildout users can add the following part to their buildouts::

    [script]
    recipe = zc.recipe.egg
    eggs = potools 
