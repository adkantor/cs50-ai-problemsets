import csv
import itertools
import sys
from numpy import prod

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set `have_trait` does not have the trait.
    """
    probs = [] # list to gather values to multiply
    for person_name in people:
        gene = get_nr_genes(person_name, one_gene, two_genes)
        trait = person_name in have_trait 
        prob_trait = PROBS["trait"][gene][trait]
        if not has_parents(people[person_name]):
            # person has no parents
            prob_gene = PROBS["gene"][gene]
        else:
            # person has parents
            father_nr_genes = get_nr_genes(people[person_name]["father"], one_gene, two_genes)
            mother_nr_genes = get_nr_genes(people[person_name]["mother"], one_gene, two_genes)
            probs_inherited_nr_genes = get_probs_inherited_nr_genes(father_nr_genes, mother_nr_genes, PROBS["mutation"])
            prob_gene = probs_inherited_nr_genes[gene]
        probs.append(prob_gene * prob_trait)

    # calculate and return product
    return prod(probs)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person_name in probabilities:
        gene = get_nr_genes(person_name, one_gene, two_genes)
        trait = person_name in have_trait
        probabilities[person_name]["gene"][gene] += p
        probabilities[person_name]["trait"][trait] += p    


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person_name in probabilities:
        sum_gene = sum(probabilities[person_name]["gene"].values())
        sum_trait = sum(probabilities[person_name]["trait"].values())
        probabilities[person_name]["gene"].update((k, v / sum_gene) for k, v in probabilities[person_name]["gene"].items())
        probabilities[person_name]["trait"].update((k, v / sum_trait) for k, v in probabilities[person_name]["trait"].items())


def has_parents(person):
    """
    Returns true if person has parents.
    """
    return (person["father"]is not None and person["mother"] is not None)


def get_nr_genes(person_name, one_gene, two_genes):
    """
    Returns number of mutated genes of person.
    """
    return  (
        2 if person_name in two_genes else
        1 if person_name in one_gene else
        0
    )


def get_probs_inherited_nr_genes(father_nr_genes, mother_nr_genes, prob_mutation):
    """
    Returns probabilities for inheriting {0, 1, 2} mutated genes from parents 
    """
    prob_from_father = (
        1 - prob_mutation if father_nr_genes == 2 else 
        0.5 if father_nr_genes == 1 else
        prob_mutation
    )
    prob_from_mother = (
        1 - prob_mutation if mother_nr_genes == 2 else 
        0.5 if mother_nr_genes == 1 else
        prob_mutation
    )
    probs = dict()
    probs[0] = round((1 - prob_from_father) * (1 - prob_from_mother), 4)
    probs[1] = round((1 - prob_from_father) * (prob_from_mother) + (prob_from_father) * (1 - prob_from_mother), 4)
    probs[2] = round((prob_from_father) * (prob_from_mother), 4)
    return probs    


if __name__ == "__main__":
    main()
