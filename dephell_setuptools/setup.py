from ._cmd import JSONCommand


def get_cmdclass():
    """distutils commands defined in this module
    """
    return {
        'json': JSONCommand,
    }
