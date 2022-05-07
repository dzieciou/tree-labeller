Imagine you have a large pile of products, and you want to categorize those products by shop departments they can be found in. This can be a daunting task if you want to do it one by one. However, products live in groups, and often products from the same group can be found in the same department. For instance, Jack Daniel's and Johnnie Walker's whiskies both can be found in the Alcohols department. If we choose and label one product from *each* group manually, we can automatically label the remaining products. This can save us a lot of time and probably money! Especially, if you want to do it for many, many shops: locations of products and available departments vary from one shop to another. 

But... did I say labeling *each* group manually? There might still be many more groups than we can label manually. Fortunately,
groups of products are organized into larger groups, and again, products from those larger groups often tend to be located in the same department. Although, with certain exceptions. For instance, Jack Daniel's whisky and Cabernet Sauvignon wine are in the Alcohols department, but Guinness can be found in my grocery store in a different department, Beers. Even though whiskies, wines, and beers are in the same large group of alcoholic drinks.

![image-title](imgs/tree_1.png)

So how do you choose products for manual labeling? And how do you infer automated labels from those manual labels?

Formalizing problem
-------------------

If <p align="center"><img src="svgs/e05be64d51efb7645867f2c085b94c04.svg?invert_in_darkmode" align=middle width=12.337954199999999pt height=12.8310534pt/></p> is a set of classes (labels or shop departments in our example), and <p align="center"><img src="svgs/46a17f664dc94d5ef15fb8067ad26891.svg?invert_in_darkmode" align=middle width=14.132466149999997pt height=11.232861749999998pt/></p> is a space of all possible products and product groups, then our goal is to find a classifier function <p align="center"><img src="svgs/248bd81d8d22c4e647d1d6f00788df1f.svg?invert_in_darkmode" align=middle width=75.55685115pt height=14.611878599999999pt/></p>. This sounds like a [multiclass classification](https://en.wikipedia.org/wiki/Multiclass_classification) problem, although we are not necessarily going to use machine learning to solve it. 

Obviously, we have bent reality a bit assuming that:

* each product can be found only in one department (otherwise that would be [multi-label classification](https://en.wikipedia.org/wiki/Multi-label_classification)), 
* and all products can be found in a considered grocery store.

We have the budget to manually label only <p align="center"><img src="svgs/b49da7325822089835b531a5fce8b94e.svg?invert_in_darkmode" align=middle width=9.866876249999999pt height=7.0776222pt/></p> of <p align="center"><img src="svgs/5d55430569d9a949e663776910069118.svg?invert_in_darkmode" align=middle width=14.4331011pt height=7.0776222pt/></p> products, where <p align="center"><img src="svgs/346636a05ff25db88664e0938e9d9d6d.svg?invert_in_darkmode" align=middle width=59.6156418pt height=16.438356pt/></p> and <p align="center"><img src="svgs/b168864bc27f014bff6418f7d3331e6f.svg?invert_in_darkmode" align=middle width=49.8705768pt height=9.5045841pt/></p>. 

Products are organized in categories that make up a taxonomy <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p>. More formally, a taxonomy, is a tree, where leaves stand 
for products and inner nodes are product categories.

Labelling in iterations
-----------------------

My idea is to label products iteratively.

First iteration is somehow special:

1. Sample <p align="center"><img src="svgs/3fcfc03ecf6ceec57065de65270211e7.svg?invert_in_darkmode" align=middle width=57.0433083pt height=13.698590399999999pt/></p> products.
2. Label <p align="center"><img src="svgs/7e1ccff43e4f502a27a0d5ea5e6b1d5c.svg?invert_in_darkmode" align=middle width=20.17129785pt height=13.698590399999999pt/></p> manually.
3. Predict labels for remaining products (<p align="center"><img src="svgs/3341efe9fc0de83a534b89a075e644e4.svg?invert_in_darkmode" align=middle width=49.82872784999999pt height=16.438356pt/></p>) based on labels for <p align="center"><img src="svgs/7e1ccff43e4f502a27a0d5ea5e6b1d5c.svg?invert_in_darkmode" align=middle width=20.17129785pt height=13.698590399999999pt/></p> and relations in 
   $$T$$.

There will be products (<p align="center"><img src="svgs/e23c514840f22fd17a0d9a9b9a551c6f.svg?invert_in_darkmode" align=middle width=19.03402215pt height=13.698590399999999pt/></p>) with only one matching label and products (<p align="center"><img src="svgs/9b7fd294d95a11f52d5220868999000b.svg?invert_in_darkmode" align=middle width=16.6324719pt height=13.698590399999999pt/></p>) with ambiguous predictions, i.e., 
multiple label candidates, that require manual clarification. In subsequent iterations <p align="center"><img src="svgs/8762f4ff9a5b3d34f99b0c32511125ab.svg?invert_in_darkmode" align=middle width=77.80903185pt height=14.0378568pt/></p> we will gradually 
clarify those ambiguous predictions:

1. Sample <p align="center"><img src="svgs/1fa59f0cd0946b04897fc009405eb38d.svg?invert_in_darkmode" align=middle width=72.566571pt height=15.068469899999998pt/></p> products. 
2. Label <p align="center"><img src="svgs/37a389f68d63fd7b78a96457e50623a6.svg?invert_in_darkmode" align=middle width=18.2696514pt height=13.698590399999999pt/></p> manually.
3. Predict labels for products without manual labels (<p align="center"><img src="svgs/7868455cee74079f4db849c31c675b62.svg?invert_in_darkmode" align=middle width=74.86874505pt height=49.794650399999995pt/></p>) based on all 
   manual labels collected so far (i.e. labels for $$\bigcup_{j=1}^{i}{X_{j}}$$) and relations in $$T$$.

Repeat until there are no products with ambiguous predictions (<p align="center"><img src="svgs/a0acccd9489d1463693e5ca2faf4eda7.svg?invert_in_darkmode" align=middle width=54.822008999999994pt height=16.438356pt/></p>) or you have consumed whole
budget (<p align="center"><img src="svgs/86e13f8313094688e1509850dc8f14dd.svg?invert_in_darkmode" align=middle width=87.946089pt height=49.794650399999995pt/></p>). The ultimate labelling will come from both manual labels
(for <p align="center"><img src="svgs/fec547ccd214e25d0df44673a7741aa3.svg?invert_in_darkmode" align=middle width=45.2113167pt height=49.794650399999995pt/></p>) and unambiguous predictions (for <p align="center"><img src="svgs/d807784eff73667b1db58c1e2319615b.svg?invert_in_darkmode" align=middle width=44.07403934999999pt height=49.794650399999995pt/></p>).

Manual labelling
----------------

Labels are assigned manually to a product in two situations: if the product has not been labelled manually so far or multiple label candidates have been predicted. In the latter case, an annotator can choose from one of predicated candidates or propose a different label.



Predicting labels
-----------------

Both product and category nodes in a taxonomy can be labelled. Each can have one or more labels predicted. If a node
has multiple labels predicted, then we call it ambiguous prediction.

The process of labelling consists of two phases. In first phase we learn labels of all categories based on manual labels of products, moving from leaves to the root of <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p>. Each inner node of <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p> gets a union of labels of its leaves. In second phase we move backwards: each leaf unlabelled so far gets labels of its labelled ancestors.


Sampling products for manual labelling
--------------------------------------

Requirements:
* Cover all products
* Cover all labels



Given a tree <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p>, we want to find a subset <p align="center"><img src="svgs/d546e0ee5a0604ca911ec7acb79e5a97.svg?invert_in_darkmode" align=middle width=14.99998995pt height=11.232861749999998pt/></p> of <p align="center"><img src="svgs/b49da7325822089835b531a5fce8b94e.svg?invert_in_darkmode" align=middle width=9.866876249999999pt height=7.0776222pt/></p> leaves that are the farthest apart. I.e., we want to find <p align="center"><img src="svgs/d546e0ee5a0604ca911ec7acb79e5a97.svg?invert_in_darkmode" align=middle width=14.99998995pt height=11.232861749999998pt/></p> that maximizes function:

<p align="center"><img src="svgs/216723aaa0181fd8459fc69cbf601423.svg?invert_in_darkmode" align=middle width=175.2078636pt height=39.1417719pt/></p>  

where <p align="center"><img src="svgs/33d67271a538b42492422baa9f7b6c54.svg?invert_in_darkmode" align=middle width=62.186175150000004pt height=16.438356pt/></p> is a distance between two vertices/nodes <p align="center"><img src="svgs/c2fa5941b3d4c85c25fe3827abe9affe.svg?invert_in_darkmode" align=middle width=15.947535449999998pt height=9.54335085pt/></p> and <p align="center"><img src="svgs/333940104ee36bb66bd7bc67f7a366e0.svg?invert_in_darkmode" align=middle width=15.947535449999998pt height=9.54335085pt/></p>. Now imagine, there is a subtree in <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p> with many very deep leaves that are close to each other but very far from leaves in other subtrees of <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p>. If we defined the distance as just the shortest number of edges between two nodes, then maximizing <p align="center"><img src="svgs/54d514a298db824e4d3f8c6ffc6ca212.svg?invert_in_darkmode" align=middle width=36.21575925pt height=16.438356pt/></p> would lead to solutions where many related categories get selected, e.g. `>Alkohol>Alkohole mocne>Whisky>Szkocka`, `>Alkohol>Alkohole mocne>Whisky>Irlandzka`, `>Alkohol>Alkohole mocne>Whisky>Angielska` rather than `>Alkohol>Alkohole mocne>Whisky>Szkocka`, `Alkohol>Piwo>Piwo bezalkoholowe>Piwo bezalkoholowe` and `Alkohol>Wino>Wino bezalkoholowe>Wino bezalkoholowe`. 

TODO Make a nice picture here

Therefore, we introduce weight <p align="center"><img src="svgs/7511f9c6a56927681a7d279e2d413cff.svg?invert_in_darkmode" align=middle width=12.21084645pt height=7.0776222pt/></p> to edges that gives more preferences to paths going closer to the root:

<p align="center"><img src="svgs/51f361706cb45f4ef9f4b522943b779d.svg?invert_in_darkmode" align=middle width=297.40643294999995pt height=19.526994300000002pt/></p>  

where <p align="center"><img src="svgs/e8e8cc5ed3b854041319ca444dcefe86.svg?invert_in_darkmode" align=middle width=30.689806949999994pt height=10.91323035pt/></p> is a child of <p align="center"><img src="svgs/96de47a534893e2f93c9edceffaef3d1.svg?invert_in_darkmode" align=middle width=14.045887349999997pt height=9.54335085pt/></p>. Now

<p align="center"><img src="svgs/348454366f999af9dca9017e2b1368fd.svg?invert_in_darkmode" align=middle width=199.12879965pt height=47.35857885pt/></p>  

where <p align="center"><img src="svgs/3ad6df89932a9ad094278c2f14cf3e11.svg?invert_in_darkmode" align=middle width=90.21505514999998pt height=10.2739725pt/></p> is a walk (sequence of nodes).

Finding farthest leaves in a tree
---------------------------------


If we have a binary tree, we should be able to solve this using [dynamic programming][3].  Let <p align="center"><img src="svgs/8b518c082b17865e28c89980c82093e0.svg?invert_in_darkmode" align=middle width=60.503389649999995pt height=16.438356pt/></p> denote the maximum possible value of the objective function

<p align="center"><img src="svgs/bf35dfd072f99c6809431c33f23e8eba.svg?invert_in_darkmode" align=middle width=289.02467055pt height=39.1417719pt/></p>

where <p align="center"><img src="svgs/d546e0ee5a0604ca911ec7acb79e5a97.svg?invert_in_darkmode" align=middle width=14.99998995pt height=11.232861749999998pt/></p> ranges over all subsets of exactly <p align="center"><img src="svgs/7d6abfd7a8903d8827b35524704fd563.svg?invert_in_darkmode" align=middle width=7.710417pt height=14.0378568pt/></p> leaves from among those that are descendants of <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p> (i.e., leaves of the subtree rooted at <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p>) and <p align="center"><img src="svgs/28b0b71e05b371ee11b28542314966d1.svg?invert_in_darkmode" align=middle width=9.07536795pt height=11.4155283pt/></p> is the number of leaves in the remaining part of the tree (i.e., not being descendants of <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p>).

If <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p> is a leaf, then <p align="center"><img src="svgs/b393d4f25795b846f1635d6c3d21e227.svg?invert_in_darkmode" align=middle width=90.6402288pt height=16.438356pt/></p> for all <p align="center"><img src="svgs/3be08e3e5ff3288be04472defc61fcf1.svg?invert_in_darkmode" align=middle width=23.1784245pt height=14.611878599999999pt/></p>. If <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p> has one child <p align="center"><img src="svgs/e0e3e6abad4cf2ae029ad99ba26b464a.svg?invert_in_darkmode" align=middle width=12.34780305pt height=13.1799822pt/></p>, it is easy to compute that <p align="center"><img src="svgs/1dceaa3c3c4ffb8186a9ff3239549124.svg?invert_in_darkmode" align=middle width=184.41326145pt height=17.2895712pt/></p> for all <p align="center"><img src="svgs/3be08e3e5ff3288be04472defc61fcf1.svg?invert_in_darkmode" align=middle width=23.1784245pt height=14.611878599999999pt/></p>.

So now suppose <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p> has two children <p align="center"><img src="svgs/fd041ba790081001d2919ec3ca40a8cf.svg?invert_in_darkmode" align=middle width=36.6133647pt height=16.3763325pt/></p>.  Then we can work out a recursive equation for <p align="center"><img src="svgs/8b518c082b17865e28c89980c82093e0.svg?invert_in_darkmode" align=middle width=60.503389649999995pt height=16.438356pt/></p> in terms of values <p align="center"><img src="svgs/d629c684e55295f4dff6bd7f2631f068.svg?invert_in_darkmode" align=middle width=57.41630729999999pt height=16.438356pt/></p> where the <p align="center"><img src="svgs/7511f9c6a56927681a7d279e2d413cff.svg?invert_in_darkmode" align=middle width=12.21084645pt height=7.0776222pt/></p>'s are descendants of <p align="center"><img src="svgs/25b3c6d9e0664b5d06c2966de6205582.svg?invert_in_darkmode" align=middle width=8.557860299999998pt height=7.0776222pt/></p>:


<p align="center"><img src="svgs/c1cc7318905dbbdd4fdf525e75ae0d36.svg?invert_in_darkmode" align=middle width=446.94511125pt height=17.2895712pt/></p>

where <p align="center"><img src="svgs/0d7e04ec545f0daa50041506d4b248b9.svg?invert_in_darkmode" align=middle width=34.9185177pt height=16.3763325pt/></p> range over all values such that <p align="center"><img src="svgs/4a0503e4e5d92647b2ebb25f2f49d4c9.svg?invert_in_darkmode" align=middle width=78.1537812pt height=16.3763325pt/></p>, <p align="center"><img src="svgs/fec9d49801b9a57544b757e776282f49.svg?invert_in_darkmode" align=middle width=95.50531319999999pt height=16.3763325pt/></p>.  The intended meaning is that <p align="center"><img src="svgs/947d4611033362e2fb8e1ff4499cd83e.svg?invert_in_darkmode" align=middle width=11.50037955pt height=16.3763325pt/></p> counts the number of leaves in <p align="center"><img src="svgs/d546e0ee5a0604ca911ec7acb79e5a97.svg?invert_in_darkmode" align=middle width=14.99998995pt height=11.232861749999998pt/></p> that are descendants of <p align="center"><img src="svgs/e0e3e6abad4cf2ae029ad99ba26b464a.svg?invert_in_darkmode" align=middle width=12.34780305pt height=13.1799822pt/></p> and <p align="center"><img src="svgs/9fc3197f717b2936b45fc2f055f36421.svg?invert_in_darkmode" align=middle width=15.290342099999998pt height=16.3763325pt/></p> counts the number of leaves in <p align="center"><img src="svgs/d546e0ee5a0604ca911ec7acb79e5a97.svg?invert_in_darkmode" align=middle width=14.99998995pt height=11.232861749999998pt/></p> that are descendants of <p align="center"><img src="svgs/5a2ba9a87499899710029a4db6aca06c.svg?invert_in_darkmode" align=middle width=16.137765599999998pt height=13.1799822pt/></p>.  In other words, we split <p align="center"><img src="svgs/b7d41f7b047a1692fe39e0184102dfa0.svg?invert_in_darkmode" align=middle width=97.3740339pt height=13.1799822pt/></p> where <p align="center"><img src="svgs/3453608cec80e7e8afdd283db167d303.svg?invert_in_darkmode" align=middle width=18.789931049999996pt height=13.1799822pt/></p> contains <p align="center"><img src="svgs/947d4611033362e2fb8e1ff4499cd83e.svg?invert_in_darkmode" align=middle width=11.50037955pt height=16.3763325pt/></p> leaves from the descendants of <p align="center"><img src="svgs/e0e3e6abad4cf2ae029ad99ba26b464a.svg?invert_in_darkmode" align=middle width=12.34780305pt height=13.1799822pt/></p>, and <p align="center"><img src="svgs/12eeaa92ef6490c1859e62d8a9fa7751.svg?invert_in_darkmode" align=middle width=22.579891949999997pt height=13.1799822pt/></p> contains <p align="center"><img src="svgs/9fc3197f717b2936b45fc2f055f36421.svg?invert_in_darkmode" align=middle width=15.290342099999998pt height=16.3763325pt/></p> leaves from the descendants of <p align="center"><img src="svgs/5a2ba9a87499899710029a4db6aca06c.svg?invert_in_darkmode" align=middle width=16.137765599999998pt height=13.1799822pt/></p>; then (loosely speaking) we compute the maximum value of <p align="center"><img src="svgs/c8c039365996d9299eeb782e0657c5a7.svg?invert_in_darkmode" align=middle width=40.82763465pt height=17.2895712pt/></p> in terms of the maximum values of <p align="center"><img src="svgs/f6caab9c478472dcb5a5cccef1aa4850.svg?invert_in_darkmode" align=middle width=45.43951005pt height=17.2895712pt/></p> and <p align="center"><img src="svgs/b4ac2eadf9f6f2d9c9bc42667d1e2175.svg?invert_in_darkmode" align=middle width=49.229465999999995pt height=17.2895712pt/></p>.  The <p align="center"><img src="svgs/7e42a8fa9279d71ee88c5e32f3002426.svg?invert_in_darkmode" align=middle width=27.430005899999998pt height=16.3763325pt/></p> term counts distances of the form <p align="center"><img src="svgs/ca2396d058b10cdc88dc64fb34fea6d1.svg?invert_in_darkmode" align=middle width=62.186175150000004pt height=16.438356pt/></p> where <p align="center"><img src="svgs/82aea9caf1d8c523449f573e7137357b.svg?invert_in_darkmode" align=middle width=55.6505169pt height=15.645710849999999pt/></p> and <p align="center"><img src="svgs/d84dbe091c6f8107070b7e56ad844e35.svg?invert_in_darkmode" align=middle width=59.4404778pt height=15.645710849999999pt/></p>.  The <p align="center"><img src="svgs/af6013ca3adcced4e7d52c519f27f843.svg?invert_in_darkmode" align=middle width=16.785786599999998pt height=14.611878599999999pt/></p> term accounts for the fact that the <p align="center"><img src="svgs/7d6abfd7a8903d8827b35524704fd563.svg?invert_in_darkmode" align=middle width=7.710417pt height=14.0378568pt/></p> root-to-leaf paths all need to be extended by one edge.

<p align="center"><img src="svgs/9fe95515a9500cc7779b059643c7c7ce.svg?invert_in_darkmode" align=middle width=12.32879835pt height=11.232861749999998pt/></p> can be calculated by traversing <p align="center"><img src="svgs/c1d5631299f1af9861ff7a8dbee8b734.svg?invert_in_darkmode" align=middle width=11.889314249999998pt height=11.232861749999998pt/></p> in post order.

If we have an arbitrary tree, not necessarily a binary tree, then it can be converted to a binary tree as follows. Children from the original tree are encoded as a left child in the binary tree and edges to left children preserve their original weights. Remaining edges, those to right children, have 0 weight. TODO Add an image.





Distributing labelling budget
-----------------------------

We have one annotator, predicting next label costs nothing (compared to manual cost), so given a budget <p align="center"><img src="svgs/b49da7325822089835b531a5fce8b94e.svg?invert_in_darkmode" align=middle width=9.866876249999999pt height=7.0776222pt/></p>, so we can have <p align="center"><img src="svgs/b49da7325822089835b531a5fce8b94e.svg?invert_in_darkmode" align=middle width=9.866876249999999pt height=7.0776222pt/></p> iterations, in each we select only one product for manual labelling.

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