import atexit
import inspect
import os

from _script import Script

SEPARATOR = '\n' + '*' * 40 + '\n'


class Baseline(object):

    z__unequal_baselines = set()

    z__registered_atexit = False

    _all_instances = {}

    z__updated_scripts = {}

    def __new__(cls, text):

        frame = inspect.getouterframes(inspect.currentframe())[1]
        path = os.path.abspath(frame[1])
        if path.endswith('.pyc'):
            assert 0, "should we ever get here?"
            path = path[:-4] + '.py'
        linenum = frame[2]

        key = (path, linenum)

        try:
            instance = cls._all_instances[key]
        except KeyError:
            instance = super(Baseline, cls).__new__(cls)
            instance.z__path = path
            instance.z__linenum = linenum
            cls._all_instances[key] = instance
        else:
            if text != instance.z__raw_text:
                raise RuntimeError('varying baseline text not allowed')

        return instance

    def __init__(self, text):

        if hasattr(self, "z__raw_text"):
            return

        self.z__raw_text = text

        lines = text.split('\n')

        if len(lines) == 1:
            self._indent = 0
            self._lines = lines

        elif lines[0].strip():
            raise RuntimeError('first line must be blank')

        elif lines[-1].strip():
            raise RuntimeError('last line must only contain indent whitespace')

        else:
            self._indent = len(lines[-1])

            if any(line[:self._indent].strip() for line in lines):
                raise RuntimeError('indents must equal or exceed indent in last line')

            self._lines = [line[self._indent:] for line in lines][1:-1]

        self._updates = set()

    def __eq__(self, text):
        lines = [line.rstrip() for line in text.split('\n')]

        result = lines == self._lines

        if not result:
            self._updates.add('\n'.join(lines))
            Baseline.z__unequal_baselines.add(self)
            if not Baseline.z__registered_atexit:
                Baseline.z__registered_atexit = True
                atexit.register(Baseline.z__atexit_callback)

        return result

    def __ne__(self, text):
        # for use with assertNotEqual( ) for internal regression test purposes
        return not self.__eq__(text)

    def __repr__(self):
        return repr('\n'.join(self._lines))

    @property
    def z__update(self):
        update = SEPARATOR.join(self._updates)
        indent = ' ' * self._indent
        lines = [(indent + line).rstrip() for line in update.split('\n')]
        if len(lines) > 1:
            lines = [''] + lines + [indent]
        return '\n'.join(lines)

    @staticmethod
    def z__atexit_callback():
        updated_scripts = Baseline.z__updated_scripts

        for baseline in Baseline.z__unequal_baselines:
            try:
                script = updated_scripts[baseline.z__path]
            except KeyError:
                script = Script(baseline.z__path)
                updated_scripts[baseline.z__path] = script

            script.add_update(baseline.z__linenum, baseline.z__update)

        for key in sorted(updated_scripts):
            script = updated_scripts[key]
            script.update()
