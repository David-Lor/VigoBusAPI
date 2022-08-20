import importlib
import pkgutil

import vigobus.utils


class Utils(vigobus.utils.Utils):

    @staticmethod
    def import_submodules(pkg, recursive=True):
        """Import all the modules of a package. Can recursively include modules from subpackages.
        Useful for processing decorators and other calls at module level.
        Source: https://stackoverflow.com/a/25562415/11245195

        :param pkg: package object or name
        :param recursive: if True, find modules in recursive packages
        """
        if isinstance(pkg, str):
            pkg = importlib.import_module(pkg)

        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(pkg.__path__):
            full_name = pkg.__name__ + '.' + name

            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(Utils.import_submodules(full_name))

        return results
