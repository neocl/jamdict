#!/bin/bash

pandoc --from=markdown --to=rst README.md -o README.rst
python3 setup.py sdist
