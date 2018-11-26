#!/usr/bin/env python3

""" This module tries to retrieve as much platform-identifying data as
    possible. It makes this information available via function APIs.

    If called from the command line, it prints the platform
    information concatenated as single string to stdout. The output
    format is useable as part of a filename.

"""
#    This module is maintained by Marc-Andre Lemburg <mal@egenix.com>.
#    If you find problems, please submit bug reports/patches via the
#    Python bug tracker (http://bugs.python.org) and assign them to "lemburg".
#
#    Still needed:
#    * more support for WinCE
#    * support for MS-DOS (PythonDX ?)
#    * support for Amiga and other still unsupported platforms running Python
#    * support for additional Linux distributions
#
#    Many thanks to all those who helped adding platform-specific
#    checks (in no particular order):
#
#      Charles G Waldman, David Arnold, Gordon McMillan, Ben Darnell,
#      Jeff Bauer, Cliff Crawford, Ivan Van Laningham, Josef
#      Betancourt, Randall Hopper, Karl Putland, John Farrell, Greg
#      Andruk, Just van Rossum, Thomas Heller, Mark R. Levinson, Mark
#      Hammond, Bill Tutt, Hans Nowak, Uwe Zessin (OpenVMS support),
#      Colin Kong, Trent Mick, Guido van Rossum, Anthony Baxter, Steve
#      Dower
#
#    History:
#
#    <see CVS and SVN checkin messages for history>
#
#    1.0.8 - changed Windows support to read version from kernel32.dll
#    1.0.7 - added DEV_NULL
#    1.0.6 - added linux_distribution()
#    1.0.5 - fixed Java support to allow running the module on Jython
#    1.0.4 - added IronPython support
#    1.0.3 - added normalization of Windows system name
#    1.0.2 - added more Windows support
#    1.0.1 - reformatted to make doc.py happy
#    1.0.0 - reformatted a bit and checked into Python CVS
#    0.8.0 - added sys.version parser and various new access
#            APIs (python_version(), python_compiler(), etc.)
#    0.7.2 - fixed architecture() to use sizeof(pointer) where available
#    0.7.1 - added support for Caldera OpenLinux
#    0.7.0 - some fixes for WinCE; untabified the source file
#    0.6.2 - support for OpenVMS - requires version 1.5.2-V006 or higher and
#            vms_lib.getsyi() configured
#    0.6.1 - added code to prevent 'uname -p' on platforms which are
#            known not to support it
#    0.6.0 - fixed win32_ver() to hopefully work on Win95,98,NT and Win2k;
#            did some cleanup of the interfaces - some APIs have changed
#    0.5.5 - fixed another type in the MacOS code... should have
#            used more coffee today ;-)
#    0.5.4 - fixed a few typos in the MacOS code
#    0.5.3 - added experimental MacOS support; added better popen()
#            workarounds in _syscmd_ver() -- still not 100% elegant
#            though
#    0.5.2 - fixed uname() to return '' instead of 'unknown' in all
#            return values (the system uname command tends to return
#            'unknown' instead of just leaving the field emtpy)
#    0.5.1 - included code for slackware dist; added exception handlers
#            to cover up situations where platforms don't have os.popen
#            (e.g. Mac) or fail on socket.gethostname(); fixed libc
#            detection RE
#    0.5.0 - changed the API names referring to system commands to *syscmd*;
#            added java_ver(); made syscmd_ver() a private
#            API (was system_ver() in previous versions) -- use uname()
#            instead; extended the win32_ver() to also return processor
#            type information
#    0.4.0 - added win32_ver() and modified the platform() output for WinXX
#    0.3.4 - fixed a bug in _follow_symlinks()
#    0.3.3 - fixed popen() and "file" command invokation bugs
#    0.3.2 - added architecture() API and support for it in platform()
#    0.3.1 - fixed syscmd_ver() RE to support Windows NT
#    0.3.0 - added system alias support
#    0.2.3 - removed 'wince' again... oh well.
#    0.2.2 - added 'wince' to syscmd_ver() supported platforms
#    0.2.1 - added cache logic and changed the platform string format
#    0.2.0 - changed the API to use functions instead of module globals
#            since some action take too long to be run on module import
#    0.1.0 - first release
#
#    You can always get the latest version of this module at:
#
#             http://www.egenix.com/files/python/platform.py
#
#    If that URL should fail, try contacting the author.


import collections
import sys, os                                                                  ###

### Globals & Constants

### System name aliasing

def system_alias(system, release, version):
    return system, release, version

### Various internal helpers

