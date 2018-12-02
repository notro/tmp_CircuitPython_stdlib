#.  Copyright (C) 2005-2010   Gregory P. Smith (greg@krypto.org)
#  Licensed to PSF under a Contributor Agreement.
#

                                                                                ###
try:                                                                            ###
    from _md5 import md5                                                        ###
except ImportError:                                                             ###
    from _pymd5 import md5                                                      ###
                                                                                ###
def new(name, data=b''):                                                        ###
    if name == 'md5':                                                           ###
        return md5(data)                                                        ###
    raise ValueError('unsupported hash type ' + name)                           ###
