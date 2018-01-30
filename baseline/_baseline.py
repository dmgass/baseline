import atexit
import inspect
import os

from _script import Script


class Baseline(object):

    z__bad_baselines = set()

    z__registered_atexit = False

    def __init__(self, text):

        frame = inspect.getouterframes(inspect.currentframe())[2]
        self.z__path = os.path.abspath(frame[1])
        self.z__linenum = frame[2]

        lines = text.split('\n')

        if len(lines) < 2:
            raise RuntimeError('text must have at least 1 newline')

        if lines[0].strip():
            raise RuntimeError('first line must be blank')

        if lines[-1].strip():
            raise RuntimeError('last line must only contain indent whitespace')

        self._indent = len(lines[-1])

        if any(line[:self._indent].strip() for line in lines):
            raise RuntimeError('indents must equal or exceed indent in last line')

        self._lines = [line[self._indent:] for line in lines][1:-1]

        self._updates = set()

    def __eq__(self, text):
        lines = [line.rstrip() for line in text.split('\n')]

        # indents = [len(line) - len(line.lstrip()) for line in lines]
        # min_indent = min([indent for indent in indents if indent] or [0])
        # lines = [line[min_indent:] for line in lines]

        result = lines == self._lines

        if not result:
            self._updates.add('\n'.join(lines))
            Baseline.z__bad_baselines.add(self)
            if not Baseline.z__registered_atexit:
                Baseline.z__registered_atexit = True
                atexit.register(Baseline.z__atexit_callback)

        return result

    @property
    def z__update(self):
        update = '\n******\n'.join(self._updates)
        return '\n'.join((indent + line).rstrip() for line in lines)

    def z__atexit_callback():
        scripts = {}
        for baseline in Baseline.z__bad_baselines:
            try:
                script = scripts[baseline.z__path]
            except KeyError:
                script = Script(baseline.path)
                scripts[baseline.path] = script

            script.add_mismatch(baseline)

        for key in sorted(scripts):
            script = scripts[key]
            script.update()
