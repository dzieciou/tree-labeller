Imagine you have a large pile of products, and you want to categorize those products by shop departments they can be found in. This can be a daunting task if you want to do it one by one. However, products live in groups, and often products from the same group can be found in the same department. For instance, Jack Daniel's and Johnnie Walker's whiskies both can be found in the Alcohols department. If we choose and label one product from *each* group manually, we can automatically label the remaining products. This can save us a lot of time and probably money! Especially, if you want to do it for many, many shops: locations of products and available departments vary from one shop to another. 

But... did I say labeling *each* group manually? There might still be many more groups than we can label manually. Fortunately,
groups of products are organized into larger groups, and again, products from those larger groups often tend to be located in the same department. Although, with certain exceptions. For instance, Jack Daniel's whisky and Cabernet Sauvignon wine are in the Alcohols department, but Guinness can be found in my grocery store in a different department, Beers. Even though whiskies, wines, and beers are in the same large group of alcoholic drinks.

![image-title](imgs/tree_1.png)

So how do you choose products for manual labeling? And how do you infer automated labels from those manual labels?

Formalizing problem
-------------------

If <img src="svgs/fce9019a5e1fa63e079199cd9b11c55e.svg?invert_in_darkmode" align=middle width=12.337954199999992pt height=22.465723500000017pt/> is a set of classes (labels or shop departments in our example), and <img src="svgs/7da75f4e61cdeabf944740206b511812.svg?invert_in_darkmode" align=middle width=14.132466149999988pt height=22.465723500000017pt/> is a space of all possible products and product groups, then our goal is to find a classifier function <img src="svgs/66ac6408d7fc5921ca31194bdcb08df9.svg?invert_in_darkmode" align=middle width=75.55685114999999pt height=22.831056599999986pt/>. This sounds like a [multiclass classification](https://en.wikipedia.org/wiki/Multiclass_classification) problem, although we are not necessarily going to use machine learning to solve it. 

Obviously, we have bent reality a bit assuming that:

* each product can be found only in one department (otherwise that would be [multi-label classification](https://en.wikipedia.org/wiki/Multi-label_classification)), 
* and all products can be found in a considered grocery store.

We have the budget to manually label only <img src="svgs/55a049b8f161ae7cfeb0197d75aff967.svg?invert_in_darkmode" align=middle width=9.86687624999999pt height=14.15524440000002pt/> of <img src="svgs/0e51a2dede42189d77627c4d742822c3.svg?invert_in_darkmode" align=middle width=14.433101099999991pt height=14.15524440000002pt/> products, where <img src="svgs/4eda06e639f0759a58c5e781852a21a6.svg?invert_in_darkmode" align=middle width=59.61564179999999pt height=24.65753399999998pt/> and <img src="svgs/489babe086c218990c6c44560f8017cf.svg?invert_in_darkmode" align=middle width=49.87057679999999pt height=17.723762100000005pt/>. 

Products are organized in categories that make up a taxonomy <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/>. More formally, a taxonomy, is a tree, where leaves stand 
for products and inner nodes are product categories.

Labelling in iterations
-----------------------

My idea is to label products iteratively.

First iteration is somehow special:

1. Sample <img src="svgs/b4fdbf4e9e08385fb7c6dd70d18f51b6.svg?invert_in_darkmode" align=middle width=57.043308299999985pt height=22.465723500000017pt/> products.
2. Label <img src="svgs/4a0dab614eaf1e6dc58146666d67ace8.svg?invert_in_darkmode" align=middle width=20.17129784999999pt height=22.465723500000017pt/> manually.
3. Predict labels for remaining products (<img src="svgs/03c23a1fe5a7b9dee5217b678ef3e840.svg?invert_in_darkmode" align=middle width=49.82872784999999pt height=24.65753399999998pt/>) based on labels for <img src="svgs/4a0dab614eaf1e6dc58146666d67ace8.svg?invert_in_darkmode" align=middle width=20.17129784999999pt height=22.465723500000017pt/> and relations in <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/>.

There will be products (<img src="svgs/4e1dcfc6c3009ba241e86add0e87a9d1.svg?invert_in_darkmode" align=middle width=19.034022149999988pt height=22.465723500000017pt/>) with only one matching label and products (<img src="svgs/264fba1c7ab2f0bc1611dac6780708a6.svg?invert_in_darkmode" align=middle width=16.632471899999988pt height=22.465723500000017pt/>) with ambiguous predictions, i.e., 
multiple label candidates, that require manual clarification. In subsequent iterations <img src="svgs/a07e538fdb521b27534795a0845f6f0f.svg?invert_in_darkmode" align=middle width=77.80903184999998pt height=21.68300969999999pt/> we will gradually 
clarify those ambiguous predictions:

1. Sample <img src="svgs/d537974612b119219327f3d9633751a2.svg?invert_in_darkmode" align=middle width=72.56657099999998pt height=22.465723500000017pt/> products. 
2. Label <img src="svgs/1338d1e5163ba5bc872f1411dd30b36a.svg?invert_in_darkmode" align=middle width=18.269651399999987pt height=22.465723500000017pt/> manually.
3. Predict labels for products without manual labels (<img src="svgs/d1dfb5f289dc5485aecfbf46ef4b1275.svg?invert_in_darkmode" align=middle width=89.38933574999999pt height=31.75825949999999pt/>) based on all manual labels collected so far (i.e. labels for <img src="svgs/8b5f51cbd69b19bcd7d49c6f07f6272a.svg?invert_in_darkmode" align=middle width=59.73190574999998pt height=31.75825949999999pt/>) and relations in <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/>.

Repeat until there are no products with ambiguous predictions (<img src="svgs/c14048522285c45bc782814beee94acd.svg?invert_in_darkmode" align=middle width=54.82200899999998pt height=24.65753399999998pt/>) or you have consumed whole
budget (<img src="svgs/77e26f659508bed2a277eb15d2113492.svg?invert_in_darkmode" align=middle width=105.12371594999999pt height=31.75825949999999pt/>). The ultimate labelling will come from both manual labels
(for <img src="svgs/8b5f51cbd69b19bcd7d49c6f07f6272a.svg?invert_in_darkmode" align=middle width=59.73190574999998pt height=31.75825949999999pt/>) and unambiguous predictions (for <img src="svgs/affb5ec0de99c455da0189c50279e339.svg?invert_in_darkmode" align=middle width=58.59463004999999pt height=31.75825949999999pt/>).

Manual labelling
----------------

Labels are assigned manually to a product in two situations: if the product has not been labelled manually so far or multiple label candidates have been predicted. In the latter case, an annotator can choose from one of predicated candidates or propose a different label.



Predicting labels
-----------------

Both product and category nodes in a taxonomy can be labelled. Each can have one or more labels predicted. If a node
has multiple labels predicted, then we call it ambiguous prediction.

The process of labelling consists of two phases. In first phase we learn labels of all categories based on manual labels of products, moving from leaves to the root of <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/>. Each inner node of <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/> gets a union of labels of its leaves. In second phase we move backwards: each leaf unlabelled so far gets labels of its labelled ancestors.

  

Evaluation
----------

I have collected a large dataset of products from [Frisco.pl](https://www.frisco.pl/) and I want to group them by deparments of my local grocery shop. For instance, *CIRIO Peeled Tomatoes* product can be found *Tomato Preserves* department in my local shop. 

Further reading
---------------

The problem we are tackling here is similar to taxonomy mapping. See ["SCHEMA - An Algorithm for Automated
Product Taxonomy Mapping in E-commerce"][1] for a sample method on that or ["Ontology Matching"][2] book for a survey of taxonomy mapping methods.

[1]: https://link.springer.com/content/pdf/10.1007/978-3-642-30284-8_27.pdf
[2]: http://www.filosofiacienciaarte.org/attachments/article/1129/Je%CC%81ro%CC%82me%20Euzenat-Ontology%20Matching.pdf
