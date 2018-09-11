### To regenerate the docs using this folder easily

    - cd into sphinx folder
    - move the files you want to document into sphinx/gamelib
    - run sphinx-apidoc -o ./rst ./gamelib
    - Make a copy of modules.rst, name it index.rst
    - run sphinx-build -b ./html ./rst

### To create the docs from scratch

    - Make sure sphinx is installed and updated
    - Create your sphinx folder
    - Run sphinx quickstart and fill out the options as follows
        - Provide project info when prompted
        - yes for auto generate from docstrings
        - yes for add links to source code
        - yes for add makefile
        - no for add Windows file (assuming you are not on windows)
    - In conf.py, uncomment 'import os' and 'import sys'.
    - In conf.py, add the following lines just below imports
        - sys.path.insert(0, os.path.abspath('.')) 
        - sys.path.append(os.path.abspath('./gamelib'))  
        - sys.path.append(os.path.abspath('..'))
    - If you want to use this exact structure, create an html, gamelib, and rst directory
    - Put a copy of conf.py into rst
    - Run 'make html'