# Heredity
### Project 2.2 for CS50's Introduction to Artificial Intelligence with Python
<br>

See presentation on implementation here: [CS50AI - Heredity](https://youtu.be/oTqD0Zzy7I8)
<br><br>

## Task
Write an AI to assess the likelihood that a person will have a particular genetic trait.
```
$ python heredity.py data/family0.csv
Harry:
  Gene:
    2: 0.0092
    1: 0.4557
    0: 0.5351
  Trait:
    True: 0.2665
    False: 0.7335
James:
  Gene:
    2: 0.1976
    1: 0.5106
    0: 0.2918
  Trait:
    True: 1.0000
    False: 0.0000
Lily:
  Gene:
    2: 0.0036
    1: 0.0136
    0: 0.9827
  Trait:
    True: 0.0000
    False: 1.0000
```


## Background
Mutated versions of the ***GJB2*** gene are one of the leading causes of hearing impairment in newborns. Each person carries two versions of the gene, so each person has the potential to possess either 0, 1, or 2 copies of the hearing impairment version GJB2. Unless a person undergoes genetic testing, though, it?s not so easy to know how many copies of mutated GJB2 a person has. This is some ?hidden state?: information that has an effect that we can observe (hearing impairment), but that we don?t necessarily directly know. After all, some people might have 1 or 2 copies of mutated GJB2 but not exhibit hearing impairment, while others might have no copies of mutated GJB2 yet still exhibit hearing impairment.

Every child inherits one copy of the GJB2 gene from each of their parents. If a parent has two copies of the mutated gene, then they will pass the mutated gene on to the child; if a parent has no copies of the mutated gene, then they will not pass the mutated gene on to the child; and if a parent has one copy of the mutated gene, then the gene is passed on to the child with probability 0.5. After a gene is passed on, though, it has some probability of undergoing additional mutation: changing from a version of the gene that causes hearing impairment to a version that doesn?t, or vice versa.

We can attempt to model all of these relationships by forming a Bayesian Network of all the relevant variables which considers a family of two parents and a single child.

Each person in the family has a Gene random variable representing how many copies of a particular gene (e.g., the hearing impairment version of GJB2) a person has: a value that is 0, 1, or 2. Each person in the family also has a Trait random variable, which is yes or no depending on whether that person expresses a trait (e.g., hearing impairment) based on that gene. There?s an arrow from each person?s Gene variable to their Trait variable to encode the idea that a person?s genes affect the probability that they have a particular trait. Meanwhile, there?s also an arrow from both the mother and father?s Gene random variable to their child?s Gene random variable: the child?s genes are dependent on the genes of their parents.

Your task in this project is to use this model to make inferences about a population. Given information about people, who their parents are, and whether they have a particular observable trait (e.g. hearing loss) caused by a given gene, your AI will infer the probability distribution for each person?s genes, as well as the probability distribution for whether any person will exhibit the trait in question.



## Specification
Complete the implementations of ```joint_probability```, ```update```, and ```normalize```.
</br></br>

The ```joint_probability``` function should take as input a dictionary of people, along with data about who has how many copies of each of the genes, and who exhibits the trait. The function should return the joint probability of all of those events taking place.

- The function accepts four values as input: ``people``, ```one_gene```, ```two_genes```, and ```have_trait```.
    - ```people``` is a dictionary of people. The keys represent names, and the values are dictionaries that contain mother and father keys. You may assume that either mother and father are both blank (no parental information in the data set), or mother and father will both refer to other people in the people dictionary.
    - ```one_gene``` is a set of all people for whom we want to compute the probability that they have one copy of the gene.
    - ```two_genes``` is a set of all people for whom we want to compute the probability that they have two copies of the gene.
    - ```have_trait``` is a set of all people for whom we want to compute the probability that they have the trait.
    - For any person not in ```one_gene``` or ```two_genes```, we would like to calculate the probability that they have no copies of the gene; and for anyone not in ```have_trait```, we would like to calculate the probability that they do not have the trait.
- For example, if the family consists of Harry, James, and Lily, then calling this function where ```one_gene = {"Harry"}```, ```two_genes = {"James"}```, and ```trait = {"Harry", "James"}``` should calculate the probability that Lily has zero copies of the gene, Harry has one copy of the gene, James has two copies of the gene, Harry exhibits the trait, James exhibits the trait, and Lily does not exhibit the trait.
- For anyone with no parents listed in the data set, use the probability distribution ```PROBS["gene"]``` to determine the probability that they have a particular number of the gene.
- For anyone with parents in the data set, each parent will pass one of their two genes on to their child randomly, and there is a ```PROBS["mutation"] ``` chance that it mutates (goes from being the gene to not being the gene, or vice versa).
- Use the probability distribution ```PROBS["trait"]``` to compute the probability that a person does or does not have a particular trait.

The ```update``` function adds a new joint distribution probability to the existing probability distributions in probabilities.

- The function accepts five values as input: ```probabilities```, ```one_gene```, ```two_genes```, ```have_trait```, and ```p```.
    - ```probabilities``` is a dictionary of people. Each person is mapped to a ```"gene"``` distribution and a ```"trait"``` distribution.
    - ```one_gene``` is a set of people with one copy of the gene in the current joint distribution.
    - ```two_genes``` is a set of people with two copies of the gene in the current joint distribution.
    - ```have_trait``` is a set of people with the trait in the current joint distribution.
    - ```p``` is the probability of the joint distribution.
- For each person person in ```probabilities```, the function should update the ```probabilities[person]["gene"]``` distribution and ```probabilities[person]["trait"]``` distribution by adding ```p``` to the appropriate value in each distribution. All other values should be left unchanged.
- For example, if "Harry" were in both ```two_genes``` and in ```have_trait```, then ```p``` would be added to ```probabilities["Harry"]["gene"][2]``` and to ```probabilities["Harry"]["trait"][True]```.
- The function should not return any value: it just needs to update the ```probabilities``` dictionary.

The ```normalize``` function updates a dictionary of probabilities such that each probability distribution is normalized (i.e., sums to 1, with relative proportions the same).

- The function accepts a single value: ```probabilities```.
-   ```probabilities``` is a dictionary of people. Each person is mapped to a ```"gene"``` distribution and a ```"trait"``` distribution.
- For both of the distributions for each person in ```probabilities```, this function should normalize that distribution so that the values in the distribution sum to 1, and the relative values in the distribution are the same.
- For example, if ```probabilities["Harry"]["trait"][True]``` were equal to 0.1 and ```probabilities["Harry"]["trait"][False]``` were equal to 0.3, then your function should update the former value to be 0.25 and the latter value to be 0.75: the numbers now sum to 1, and the latter value is still three times larger than the former value.
- The function should not return any value: it just needs to update the ```probabilities``` dictionary.

You should not modify anything else in ```heredity.py``` other than the three functions the specification calls for you to implement, though you may write additional functions and/or import other Python standard library modules. You may also import ```numpy``` or ```pandas```, if familiar with them, but you should not use any other third-party Python modules.