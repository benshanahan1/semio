""" 
The MIT License (MIT)
Copyright (c) 2016 Benjamin Shanahan

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from distutils.core import setup
import py2exe

setup(name="Semio",
    version="1.0",
    description="Objective Semiology Diagnostic Tool",
    author="Benjamin Shanahan",
    author_email="benshanahan1@gmail.com",
    url="http://www.bshanahan.info/semio",
    # console=[  # for non-windows distributions
    windows=[
        {
            "script": "main.py",
            "icon_resources": [(0, "icon/favicon.ico")],
            "dest_base": "Semio"
        }
    ],
    data_files=[
        ("icon", ["icon/favicon.ico"]),
        ("data", ["data/data.json"]),
    ])