def _platform(*args):

    """ Helper to format the platform string in a filename
        compatible format e.g. "system-version-machine".
    """
    # Format the platform string
    platform = '-'.join(x.strip() for x in filter(len, args))

    # Cleanup some possible filename obstacles...
    platform = platform.replace(' ', '_')
    platform = platform.replace('/', '-')
    platform = platform.replace('\\', '-')
    platform = platform.replace(':', '-')
    platform = platform.replace(';', '-')
    platform = platform.replace('"', '-')
    platform = platform.replace('(', '-')
    platform = platform.replace(')', '-')

    # No need to report 'unknown' information...
    platform = platform.replace('unknown', '')

    # Fold '--'s and remove trailing '-'
    while 1:
        cleaned = platform.replace('--', '-')
        if cleaned == platform:
            break
        platform = cleaned
    while platform[-1] == '-':
        platform = platform[:-1]

    return platform

def architecture(executable=None, bits='', linkage=''):                         ###

    """ Queries the given executable (defaults to the Python interpreter
        binary) for various architecture information.

        Returns a tuple (bits, linkage) which contains information about
        the bit architecture and the linkage format used for the
        executable. Both values are returned as strings.

        Values that cannot be determined are returned as given by the
        parameter presets. If bits is given as '', the sizeof(pointer)
        (or sizeof(long) on Python version < 1.5.2) is used as
        indicator for the supported pointer size.

        The function relies on the system's "file" command to do the
        actual work. This is available on most if not all Unix
        platforms. On some non-Unix platforms where the "file" command
        does not exist and the executable is set to the Python interpreter
        binary defaults from _default_architecture are used.

    """
    # Use the sizeof(pointer) as default number of bits if nothing
    # else is given as default.
    if not bits:
        import struct
        try:
            size = struct.calcsize('P')
        except ValueError:                                                      ###
            # Older installations can only query longs
            size = struct.calcsize('l')
        bits = str(size*8) + 'bit'

    return bits, linkage

### Portable uname() interface

uname_result = collections.namedtuple("uname_result",
                    "system node release version machine processor")

_uname_cache = None

def uname():

    """ Fairly portable uname interface. Returns a tuple
        of strings (system, node, release, version, machine, processor)
        identifying the underlying platform.

        Note that unlike the os.uname function this also returns
        possible processor information as an additional tuple entry.

        Entries which cannot be determined are set to ''.

    """
    global _uname_cache
    no_os_uname = 0

    if _uname_cache is not None:
        return _uname_cache

    processor = ''

    # Get some infos from the builtin os.uname API...
    try:
        system, node, release, version, machine = os.uname()
    except AttributeError:
        no_os_uname = 1

    #If any unknowns still exist, replace them with ''s, which are more portable
    if system == 'unknown':
        system = ''
    if node == 'unknown':
        node = ''
    if release == 'unknown':
        release = ''
    if version == 'unknown':
        version = ''
    if machine == 'unknown':
        machine = ''
    if processor == 'unknown':
        processor = ''

    _uname_cache = uname_result(system, node, release, version,
                                machine, processor)
    return _uname_cache

### Direct interfaces to some of the uname() return values

def system():

    """ Returns the system/OS name, e.g. 'Linux', 'Windows' or 'Java'.

        An empty string is returned if the value cannot be determined.

    """
    return uname().system

def node():

    """ Returns the computer's network name (which may not be fully
        qualified)

        An empty string is returned if the value cannot be determined.

    """
    return uname().node

def release():

    """ Returns the system's release, e.g. '2.2.0' or 'NT'

        An empty string is returned if the value cannot be determined.

    """
    return uname().release

def version():

    """ Returns the system's release version, e.g. '#3 on degas'

        An empty string is returned if the value cannot be determined.

    """
    return uname().version

def machine():

    """ Returns the machine type, e.g. 'i386'

        An empty string is returned if the value cannot be determined.

    """
    return uname().machine

def processor():

    """ Returns the (true) processor name, e.g. 'amdk6'

        An empty string is returned if the value cannot be
        determined. Note that many platforms do not provide this
        information or simply return the same value as for machine(),
        e.g.  NetBSD does this.

    """
    return uname().processor


### The Opus Magnum of platform strings :-)

_platform_cache = {}

def platform(aliased=0, terse=0):

    """ Returns a single string identifying the underlying platform
        with as much useful information as possible (but no more :).

        The output is intended to be human readable rather than
        machine parseable. It may look different on different
        platforms and this is intended.

        If "aliased" is true, the function will use aliases for
        various platforms that report system names which differ from
        their common names, e.g. SunOS will be reported as
        Solaris. The system_alias() function is used to implement
        this.

        Setting terse to true causes the function to return only the
        absolute minimum information needed to identify the platform.

    """
    result = _platform_cache.get((aliased, terse), None)
    if result is not None:
        return result

    # Get uname information and then apply platform specific cosmetics
    # to it...
    system, node, release, version, machine, processor = uname()
    if machine == processor:
        processor = ''
    if aliased:
        system, release, version = system_alias(system, release, version)

    if True:                                                                    ###
        # Generic handler
        if terse:
            platform = _platform(system, release)
        else:
            bits, linkage = architecture()                                      ###
            platform = _platform(system, release, machine,
                                 processor, bits, linkage)

    _platform_cache[(aliased, terse)] = platform
    return platform

