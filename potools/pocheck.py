import sys
import os
import re
import polib
import logging
from potools import utils

logging.basicConfig(
            level=utils.loglevel(),
            format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

def check_untranslated():
    """%(program)s: Extract all untranslated messages from a given po file and
        write them to a new po file.
        The "Default" translation will be written into the msgstr field, or the msgid
        itself if not default is present. This can be optionally turned off.

        usage:      %(program)s input.po output.po [--noprefill]
        input.po    A po file that contains untranslated messages and potentially
                    some tranlated ones.
        output.po   The name of a po file that will be created by this script.
        --noprefill With this option you can prevent the "msgstr" field being filled
                    with the default translation.
    """
    patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)
    noprefill = False

    if len(sys.argv) < 3:
        utils.usage(sys.stderr, check_untranslated, "\nERROR: Not enough arguments")
    input = sys.argv[1]
    output = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3] == "--noprefill":
        noprefill = True

    if not os.path.isfile(input):
        utils.usage(sys.stderr, check_untranslated, "\nERROR: path to input file is not valid")

    po = polib.pofile(input)
    newpo = polib.POFile()
    # Copy header and metadata
    newpo.header = po.header
    [newpo.metadata.update({key: val}) for (key, val) in po.metadata.items()]

    # Copy all untranslated messages
    for entry in po.untranslated_entries():
        match = patt.match(entry.comment)
        # Write the "Default: " text into the msgstr. Reason: Many translators will
        # not see comments in their translation program.
        default = entry.msgid
        if match:
            default = match.group(1).replace('\n', ' ')
            if "Default:" in default:
                print "ERROR! There seems to be a duplicate Default entry for msgid '%s'" % entry.msgid
        if noprefill:
            default = u''
        newpo.append(polib.POEntry(msgid=entry.msgid, msgstr=default, occurrences=entry.occurrences,
            comment=entry.comment))

    newpo.save(output)
    sys.exit('Ok')


def check_new():
    """%(program)s: Compare two .po or .pot files and find all the entries in the
        second file that are not in the first one. These entries are then written to a
        new po file.

        usage:                  %(program)s first.po second.pot out.po
        first.po                A po/pot file with
        second.pot              A po/pot file with updated default translations (e.g. via extraction)
        out.po                  A name for the output po file
        --ignore-translated     Ignore translated entries. Only untranslated and fuzzy
                                entries will be returned.
    """
    patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)

    if len(sys.argv) < 4:
        utils.usage(sys.stderr, check_new, "\nERROR: Not enough arguments")
    elif len(sys.argv) > 5:
        utils.usage(sys.stderr, check_new, "\nERROR: Too many arguments")

    oldfile = sys.argv[1]
    if not os.path.isfile(oldfile):
        utils.usage(sys.stderr, check_new, "\nERROR: path to 'old' file is not valid")

    newfile = sys.argv[2]
    if not os.path.isfile(newfile):
        utils.usage(sys.stderr, check_new, "\nERROR: path to 'new' file is not valid")

    outfile = sys.argv[3]

    firstpo = polib.pofile(oldfile)
    secondpo = polib.pofile(newfile)
    outpo = polib.POFile()

    # Copy header and metadata
    outpo.header = secondpo.header
    [outpo.metadata.update({key: val}) for (key, val) in secondpo.metadata.items()]

    if len(sys.argv) == 5 and "--ignore-translated" in sys.argv[4]:
        entries = secondpo.untranslated_entries() + secondpo.fuzzy_entries()
    else:
        entries = secondpo

    for entry in entries:
        if entry.obsolete:
            # Ignore outcommented entries
            continue

        default= utils.get_default(entry)
        if not firstpo.find(entry.msgid):
            outpo = utils.append_entry(outpo, entry, default)

    outpo.save(outfile)
    sys.exit('Found %d entries in %s that are not in %s' % (len(outpo), newfile, oldfile))


