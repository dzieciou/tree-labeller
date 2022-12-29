=================
Predicting labels
=================

Both product and category nodes in a taxonomy can be labelled. Each can have one or more labels predicted. If a node
has multiple labels predicted, then we call it ambiguous prediction.

The process of labelling consists of two phases. In first phase we learn labels of all categories based on manual labels of products, moving from leaves to the root of $T$. Each inner node of $T$ gets a union of labels of its leaves. In second phase we move backwards: each leaf unlabelled so far gets labels of its labelled ancestors.
