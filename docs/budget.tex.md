# Distributing labelling budget


## Formalizing problem

If $\mathcal{Y}$ is a set of classes (labels or shop departments in our example), and $\mathcal{X}$ is a space of all possible products and product groups, then our goal is to find a classifier function $f: \mathcal{X} \to \mathcal{Y}$. This sounds like a [multiclass classification](https://en.wikipedia.org/wiki/Multiclass_classification) problem, although we are not necessarily going to use machine learning to solve it. 

Obviously, we have bent reality a bit assuming that:

* each product can be found only in one department (otherwise that would be [multi-label classification](https://en.wikipedia.org/wiki/Multi-label_classification)), 
* and all products can be found in a considered grocery store.

We have the budget to manually label only $n$ of $m$ products, where $m=\vert\mathcal{X}\vert$ and $n \ll m$. 

Products are organized in categories that make up a taxonomy $T$. More formally, a taxonomy, is a tree, where leaves stand 
for products and inner nodes are product categories.

## Labelling in iterations

My idea is to label products iteratively.

First iteration is somehow special:

1. Sample $X_1 \subset \mathcal{X}$ products.
2. Label $X_1$ manually.
3. Predict labels for remaining products ($\mathcal{X} \setminus X_1$) based on labels for $X_1$ and relations in $T$.

There will be products ($R_1$) with only one matching label and products ($S_1$) with ambiguous predictions, i.e., 
multiple label candidates, that require manual clarification. In subsequent iterations $i=2,3,\dots$ we will gradually 
clarify those ambiguous predictions:

1. Sample $X_i \subset S_{i-1}$ products. 
2. Label $X_i$ manually.
3. Predict labels for products without manual labels ($\mathcal{X} \setminus \bigcup_{j=1}^{i}{X_{j}}$) based on all manual labels collected so far (i.e. labels for $\bigcup_{j=1}^{i}{X_{j}}$) and relations in $T$.

Repeat until there are no products with ambiguous predictions ($\vert S_i \vert = 0$) or you have consumed whole
budget ($\sum_{j=1}^{i}{\vert X_j \vert} \geq n $). The ultimate labelling will come from both manual labels
(for $\bigcup_{j=1}^{i}{X_{j}}$) and unambiguous predictions (for $\bigcup_{j=1}^{i}{R_{j}}$).

## Considerations

We have one annotator, predicting next label costs nothing (compared to manual cost), so given a budget <img src="svgs/55a049b8f161ae7cfeb0197d75aff967.svg?invert_in_darkmode" align=middle width=9.86687624999999pt height=14.15524440000002pt/>, so we can have <img src="svgs/55a049b8f161ae7cfeb0197d75aff967.svg?invert_in_darkmode" align=middle width=9.86687624999999pt height=14.15524440000002pt/> iterations, in each we select only one product for manual labelling.

The problem then boils down, which product to select next?
- The one that resolves most conflicts: products with the highest number of label candidates?
- Or on the contrary: 
  
  > "In contrast, for an ambiguous instance which falls near the boundary of categories, even
those reliable workers will still disagree with each other and generate inconsistent labels.
For those ambiguous instances, we are facing a challenging decision problem on how much
budget that we should spend on them. On one hand, it is worth to collect more labels to
boost the accuracy of the aggregate label. On the other hand, since our goal is to maximize
the overall labeling accuracy, when the budget is limited, we should simply put those few
highly ambiguous instances aside to save budget for labeling less difficult instances." 

Quote form [Statistical Decision Making for Optimal Budget Allocation in Crowd Labeling](https://www.jmlr.org/papers/volume16/chen15a/chen15a.pdf)

Technically, the number of conflicting labels could be included in the weight function.

However, if in the first iteration we select only one item to label then all remaining items will get same label (which might be incorrect). In the begining we want to find items matching possibly all label classes. 

Also, conflicts are good because they lead to clarification. 

TODO:
- Experiment with current implementation to get some intuitions on budget allocation, number of iterations, when conflicts are good.
- If we don't have groundtruth labels, how do we know what is an optimal labelling, how to measure it? How they evaluated that in the paper?