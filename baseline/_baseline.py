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

        triple_single_quote = (text[-1] == '"') or ('"""' in text)

        if triple_single_quote and "'''" in text:
            text = text.replace("'''", r"' ''")
        else:
            text = text.replace('"""', r'" ""')

        if text[-1] == '\\' and text[-2:] != r'\\':
            text += ' '

        text = ''.join(
            (r if len(r) == 3 else c) for c, r in [(c, repr(c)[1:-1]) for c in text])

        is_equal = super(Baseline, self).__eq__(text)

        if not is_equal:
            quotes = "'''" if triple_single_quote else '"""'
            if '\n' in text:
                update = 'r' + quotes + '\n' + text + '\n' + quotes
            else:
                update = 'r' + quotes + text + quotes
            self._updates.add(update)
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
        # sort updates so Python has seed has no impact on regression test
        update = SEPARATOR.join(sorted(self._updates))
        indent = ' ' * self._indent
        lines = [(indent + line).rstrip() for line in update.split('\n')]
        if len(lines) > 1:
            lines = [''] + lines
        return '\n'.join(lines).lstrip()

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
