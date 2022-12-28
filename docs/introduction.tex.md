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

Manual labelling
----------------

Labels are assigned manually to a product in two situations: if the product has not been labelled manually so far or multiple label candidates have been predicted. In the latter case, an annotator can choose from one of predicated candidates or propose a different label.




  

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
