__author__ = 'calvin'

import cProfile
import logging
from pyperform import StringIO
import os
import pstats
import sys
import threading

Thread = threading.Thread          # Start off using threading.Thread until changed
BaseThread = threading.Thread      # Store the Thread class from the threading module before monkey-patching
profiled_thread_enabled = False
logged_thread_enabled = True


def enable_thread_profiling(profile_dir, exception_callback=None):
    """
    Monkey-patch the threading.Thread class with our own ProfiledThread. Any subsequent imports of threading.Thread
    will reference ProfiledThread instead.
    """
    global profiled_thread_enabled, Thread
    if os.path.isdir(profile_dir):
        ProfiledThread.profile_dir = profile_dir
    else:
        raise OSError('%s does not exist' % profile_dir)
    ProfiledThread.exception_callback = exception_callback
    Thread = threading.Thread = ProfiledThread
    profiled_thread_enabled = True


def enable_thread_logging(exception_callback=None):
    """
    Monkey-patch the threading.Thread class with our own LoggedThread. Any subsequent imports of threading.Thread
    will reference LoggedThread instead.
    """
    global logged_thread_enabled, Thread
    LoggedThread.exception_callback = exception_callback
    Thread = threading.Thread = LoggedThread
    logged_thread_enabled = True


class ProfiledThread(BaseThread):
    """
    A Thread that contains it's own profiler. When the SSI_App closes, all profiles are combined and printed
    to a single .profile.
    """
    profile_dir = None
    exception_callback = None

    def run(self):
        profiler = cProfile.Profile()
        try:
            logging.debug('ProfiledThread: Starting ProfiledThread {}'.format(self.name))
            profiler.runcall(BaseThread.run, self)
        except Exception as e:
            logging.error('ProfiledThread: Error encountered in Thread {name}'.format(name=self.name))
            logging.error(e)
            if ProfiledThread.exception_callback:
                e_type, e_value, last_traceback = sys.exc_info()
                ProfiledThread.exception_callback(e_type, e_value, last_traceback)
        finally:
            if ProfiledThread.profile_dir is None:
                logging.warning('ProfiledThread: profile_dir is not specified. '
                                'Profile \'{}\' will not be saved.'.format(self.name))
                return
            self.print_stats(profiler)

    def print_stats(self, profiler):
        filename = os.path.join(self.profile_dir, self.name)
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(profiler, stream=s)
        # Take out directory names
        ps.strip_dirs()
        # Sort
        ps.sort_stats(sortby)
        # Print to the stream
        ps.print_stats()

        stats_file = filename + '.stats'
        profile_file = filename + '.profile'
        # Create the stats file
        ps.dump_stats(stats_file)
        # Create a readable .profile file
        with open(profile_file, 'w') as f:
            f.write(s.getvalue())

    @staticmethod
    def combine_profiles(profile_dir, outfile, sortby='cumulative'):
        s = StringIO.StringIO()
        stat_files = [f for f in os.listdir(profile_dir) if os.path.isfile(os.path.join(profile_dir, f))
                      and f.endswith('.stats')]
        ps = pstats.Stats(os.path.join(profile_dir, stat_files[0]), stream=s)
        if len(stat_files) > 1:
            for stat in stat_files[1:]:
                ps.add(os.path.join(profile_dir, stat))

        profile_name = os.path.join(profile_dir, '{}.profile'.format(outfile.replace('.profile', '')))
        with open(profile_name, 'w') as f:
            ps.strip_dirs()
            ps.sort_stats(sortby)
            ps.print_stats()
            f.write(s.getvalue())


class LoggedThread(BaseThread):

    exception_callback = None

    def run(self):
        logging.debug('LoggedThread: Starting LoggedThread {}'.format(self.name))
        try:
            super(LoggedThread, self).run()
        except Exception as e:
            logging.error('LoggedThread: Error encountered in Thread {name}'.format(name=self.name))
            logging.error(e)
            if LoggedThread.exception_callback:
                e_type, e_value, last_traceback = sys.exc_info()
                LoggedThread.exception_callback(e_type, e_value, last_traceback)


