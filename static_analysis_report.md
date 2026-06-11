# Static Analysis Audit Report

### Ruff Linting Violations
```
E402 Module level import not at top of file
  --> app\main.py:9:1
   |
 7 |     sys.path.insert(0, str(PROJECT_ROOT))
 8 |
 9 | import streamlit as st
   | ^^^^^^^^^^^^^^^^^^^^^^
10 | import time
11 | from config.config import PROJECT_NAME
   |

E402 Module level import not at top of file
  --> app\main.py:10:1
   |
 9 | import streamlit as st
10 | import time
   | ^^^^^^^^^^^
11 | from config.config import PROJECT_NAME
12 | from database.mongodb import db_conn
   |

F401 [*] `time` imported but unused
  --> app\main.py:10:8
   |
 9 | import streamlit as st
10 | import time
   |        ^^^^
11 | from config.config import PROJECT_NAME
12 | from database.mongodb import db_conn
   |
help: Remove unused import: `time`

E402 Module level import not at top of file
  --> app\main.py:11:1
   |
 9 | import streamlit as st
10 | import time
11 | from config.config import PROJECT_NAME
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
12 | from database.mongodb import db_conn
13 | from config.logger impo
```
### MyPy Typing Violations
```
app\__init__.py: error: Duplicate module named "app" (also at "backend\app\__init__.py")
app\__init__.py: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules for more info
app\__init__.py: note: Common resolutions include:
app\__init__.py: note:     a) using `--exclude` to avoid checking one of them,
app\__init__.py: note:     b) adding `__init__.py` somewhere,
app\__init__.py: note:     c) using `--explicit-package-bases` or adjusting `MYPYPATH`
Found 1 error in 1 file (errors prevented further checking)

```