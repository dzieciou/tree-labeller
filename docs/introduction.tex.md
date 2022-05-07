Imagine you have a large pile of products, and you want to categorize those products by shop departments they can be found in. This can be a daunting task if you want to do it one by one. However, products live in groups, and often products from the same group can be found in the same department. For instance, Jack Daniel's and Johnnie Walker's whiskies both can be found in the Alcohols department. If we choose and label one product from *each* group manually, we can automatically label the remaining products. This can save us a lot of time and probably money! Especially, if you want to do it for many, many shops: locations of products and available departments vary from one shop to another. 

But... did I say labeling *each* group manually? There might still be many more groups than we can label manually. Fortunately,
groups of products are organized into larger groups, and again, products from those larger groups often tend to be located in the same department. Although, with certain exceptions. For instance, Jack Daniel's whisky and Cabernet Sauvignon wine are in the Alcohols department, but Guinness can be found in my grocery store in a different department, Beers. Even though whiskies, wines, and beers are in the same large group of alcoholic drinks.

![image-title](imgs/tree_1.png)

So how do you choose products for manual labeling? And how do you infer automated labels from those manual labels?

Formalizing problem
-------------------

If $\mathcal{Y}$ is a set of classes (labels or shop departments in our example), and $\mathcal{X}$ is a space of all possible products and product groups, then our goal is to find a classifier function $f: \mathcal{X} \to \mathcal{Y}$. This sounds like a [multiclass classification](https://en.wikipedia.org/wiki/Multiclass_classification) problem, although we are not necessarily going to use machine learning to solve it. 

Obviously, we have bent reality a bit assuming that:

* each product can be found only in one department (otherwise that would be [multi-label classification](https://en.wikipedia.org/wiki/Multi-label_classification)), 
* and all products can be found in a considered grocery store.

We have the budget to manually label only $n$ of $m$ products, where $m=\vert\mathcal{X}\vert$ and $n \ll m$. 

Products are organized in categories that make up a taxonomy $T$. More formally, a taxonomy, is a tree, where leaves stand 
for products and inner nodes are product categories.

Labelling in iterations
-----------------------

My idea is to label products iteratively.

First iteration is somehow special:

1. Sample $X_1 \subset \mathcal{X}$ products.
2. Label $X_1$ manually.
3. Predict labels for remaining products ($\mathcal{X} \setminus X_1$) based on labels for $X_1$ and relations in 
   $T$.

There will be products ($R_1$) with only one matching label and products ($S_1$) with ambiguous predictions, i.e., 
multiple label candidates, that require manual clarification. In subsequent iterations $i=2,3,\dots$ we will gradually 
clarify those ambiguous predictions:

1. Sample $X_i \subset S_{i-1}$ products. 
2. Label $X_i$ manually.
3. Predict labels for products without manual labels ($\mathcal{X} \setminus \bigcup_{j=1}^{i}{X_{j}}$) based on all 
   manual labels collected so far (i.e. labels for $\bigcup_{j=1}^{i}{X_{j}}$) and relations in $T$.

Repeat until there are no products with ambiguous predictions ($\vert S_i \vert = 0$) or you have consumed whole
budget ($\sum_{j=1}^{i}{\vert X_j \vert} \geq n $). The ultimate labelling will come from both manual labels
(for $\bigcup_{j=1}^{i}{X_{j}}$) and unambiguous predictions (for $\bigcup_{j=1}^{i}{R_{j}}$).

Manual labelling
----------------

Labels are assigned manually to a product in two situations: if the product has not been labelled manually so far or multiple label candidates have been predicted. In the latter case, an annotator can choose from one of predicated candidates or propose a different label.



Predicting labels
-----------------

Both product and category nodes in a taxonomy can be labelled. Each can have one or more labels predicted. If a node
has multiple labels predicted, then we call it ambiguous prediction.

The process of labelling consists of two phases. In first phase we learn labels of all categories based on manual labels of products, moving from leaves to the root of $T$. Each inner node of $T$ gets a union of labels of its leaves. In second phase we move backwards: each leaf unlabelled so far gets labels of its labelled ancestors.


Sampling products for manual labelling
--------------------------------------

Requirements:
* Cover all products
* Cover all labels



Given a tree $T$, we want to find a subset $N$ of $n$ leaves that are the farthest apart. I.e., we want to find $N$ that maximizes function:

$g(N)=\sum\limits_{x_1,x_2 \in N}{d(x_1,x_2)}$  

where $d(x_1, x_2)$ is a distance between two vertices/nodes $x_1$ and $x_2$. Now imagine, there is a subtree in $T$ with many very deep leaves that are close to each other but very far from leaves in other subtrees of $T$. If we defined the distance as just the shortest number of edges between two nodes, then maximizing $g(N)$ would lead to solutions where many related categories get selected, e.g. `>Alkohol>Alkohole mocne>Whisky>Szkocka`, `>Alkohol>Alkohole mocne>Whisky>Irlandzka`, `>Alkohol>Alkohole mocne>Whisky>Angielska` rather than `>Alkohol>Alkohole mocne>Whisky>Szkocka`, `Alkohol>Piwo>Piwo bezalkoholowe>Piwo bezalkoholowe` and `Alkohol>Wino>Wino bezalkoholowe>Wino bezalkoholowe`. 

TODO Make a nice picture here

Therefore, we introduce weight $w$ to edges that gives more preferences to paths going closer to the root:

$w(x_{i+1}, x_i) = w(x_i, x_{i+1})=10^{-depth(x_{i+1})}$  

where $x_{i+1}$ is a child of $x_i$. Now

$d(x_1, x_m)=\sum\limits_{i=1}^{m-1}{w(x_i,x_{i+1})}$  

where $x_1, x_2, ..., x_m$ is a walk (sequence of nodes).

Finding farthest leaves in a tree
---------------------------------


If we have a binary tree, we should be able to solve this using [dynamic programming][3].  Let $A[v,j,k]$ denote the maximum possible value of the objective function

$g'(N) = \sum_{x_1,x_2 \in N} d(x_1,x_2) + k \sum_{x \in N} d(v,x)$

where $N$ ranges over all subsets of exactly $j$ leaves from among those that are descendants of $v$ (i.e., leaves of the subtree rooted at $v$) and $k$ is the number of leaves in the remaining part of the tree (i.e., not being descendants of $v$).

If $v$ is a leaf, then $A[v,j,k]=0$ for all $j,k$. If $v$ has one child $v'$, it is easy to compute that $A[v,j,k]=A[v',j,k] + jk$ for all $j,k$.

So now suppose $v$ has two children $v',v''$.  Then we can work out a recursive equation for $A[v,j,k]$ in terms of values $A[w,\cdot,\cdot]$ where the $w$'s are descendants of $v$:


$
A[v,j,k] = \max A[v',j',k+j''] + A[v'',j'',k+j'] + 2 j' j'' + jk
$

where $j',j''$ range over all values such that $j'+j'' = j$, $0 \le j',j'' \le j$.  The intended meaning is that $j'$ counts the number of leaves in $N$ that are descendants of $v'$ and $j''$ counts the number of leaves in $N$ that are descendants of $v''$.  In other words, we split $N=N' \cup N''$ where $N'$ contains $j'$ leaves from the descendants of $v'$, and $N''$ contains $j''$ leaves from the descendants of $v''$; then (loosely speaking) we compute the maximum value of $g'(N)$ in terms of the maximum values of $g'(N')$ and $g'(N'')$.  The $2jj'$ term counts distances of the form $d(x_1,x_2)$ where $x_1 \in N'$ and $x_2 \in N''$.  The $jk$ term accounts for the fact that the $j$ root-to-leaf paths all need to be extended by one edge.

$A$ can be calculated by traversing $T$ in post order.

If we have an arbitrary tree, not necessarily a binary tree, then it can be converted to a binary tree as follows. Children from the original tree are encoded as a left child in the binary tree and edges to left children preserve their original weights. Remaining edges, those to right children, have 0 weight. TODO Add an image.





Distributing labelling budget
-----------------------------

We have one annotator, predicting next label costs nothing (compared to manual cost), so given a budget $n$, so we can have $n$ iterations, in each we select only one product for manual labelling.

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


Evaluation
----------

I have collected a large dataset of products from [Frisco.pl](https://www.frisco.pl/) and I want to group them by deparments of my local grocery shop. For instance, *CIRIO Peeled Tomatoes* product can be found *Tomato Preserves* department in my local shop. 

Further reading
---------------

The problem we are tackling here is similar to taxonomy mapping. See ["SCHEMA - An Algorithm for Automated
Product Taxonomy Mapping in E-commerce"][1] for a sample method on that or ["Ontology Matching"][2] book for a survey of taxonomy mapping methods.

Acknowledgements
----------------

I would like to thank people from StackExchange for help in developing algorithms, my girlfriend Renata for help in mapping our local grocery store and my work mates for feedback during Lighting Talks.

[1]: https://link.springer.com/content/pdf/10.1007/978-3-642-30284-8_27.pdf
[2]: http://www.filosofiacienciaarte.org/attachments/article/1129/Je%CC%81ro%CC%82me%20Euzenat-Ontology%20Matching.pdf
[3]: https://en.wikipedia.org/wiki/Dynamic_programming