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


Sampling products for manual labelling
--------------------------------------

Requirements:
* Cover all products
* Cover all labels



Given a tree <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/>, we want to find a subset <img src="svgs/f9c4988898e7f532b9f826a75014ed3c.svg?invert_in_darkmode" align=middle width=14.99998994999999pt height=22.465723500000017pt/> of <img src="svgs/55a049b8f161ae7cfeb0197d75aff967.svg?invert_in_darkmode" align=middle width=9.86687624999999pt height=14.15524440000002pt/> leaves that are the farthest apart. I.e., we want to find <img src="svgs/f9c4988898e7f532b9f826a75014ed3c.svg?invert_in_darkmode" align=middle width=14.99998994999999pt height=22.465723500000017pt/> that maximizes function:

<img src="svgs/10dfb819130b17d07ad98871c5b73260.svg?invert_in_darkmode" align=middle width=175.2078636pt height=33.89973840000001pt/>  

where <img src="svgs/8790a6e51a3b8a0b16013a135871a86d.svg?invert_in_darkmode" align=middle width=62.18617514999999pt height=24.65753399999998pt/> is a distance between two vertices/nodes <img src="svgs/277fbbae7d4bc65b6aa601ea481bebcc.svg?invert_in_darkmode" align=middle width=15.94753544999999pt height=14.15524440000002pt/> and <img src="svgs/95d239357c7dfa2e8d1fd21ff6ed5c7b.svg?invert_in_darkmode" align=middle width=15.94753544999999pt height=14.15524440000002pt/>. Now imagine, there is a subtree in <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/> with many very deep leaves that are close to each other but very far from leaves in other subtrees of <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/>. If we defined the distance as just the shortest number of edges between two nodes, then maximizing <img src="svgs/3be7c0b48f7c34bf07832269c78b5eb6.svg?invert_in_darkmode" align=middle width=36.21575924999999pt height=24.65753399999998pt/> would lead to solutions where many related categories get selected, e.g. `>Alkohol>Alkohole mocne>Whisky>Szkocka`, `>Alkohol>Alkohole mocne>Whisky>Irlandzka`, `>Alkohol>Alkohole mocne>Whisky>Angielska` rather than `>Alkohol>Alkohole mocne>Whisky>Szkocka`, `Alkohol>Piwo>Piwo bezalkoholowe>Piwo bezalkoholowe` and `Alkohol>Wino>Wino bezalkoholowe>Wino bezalkoholowe`. 

TODO Make a nice picture here

Therefore, we introduce weight <img src="svgs/31fae8b8b78ebe01cbfbe2fe53832624.svg?invert_in_darkmode" align=middle width=12.210846449999991pt height=14.15524440000002pt/> to edges that gives more preferences to paths going closer to the root:

<img src="svgs/10a8277280bc6ea7426a192bc3a5c3e9.svg?invert_in_darkmode" align=middle width=297.40643295pt height=29.190975000000005pt/>  

where <img src="svgs/7c5d09796fa72f50fc8f541920f3d44a.svg?invert_in_darkmode" align=middle width=30.68980694999999pt height=14.15524440000002pt/> is a child of <img src="svgs/9fc20fb1d3825674c6a279cb0d5ca636.svg?invert_in_darkmode" align=middle width=14.045887349999989pt height=14.15524440000002pt/>. Now

<img src="svgs/85b51e19a5771379dd17f88838439b88.svg?invert_in_darkmode" align=middle width=199.12879964999996pt height=46.06407959999998pt/>  

where <img src="svgs/715f1d9bbd0efc96188daed9f2a78c9a.svg?invert_in_darkmode" align=middle width=90.21505514999998pt height=14.15524440000002pt/> is a walk (sequence of nodes).

Finding farthest leaves in a tree
---------------------------------


If we have a binary tree, we should be able to solve this using [dynamic programming][3].  Let <img src="svgs/789737ac1507bda7fca8f102735e5d6f.svg?invert_in_darkmode" align=middle width=60.503389649999995pt height=24.65753399999998pt/> denote the maximum possible value of the objective function

<img src="svgs/b3003206bc2792d9ccbf0617943d8215.svg?invert_in_darkmode" align=middle width=325.3718094pt height=24.7161288pt/>

