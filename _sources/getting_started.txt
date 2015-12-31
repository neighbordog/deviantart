Getting started with deviantart for python
==========================================

Installation
----------

Installation using ``pip``::

    pip install deviantart

Basic usage
----------

.. code-block:: python
   :linenos:

   #import deviantart library
   import deviantart

   #create an API object with your client credentials
   da = deviantart.Api("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")

   #fetch daily deviations
   dailydeviations = da.browse_dailydeviations()

   #loop over daily deviations
   for deviation in dailydeviations:

       #print deviation title
       print deviation.title

       #print username of author of deviation
       print deviation.author.username
