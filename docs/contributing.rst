.. _contributing:

Contributing
============

There are many ways to contribute to the Jamdict project.
The one that Jamdict development team are focusing on at the moment are:

- Fixing :ref:`existing bugs <contrib_bugfix>`
- Improving query functions
- Improving :ref:`documentation <contrib_docs>`
- Keeping jamdict database up to date

If you have some suggestions or bug reports, please share on `jamdict issues tracker <https://github.com/neocl/jamdict/issues>`_.

.. _contrib_bugfix:

Fixing bugs
-----------

If you found a bug please report at https://github.com/neocl/jamdict/issues

When it is possible, please also share how to reproduce the bugs and a snapshot of jamdict info to help with the bug finding process.

.. code:: bash

   python3 -m jamdict info

Pull requests are welcome.

.. _contrib_docs:

Updating Documentation
----------------------

1. Fork `jamdict <https://github.com/neocl/jamdict>`_ repository to your own Github account.

#. Clone `jamdict` repository to your local machine.

   .. code:: bash
      
      git clone https://github.com/<your-account-name>/jamdict
      
#. Create a virtual environment (optional, but highly recommended)

   .. code:: bash

      # if you use virtualenvwrapper
      mkvirtualenv jamdev
      workon jamdev

      # if you use Python venv
      python3 -m venv .env
      . .env/bin/activate
      python3 -m pip install --upgrade pip wheel Sphinx

#. Build the docs

   .. code:: bash

      cd jamdict/docs
      # compile the docs
      make dirhtml
      # serve the docs using Python3 built-in development server
      # Note: this requires Python >= 3.7 to support --directory
      python3 -m http.server 7000 --directory _build/dirhtml
      # if you use earlier Python 3, you may use
      cd _build/dirhtml
      python3 -m http.server 7000

#. Now the docs should be ready to view at http://localhost:7000 . You can visit that URL on your browser to view the docs.

#. More information:

   - Sphinx tutorial: https://sphinx-tutorial.readthedocs.io/start/
   - Using `virtualenv`: https://virtualenvwrapper.readthedocs.io/en/latest/install.html
   - Using `venv`: https://docs.python.org/3/library/venv.html

.. _contrib_dev:

Development
-----------

Development contributions are welcome.
Setting up development environment for Jamdict should be similar to :ref:`contrib_docs`.

Please contact the development team if you need more information: https://github.com/neocl/jamdict/issues
