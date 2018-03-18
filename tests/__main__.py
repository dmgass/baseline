# Copyright (c) 2018 Daniel Mark Gass
# Licensed under the MIT License
# http://opensource.org/licenses/MIT

from __future__ import absolute_import

import unittest, sys
from . import test_dir, top_dir
tests = unittest.defaultTestLoader.discover(start_dir=test_dir,
                                            top_level_dir=top_dir)
result = unittest.TextTestRunner(verbosity=1).run(tests)
sys.exit(0 if result.wasSuccessful() else 1)