where <img src="svgs/f9c4988898e7f532b9f826a75014ed3c.svg?invert_in_darkmode" align=middle width=14.99998994999999pt height=22.465723500000017pt/> ranges over all subsets of exactly <img src="svgs/36b5afebdba34564d884d347484ac0c7.svg?invert_in_darkmode" align=middle width=7.710416999999989pt height=21.68300969999999pt/> leaves from among those that are descendants of <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/> (i.e., leaves of the subtree rooted at <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/>) and <img src="svgs/63bb9849783d01d91403bc9a5fea12a2.svg?invert_in_darkmode" align=middle width=9.075367949999992pt height=22.831056599999986pt/> is the number of leaves in the remaining part of the tree (i.e., not being descendants of <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/>).

If <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/> is a leaf, then <img src="svgs/aad2f9296e477961d6dddba681df1ee2.svg?invert_in_darkmode" align=middle width=90.64022879999999pt height=24.65753399999998pt/> for all <img src="svgs/141a2a51928b1276452103cbde48ae17.svg?invert_in_darkmode" align=middle width=23.17842449999999pt height=22.831056599999986pt/>. If <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/> has one child <img src="svgs/19ef11ed79c62a9cb46775c20450d89f.svg?invert_in_darkmode" align=middle width=12.347803049999989pt height=24.7161288pt/>, it is easy to compute that <img src="svgs/0b5adee2a8a01ea27c7c77a0f6cf1483.svg?invert_in_darkmode" align=middle width=184.41326144999996pt height=24.7161288pt/> for all <img src="svgs/141a2a51928b1276452103cbde48ae17.svg?invert_in_darkmode" align=middle width=23.17842449999999pt height=22.831056599999986pt/>.

So now suppose <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/> has two children <img src="svgs/20a447ad9b96078ae3dfd9e093caa2dc.svg?invert_in_darkmode" align=middle width=36.61336469999999pt height=24.7161288pt/>.  Then we can work out a recursive equation for <img src="svgs/789737ac1507bda7fca8f102735e5d6f.svg?invert_in_darkmode" align=middle width=60.503389649999995pt height=24.65753399999998pt/> in terms of values <img src="svgs/97f337fb6ad5d2c7317f331c3f6d1e81.svg?invert_in_darkmode" align=middle width=57.416307299999986pt height=24.65753399999998pt/> where the <img src="svgs/31fae8b8b78ebe01cbfbe2fe53832624.svg?invert_in_darkmode" align=middle width=12.210846449999991pt height=14.15524440000002pt/>'s are descendants of <img src="svgs/6c4adbc36120d62b98deef2a20d5d303.svg?invert_in_darkmode" align=middle width=8.55786029999999pt height=14.15524440000002pt/>:


<img src="svgs/255715c05add81e4dcde890f190e95a1.svg?invert_in_darkmode" align=middle width=446.94511125pt height=24.7161288pt/>

