.. _installpage:

Installation
=============

jamdict and jamdict dictionary data are both available on PyPI and can be installed using `pip`.

.. code-block:: bash

   pip install --user jamdict jamdict-data
   # pip script sometimes doesn't work properly
   # so you may want to try this instead
   python3 -m pip install jamdict jamdict-data

.. note::
   When you use :code:`pip install` in a virtual environment, especially the ones created via :code:`python3 -m venv`,
   wheel support can be missing. :code:`jamdict-data` relies on wheel/pip to extract xz-compressed database and this may cause a problem.
   If you encounter any error, please make sure that wheel is available

   .. code-block:: bash

      # list all available packages in pip
      pip list
      # ensure wheel support in pip
      pip install -U wheel

   You may need to uninstall :code:`jamdict-data` before reinstalling it.

   .. code-block:: bash

      pip uninstall jamdict-data

Download database file manually
-------------------------------

This should not be useful anymore from version 0.1a8 with the release of the `jamdict_data <https://pypi.org/project/jamdict_data/>`_ package on PyPI.
If for some reason you want to download and install jamdict database by yourself, here are the steps:

1. Download the offical, pre-compiled jamdict database
   (``jamdict-0.1a7.tar.xz``) from Google Drive
   https://drive.google.com/drive/u/1/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk
2. Extract and copy ``jamdict.db`` to jamdict data folder (defaulted to
   ``~/.jamdict/data/jamdict.db``)
3. To know where to copy data files you can use `python3 -m jamdict info` command via a terminal: 

.. code:: bash

  python3 -m jamdict info
  # Jamdict 0.1a8
  # Python library for manipulating Jim Breen's JMdict, KanjiDic2, KRADFILE and JMnedict
  #
  # Basic configuration
  # ------------------------------------------------------------
  # JAMDICT_HOME             : ~/local/jamdict
  # jamdict_data availability: False
  # Config file location     : /home/tuananh/.jamdict/config.json
  # 
  # Custom Data files
  # ------------------------------------------------------------
  # Jamdict DB location: ~/local/jamdict/data/jamdict.db - [OK]
  # JMDict XML file    : ~/local/jamdict/data/JMdict_e.gz - [OK]
  # KanjiDic2 XML file : ~/local/jamdict/data/kanjidic2.xml.gz - [OK]
  # JMnedict XML file : ~/local/jamdict/data/JMnedict.xml.gz - [OK]
  # 
  # Others
  # ------------------------------------------------------------
  # lxml availability: False

Build database file from source
-------------------------------

Normal users who just want to look up the dictionaries do not have to do this.
If you are a developer and want to build jamdict database from source,
copy the dictionary source files to jamdict data folder.
The original XML files can be downloaded either from the official website
https://www.edrdg.org/ or from `this jamdict Google Drive folder <https://drive.google.com/drive/folders/1ZMM6Xb46XcwwQGWBZnY3gj637exWPWuU>`_.

To find out where to copy the files or whether they are recognised by jamdict,
you may use the command `python3 -m jamdict info` as in the section above.

You should make sure that all files under the section `Custom data files` are all marked [OK].
After that you should be able to build the database with the command:

.. code:: bash

  python3 -m jamdict import

Note on XML parser: jamdict will use `lxml` instead of Python 3 default `xml` when it is available.


