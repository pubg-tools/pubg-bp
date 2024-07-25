# -*- coding: utf-8 -*-
"""
This file can be called from terminal to convert an .py file to .pyd or .c file, where .pyd is kind
of a .dll file for python which can be called in any python model but anyone can not read it easily
and .c file contains our algorithm in ``c`` programing language.
we can call the file in the following way from the terminal:

```
$ python encrypt.py -f FILE.py
```

This command line will create following 3 files and 1 folder:

- FILE.cp[PYTHON_VERSION].[OS_NAME].pyd : Files can be used as python .dll file
- FILE.c    : File contains algorithm in ``c`` programing language
- FILE.pyx  : File which is used for creating .pyd file (can delete this file)
- build (folder)    : Folder contains our algorithms .exe, .lib and .obj file

Now you can directly use .pyd file in your other python files by importing in the following way:
```
import FILE
```

Error:
++++++
- Unable to find vcvarsall.bat : This error shows that we don't have c compiler in our os
download and install microsoft visual c++ build tools for you respective os and python version.
"""

import shutil
import os
import argparse


class Encryptor:
    """
    Class: Encryptor have following methods:

    - __init__(self, file_path): Takes file_path (python file path) as an argument and initialize
     other variables then calls setup_file() and encrypt() methods
    - setup_file(self): Creates a setup.py file with its context
    - encrypt(self): Call the setup.py file from terminal/command prompt
    """

    def __init__(self, file_path):
        r"""
        This method  initialize all the variables then calls setup_file() and encrypt() methods.
        It also creates File.pyx which is just copy of File.py with renamed to File.pyx, cython read
        File.pyx file not FIle.py file.
        :param file_path: Python file path example: (C:\Project_folder\File.py)
        """
        if not os.path.exists(file_path):
            raise Exception("{} does not exists!".format(file_path))
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.file_dir = os.path.dirname(self.file_path)
        self.file_base_name, self.file_extension = os.path.splitext(self.file_name)
        if not self.file_extension == ".py":
            raise Exception("{} is not .py format!".format(self.file_extension))
        # Creating .pvx file
        self.file_pyx_name = self.file_base_name + ".pyx"
        shutil.copy(self.file_path, self.file_pyx_name)
        self.setup_file()
        self.encrypt()

    def setup_file(self):
        """
        Creates a setup.py file which contains the cython script to cythonize the FILE.pyx file.
        """
        with open("setup.py", "+w") as file:
            file.write(
                "from setuptools import setup\n"
                "from Cython.Build import cythonize\n\n"
                "setup(ext_modules=cythonize('{}'))".format(self.file_pyx_name)
            )

    def encrypt(self):
        """
        Calls the setup.py from terminal/command prompt to cythonize the file.
        """
        command = "python setup.py build_ext --inplace"
        os.system(str(command))

        print(
            "Now you can directly use import {} to use your file and"
            " its functions from .pyd file.".format(self.file_base_name)
        )


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Convert .py file to .pyd file using Cython"
    )
    PARSER.add_argument(
        "-f",
        "--file",
        type=str,
        action="store",
        help="Enter the file_path(if "
        "file is in other "
        "directory else file name) "
        "which you want to convert "
        "to .pyd format\nPlease "
        'use "FILE_NAME" for your '
        "file name",
    )
    ARGS = PARSER.parse_args()
    Encryptor(ARGS.file)
