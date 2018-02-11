import atexit
import inspect
import os

from _script import Script

SEPARATOR = '\n' + '*' * 40 + '\n'


class Baseline(str):

    z__unequal_baselines = set()

    z__registered_atexit = False

    _all_instances = {}

    z__updated_scripts = {}

    @staticmethod
    def _dedent(text):
        lines = text.split('\n')

        if len(lines) == 1:
            indent = 0

        elif lines[0].strip():
            raise RuntimeError('first line must be blank')

        elif lines[-1].strip():
            raise RuntimeError('last line must only contain indent whitespace')

        else:
            indent = len(lines[-1])

            if any(line[:indent].strip() for line in lines):
                raise RuntimeError('indents must equal or exceed indent in last line')

            lines = [line[indent:] for line in lines][1:-1]

        return indent, '\n'.join(lines)

    def __new__(cls, text):

        frame = inspect.getouterframes(inspect.currentframe())[1]
        path = os.path.abspath(frame[1])
        if path.endswith('.pyc'):
            assert 0, "should we ever get here?"
            # path = path[:-4] + '.py'
        linenum = frame[2]

        key = (path, linenum)

        try:
            instance = cls._all_instances[key]
        except KeyError:
            indent, text = cls._dedent(text)
            instance = super(Baseline, cls).__new__(cls, text)
            instance.z__raw_text = text
            instance.z__path = path
            instance.z__linenum = linenum
            instance._indent = indent
            instance._updates = set()
            cls._all_instances[key] = instance
        else:
            if text != instance.z__raw_text:
                raise RuntimeError('varying baseline text not allowed')

        return instance

    def __eq__(self, text):
        # don't baseline trailing whitespace to avoid pylint complaints
        text = '\n'.join(line.rstrip() for line in text.split('\n'))

        is_equal = super(Baseline, self).__eq__(text)

        if not is_equal:
            self._updates.add(text)
            Baseline.z__unequal_baselines.add(self)
            if not Baseline.z__registered_atexit:
                Baseline.z__registered_atexit = True
                atexit.register(Baseline.z__atexit_callback)

        return is_equal

    def __ne__(self, text):
        # for use with assertNotEqual( ) for internal regression test purposes
        return not self.__eq__(text)

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
