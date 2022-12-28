====
Demo
====

Here is a quick demonstration how to map products from a real online shop, `Frisco.pl`_, to departments in a real local grocery, `Marketpoint`_.


.. _Frisco.pl: https://www.frisco.pl/
.. _Marketpoint: https://market-point.pl/sklepy/sklep-krakow-rynek-falecki-1/



Use case
--------

Same products can be organized differently, depending on the shop. See, for instance, how products are distributed across different departments of Marketpoint.

.. image:: imgs/marketpoint.svg

The arrangement of departments in my local grocery shop. Sometimes, related products are split into two distant locations, e.g., most vegetable preserves are in Fruits & vegetable preserves on the left except for canned tomatoes that can be found in Tomato preserves in the middle. Sometimes, same products can be found in two distant departments, e.g., cheese can be both in Diary and in Cheese (by weight).

Preparing taxonomy
------------------

Download sample taxonomy file of products and their categories from  online shop.

.. code-block:: bash

    fetch_frisco > frisco.yaml


Labelling
---------

Create task for labelling Frisco products with departments from Marketpoint.

.. code-block:: bash

    create_task \
        --dir ./marketpoint \
        --tree ./frisco.yaml \
        --allowed-labels Alcohols,Beers,Vegetables

Sample products for labelling:


.. code-block:: bash

    label ./marketpoint
