import os
import pip

pipDependencyFilename = 'pip_dependencies.txt'

working_dir = os.path.dirname(os.path.abspath(__file__))
pipDependencyFilename = os.path.join(working_dir, pipDependencyFilename)

def install():
    """ Installs any missing dependencies using pip """
    dependencies = get_pip_dependencies()

    if dependencies:
        for package in dependencies:
            try:
                pip.main(['install', package])
            except:
                pass

def get_pip_dependencies():
    """ Returns a list of pip modules to install """

    try:
        with open(pipDependencyFilename, 'r') as f:
            return f.readlines()
    except (FileNotFoundError, EOFError):
        return None
