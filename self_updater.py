import os
import sys
import time

import git

def check_for_updates():
    """ Pulls master branch of repo from git
        
        NOTE: Expects git to be initialized and
              current working dir to be in a cloned
              git repo.
    """

    working_dir = os.path.dirname(os.path.abspath(__file__))

    git_cmd = git.cmd.Git(working_dir=working_dir)
    git_cmd.pull()

def restart(logger, seconds_before_restart=5):
    """ Waits a determined amount of time and then restarts
        this program.y
    """
    pre_wait_message = 'event loop has stopped... waiting {sec} seconds before restart'
    restarting_message = 'restarting bot...'

    logger.debug(pre_wait_message.format(sec=seconds_before_restart))
    time.sleep(seconds_before_restart)
    logger.debug(restarting_message)

    python = sys.executable
    os.execl(python, python, *sys.argv)
