=============
Tree Labeller
=============

Labels all leaves of a tree based only on a small sample of manually labelled leaves.

Sample scenarios include:

- Assigning shop departments to products organized in a taxonomy of categories
- Mapping taxonomy of book categories in one library to flat vocabulary of book categories in another library
- Annotating training data organized in a tree

The input has format:

.. code-block:: yaml

    name: categories
    children:
    - name: Alholic Drinks
      children:
      - name: Whiskies
        children:
        - name: Jack Daniel's
        - name: Johnnie Walker's
      - name: Wines
        children:
        - name: Cabernet Sauvignon
      - name: Beers
        children:
        - name: Guinness


The output has format:

.. code-block:: tsv

    name	            label
    Jack Daniel's	    Alcohols department
    Johnnie Walker's    Alcohols department
    Cabernet Sauvignon  Alcohols department
    Guiness             Beers department
    ...

Install
=======

Install with pip:

.. code-block:: bash

    pip install tree-labeller


Usage
=====




Development
===========

Install poetry:

.. code-block:: bash

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

Install the labelling tool:

.. code-block:: bash

    poetry install --no-dev
    poetry shell


Usage
=====

Labelling
---------

Labelling is a semi-automatic iterative process. You start by labeling few samples and the rule-based prediction algorithm tries to learn and tag the rest of the data set for you. You then correct predicted labels for a sample of most ambiguous items and the algorithm repeats prediction based on labels you provided.

The algorithm suggests the most diverse sample of items to label, i.e. coming from different categories, so you don't waste time with samples that have high chance of belonging to the same shop department. Items in the sample are sorted starting from the most ambiguous ones, i.e., having many possible labels.

Here are the steps to follow.

Define a name of shop. It will be used to locate data and model:

.. code-block:: bash

    export TARGET_SHOP=shop

Create a folder where new labels will be stored:

.. code-block:: bash

    mkdir -p labels/${TARGET_SHOP}

Define list of available departments in the shop in ``labels/${TARGET_SHOP}/departments.txt`` with each department
in a separate line, e.g.:

.. code-block:: bash

    Drogeria
    Dżemy i miody
    Herbata
    Kawa
    Konserwy mięsne i rybne

To generate a sample and run predictions:

.. code-block:: bash

    label \
        --allowed-labels labels/${TARGET_SHOP}/departments.txt \
        --labels labels/${TARGET_SHOP}/ \
        --n-sample 10

After each iteration you will get statistics to help you decide when to stop labelling:

.. code-block:: bash

      Iteration    Manual    Univocal    Ambiguous    Missing    Total    Allowed Labels
    -----------  --------  ----------  -----------  ---------  -------  ----------------
              1         0          0%           0%       100%    14456                0%
              2        10         71%          29%         0%    14456               37%

In the ideal situation we want to have 100% of univocal predictions, 0% of ambiguous and missing predictions and 100% of allowed labels (departments) coverage while providing as few manual labels as possible.

If you decide to continue, you can do one or more of the following actions:

- Correct ambiguous predicted labels in a sample.
- Correct your previous manual labels.
- Label with ``?`` to skip the product from the prediction (it won't be sampled next time).
- Label with ``!`` to tell the algorithm that the product ,and perhaps its category, are not present in the target shop (the algorithm will try to learn other similar products that might be not present in a shop)
- If one of departments have no products labeled so far, you can search for matching products manually and add them to the sample with correct label. For search you can use last TSV file with univocal predicted labels.
- You can also occasionally review univocal predicted labels and correct them by adding to the sample.


Development
===========

Install poetry.


Install environment:

.. code-block:: bash

    poetry install


Publish package to dev registry.

.. code-block:: bash

    poetry publish -r dev --build

