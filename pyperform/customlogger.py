__author__ = 'clobo'

import logging


class CustomLogLevel(object):

    def __init__(self, level, name, logger_name=None):
        self.level = level
        self.name = name
        self.logger_name = logger_name
        if logger_name is None:
            self.logger = logging.getLogger()
        else:
            self.logger = logging.getLogger(logger_name)

    def __call__(self, customlevel):
        """
        Wrap the decorated function to take care of the setting up of the custom log level.

        """
        # Add the new custom level to the list of known levels
        logging.addLevelName(self.level, self.name)

        def _wrapper(msg, *args, **kwargs):
            # Check if the currently set level allows this log level to print.
            if self.logger.isEnabledFor(level):
                _msg, _args, _kwargs = customlevel(self.logger, msg, *args, **kwargs)
                self.logger.log(level, _msg, *_args, **_kwargs)

        # Create function bindings in the logger or if using the root logger, setup the bindings to allow
        # calls to logging.mycustomlevel() much like logging.info(), logging.debug() etc.
        setattr(self.logger, self.name, _wrapper)
        if self.logger_name is None:
            setattr(logging, self.name, _wrapper)

        return customlevel


if __name__ == '__main__':

    level = logging.INFO-5
    name = 'cool'
    logger_name = 'mylogger'
    # logger_name = None

    @CustomLogLevel(level, name, logger_name=logger_name)
    def myloglevel(logger, msg, *args, **kwargs):
        return msg, args, kwargs


    logging.basicConfig()
    if logger_name:
        l = logging.getLogger(logger_name)
        logger = l
    else:
        l = logging.getLogger()
        logger = logging

    l.setLevel(logging.INFO)
    logger.info('this is a test')
    logger.cool('this is a test')
    l.setLevel(level)
    logger.info('this is a test')
    logger.cool('this is a test')


