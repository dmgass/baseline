import atexit
import inspect
import os

from _script import Script


class Baseline(object):

    z__bad_baselines = set()

    z__registered_atexit = False

    _all_instances = {}

    def __new__(cls, text):

        frame = inspect.getouterframes(inspect.currentframe())[1]
        path = os.path.abspath(frame[1])
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
        return '\n'.join(
            (' ' * self._indent + line).rstrip() for line in update.split('\n'))

    @staticmethod
    def z__atexit_callback():
        scripts = {}
        for baseline in Baseline.z__bad_baselines:
            try:
                script = scripts[baseline.z__path]
            except KeyError:
                script = Script(baseline.z__path)
                scripts[baseline.z__path] = script

            script.add_mismatch(baseline)

        for key in sorted(scripts):
            print "SCRIPT", script.path
            script = scripts[key]
            script.update()


x = Baseline("""
line 1
line 2
""")


heredoc = """
line 1
    line 2
line 3
"""

print x == heredoc
print x == heredoc + 'line 4'

y = Baseline("""
line 1
line 2
""")

heredoc2 = """
line 1
line 2
line 3
"""

print y == heredoc2
