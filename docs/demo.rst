====
Demo
====

Here is a quick demonstration how to map products from online shop to departments in a local grocery.

Download sample taxonomy file of products and their categories from `Frisco.pl`_ online shop.

.. code-block:: bash

    fetch_frisco > frisco.yaml

Create task for labelling Frisco products with departments from `Marketpoint`_, local grocery in Krakow.

.. code-block:: bash

    create_task \
        --dir ./marketpoint \
        --tree ./frisco.yaml \
        --allowed-labels Alcohols,Beers,Vegetables

Sample products for labelling:


.. code-block:: bash

    label ./marketpoint

.. _Frisco.pl: https://www.frisco.pl/
.. _Marketpoint: https://market-point.pl/sklepy/sklep-krakow-rynek-falecki-1/