def check_dirty():
    """%(program)s: Compare two .po or .pot files to find entries that need to be
        updated. This is done by comparing the "Default" translations.
        All entries found in this way are written to a new po file that can be sent
        to translators.

        usage:           %(program)s old.po new.pot 
        old.po           A po file that contains existing, potentially outdated translations
        new.pot          A po/pot file with updated default translations (e.g. via extraction)
        --untranslated   Optional. Specifies that untranslated entries from old.po must also be
                        included in the out.po file.
        --fuzzy          Optional. Specifies that fuzzy entries in old.po must
                        also be included in the out.po file.
        --debug          Print debug statistics.
        --output         Specify file to which contents must be written (using =), otherwise stdout is used.
        --noprefill      With this option you can prevent the "msgstr" field being filled
                         with the default translation.
    """
    include_untranslated = False
    include_fuzzy = False
    debug = False
    extra_entries = []
    files = []
    outfile = None
    noprefill = False

    for i in range(1, len(sys.argv)):
        arg = sys.argv.pop()
        if arg == "--untranslated":
            include_untranslated = True
        elif arg == "--fuzzy":
            include_fuzzy = True
        elif "--output=" in arg:
            outfile = arg.split('=')[1]
        elif arg == "--noprefill":
            noprefill = True
        elif os.path.isfile(arg):
            files.append(arg)
        else:
            utils.usage(sys.stderr, check_dirty, "\nERROR: path to file is not valid: %s" % arg)

    if len(files) != 2:
        utils.usage(sys.stderr, check_dirty, "\nERROR: Too many or too few files specified")

    newfile, oldfile = files
    oldpo = polib.pofile(oldfile)
    newpo = polib.pofile(newfile)
    outpo = polib.POFile()
            
    # Copy header and metadata
    outpo.header = newpo.header
    [outpo.metadata.update({key: val}) for (key, val) in newpo.metadata.items()]

    new_entries = 0
    changed_entries = 0

    for entry in newpo:
        if entry.obsolete:
            # Ignore commented out entries
            continue

        default_old = default_new = u''
        # fist, extract the default translation of the new (POT) file
        default_new = utils.get_default(entry)
        # string to put as translation:
        default_msgstr = noprefill and " " or default_new
        # try to find the same message in the existing po file
        target = oldpo.find(entry.msgid)
        if not target:
            # not found == new translation
            new_entries += 1
            outpo = utils.append_entry(outpo, entry, default_msgstr)
            continue 

        default_old = utils.get_default(target)
        if default_old != default_new:
            # Default value is different between the two files
            changed_entries += 1
            outpo = utils.append_entry(outpo, entry, default_msgstr)

    if include_untranslated:
        extra_entries += oldpo.untranslated_entries()
    if include_fuzzy:
        extra_entries += oldpo.fuzzy_entries()

    for entry in extra_entries:
        if entry.obsolete: 
            # Remove commented entries
            continue
        default_msgstr = noprefill and " " or utils.get_default(entry)
        outpo = utils.append_entry(outpo, entry, default_msgstr)

    if outfile:
        outpo.save(outfile)
    else:
        print outpo 

    log.debug("--------------------------------------------------------")
    log.debug("SOME STATS TO HELP WITH DOUBLE-CHECKING:")
    log.debug("In %s: %d untranslated entries and %d fuzzy entries" \
                            % ( oldfile, ),
                                len(oldpo.untranslated_entries()), 
                                len(oldpo.fuzzy_entries()))
    log.debug("In %s: %d new entries and %d changed entries" % (newfile, new_entries, changed_entries))
    log.debug("%d entries were updated" % len(outpo))
    log.debug("--------------------------------------------------------")
    sys.exit('Finished sucessfully')
    

def check_defaults():
    """%(program)s: Parses a given .po file and shouts a warning for every 
        entry that has more than one Default entry.

        usage:    %(program)s file.po
        file.po   A po to check
        --debug   Print debug statistics.
    """
    patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)

    if len(sys.argv) < 3:
        utils.usage(sys.stderr, check_defaults, u"\nERROR: Not enough arguments")
    filename = sys.argv[2]

    po = polib.pofile(filename)
    counter = 0

    for entry in po:
        counter += 1
        match = patt.match(entry.comment)
        if match:
            default = match.group(1).replace('\n', ' ')
            if "Default:" in default:
                log.error(u"Duplicate default for msgid '%s'" % entry.msgid)
        else:
            log.debug(u"No Default translation for msgid '%s'." %
                    entry.msgid)

    sys.exit('Finished, checked all %d entries.' % counter)


def pocheck():
    """ """
    if 'defaults' in sys.argv:
        return check_defaults()
    if 'dirty' in sys.argv:
        return check_dirty()
    if 'new' in sys.argv:
        return check_new()
    if 'untranslated' in sys.argv:
        return check_untranslated()
