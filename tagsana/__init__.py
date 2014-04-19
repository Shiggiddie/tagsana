import gettext

#: Version info (major, minor, revision[, 'dev']).
version_info = (0, 0, 0, 'dev')
#: Version str
version = __version__ = ".".join(map(str, version_info))
gettext.install('tagsana')
