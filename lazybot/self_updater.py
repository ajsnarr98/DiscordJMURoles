import os
import sys
import time

import git

def check_for_updates() -> bool:
    """ Pulls master branch of repo from git
        
        NOTE: Expects git to be initialized and
              current working dir to be in a cloned
              git repo.
              
        Return (bool):
            Whether or not updates were found.
    """

    no_changes = 'Already up to date.'

    working_dir = os.path.dirname(os.path.abspath(__file__))

    git_cmd = git.cmd.Git(working_dir=working_dir)
    info = git_cmd.pull()
    
    return str(info) != no_changes

def restart(logger, seconds_before_restart=5):
    """ Waits a determined amount of time and then restarts
        this program.
    """
    pre_wait_message = 'event loop has stopped... restarting in {sec}'
    restarting_message = 'restarting bot...'
    
    print()
    while seconds_before_restart > 0:
        print(pre_wait_message.format(sec=seconds_before_restart), end="\r")
        time.sleep(1)
        seconds_before_restart -= 1
    print()
    
    logger.debug(restarting_message)
    time.sleep(.5) # just small delay because print/log statements may now be part of a race condition

    python = sys.executable
    os.execl(python, python, *sys.argv)