where <img src="svgs/c6e69007f01adcf9c3411036de93368b.svg?invert_in_darkmode" align=middle width=34.91851769999999pt height=24.7161288pt/> range over all values such that <img src="svgs/aae6edd1af4a63f6983dddb982932a91.svg?invert_in_darkmode" align=middle width=78.1537812pt height=24.7161288pt/>, <img src="svgs/7972c0db592b2436c74fb19b8b0bb482.svg?invert_in_darkmode" align=middle width=95.50531319999997pt height=24.7161288pt/>.  The intended meaning is that <img src="svgs/1041e382f1560a32a7a26f335a9e77bf.svg?invert_in_darkmode" align=middle width=11.500379549999991pt height=24.7161288pt/> counts the number of leaves in <img src="svgs/f9c4988898e7f532b9f826a75014ed3c.svg?invert_in_darkmode" align=middle width=14.99998994999999pt height=22.465723500000017pt/> that are descendants of <img src="svgs/19ef11ed79c62a9cb46775c20450d89f.svg?invert_in_darkmode" align=middle width=12.347803049999989pt height=24.7161288pt/> and <img src="svgs/5a076e77e958e2544ebdfdec74d3e819.svg?invert_in_darkmode" align=middle width=15.29034209999999pt height=24.7161288pt/> counts the number of leaves in <img src="svgs/f9c4988898e7f532b9f826a75014ed3c.svg?invert_in_darkmode" align=middle width=14.99998994999999pt height=22.465723500000017pt/> that are descendants of <img src="svgs/5081f7b158385a4bde3513e2af9b8208.svg?invert_in_darkmode" align=middle width=16.13776559999999pt height=24.7161288pt/>.  In other words, we split <img src="svgs/a286a55d62007a0d2ae74c96f9285757.svg?invert_in_darkmode" align=middle width=97.37403389999999pt height=24.7161288pt/> where <img src="svgs/4e561a02bc60d8c644063654dc2fee6e.svg?invert_in_darkmode" align=middle width=18.78993104999999pt height=24.7161288pt/> contains <img src="svgs/1041e382f1560a32a7a26f335a9e77bf.svg?invert_in_darkmode" align=middle width=11.500379549999991pt height=24.7161288pt/> leaves from the descendants of <img src="svgs/19ef11ed79c62a9cb46775c20450d89f.svg?invert_in_darkmode" align=middle width=12.347803049999989pt height=24.7161288pt/>, and <img src="svgs/62eded7ff8301fe42b2af33f6367da50.svg?invert_in_darkmode" align=middle width=22.579891949999993pt height=24.7161288pt/> contains <img src="svgs/5a076e77e958e2544ebdfdec74d3e819.svg?invert_in_darkmode" align=middle width=15.29034209999999pt height=24.7161288pt/> leaves from the descendants of <img src="svgs/5081f7b158385a4bde3513e2af9b8208.svg?invert_in_darkmode" align=middle width=16.13776559999999pt height=24.7161288pt/>; then (loosely speaking) we compute the maximum value of <img src="svgs/3daa05846df920aa811dfb6cb16c5f90.svg?invert_in_darkmode" align=middle width=40.827634649999986pt height=24.7161288pt/> in terms of the maximum values of <img src="svgs/94e71218f285db1a4d287adc972ddc88.svg?invert_in_darkmode" align=middle width=45.43951004999998pt height=24.7161288pt/> and <img src="svgs/e586df343652d9fe00a840d84e6aa0de.svg?invert_in_darkmode" align=middle width=49.229465999999995pt height=24.7161288pt/>.  The <img src="svgs/22f267816abde93adeac5238140fa88f.svg?invert_in_darkmode" align=middle width=27.43000589999999pt height=24.7161288pt/> term counts distances of the form <img src="svgs/375ce81f3b623ec92367b71fd8aa043b.svg?invert_in_darkmode" align=middle width=62.18617514999999pt height=24.65753399999998pt/> where <img src="svgs/cc58914feb7d7e9183cb56b28c426bd7.svg?invert_in_darkmode" align=middle width=55.65051689999999pt height=24.7161288pt/> and <img src="svgs/56e1e4cb66bad49b68fd88f5bdca5094.svg?invert_in_darkmode" align=middle width=59.44047779999999pt height=24.7161288pt/>.  The <img src="svgs/c81353603ee07b56135c3bd79f7b87ab.svg?invert_in_darkmode" align=middle width=16.78578659999999pt height=22.831056599999986pt/> term accounts for the fact that the <img src="svgs/36b5afebdba34564d884d347484ac0c7.svg?invert_in_darkmode" align=middle width=7.710416999999989pt height=21.68300969999999pt/> root-to-leaf paths all need to be extended by one edge.

<img src="svgs/53d147e7f3fe6e47ee05b88b166bd3f6.svg?invert_in_darkmode" align=middle width=12.32879834999999pt height=22.465723500000017pt/> can be calculated by traversing <img src="svgs/2f118ee06d05f3c2d98361d9c30e38ce.svg?invert_in_darkmode" align=middle width=11.889314249999991pt height=22.465723500000017pt/> in post order.

If we have an arbitrary tree, not necessarily a binary tree, then it can be converted to a binary tree as follows. Children from the original tree are encoded as a left child in the binary tree and edges to left children preserve their original weights. Remaining edges, those to right children, have 0 weight. TODO Add an image.





Distributing labelling budget
-----------------------------

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