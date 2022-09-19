import sys
from queue import Queue

import numpy as np

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            var_length = var.length
            words = self.domains[var]
            # create set of words whose length == variable length
            consistent_words = [word for word in words if len(word) == var_length]
            words.intersection_update(consistent_words)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        
        # check for overlap
        if not self.crossword.overlaps[x, y]:
            return revised

        words_to_remove = self.get_words_to_remove(x, y)
        # remove words from x's domain
        if len(words_to_remove) > 0:
            self.domains[x].difference_update(words_to_remove)
            revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # initiate queue if not exist
        if not arcs:
            arcs = Queue()
            for arc in self.crossword.overlaps:
                arcs.put(arc)

        while not arcs.empty():
            # consider arc if consistent
            x, y = arcs.get()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    # domain of x is empty --> problem is unsolvable
                    return False
                else:
                    # add neighbours of x to queue
                    for n in self.crossword.neighbors(x):
                        if n != y:
                            arcs.put((n, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        word_assigned = set(assignment.keys())
        return (self.crossword.variables == word_assigned)
    

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check all values are distinct -> if not distinct set of values will be shorter than set of keys
        if len(set(assignment.values())) != len(set(assignment.keys())):
            return False

        # check all values are correct length
        var_lengths = [var.length for var in assignment.keys()]
        word_lengths = [len(word) for word in assignment.values()]
        if var_lengths != word_lengths:
            return False

        # check no conflicts between neighbours
        for var in assignment:
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                if neighbor in assignment:
                    # neighbor is also in the assignment
                    i, j = self.crossword.overlaps[var, neighbor]
                    word_var = assignment[var]
                    word_neighbor = assignment[neighbor]
                    if word_var[i] != word_neighbor[j]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """        
        domain_values = list(self.domains[var])
        eliminations = {} # dict{word: nr of value ruled out}
        # for each word in var's domain count the number of eliminations
        for word in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                # consider only neighboring unassigned variables
                if neighbor in assignment:
                    continue
                words_to_remove = self.get_words_to_remove(neighbor, var, word)
                count += len(words_to_remove)
            eliminations[word] = count        
        
        # return list sorted by number of eliminations
        return sorted(domain_values, key=lambda word: eliminations[word])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # select all unassigned variables
        selected_variables = np.array([var for var in self.domains if var not in assignment])
        
        # select variables with the minimum number of remaining values
        remaining_values = np.array([len(self.domains[var]) for var in selected_variables])
        indices = np.where(remaining_values == remaining_values.min())[0]
        
        # if tie, select variables with highest degree (nr of neighbors)
        if len(indices) > 1:        
            # filter selected variables to variables with MRV
            selected_variables = selected_variables[indices]
            # variables with the highest degree (nr of neighbors)
            degrees = np.array([len(self.crossword.neighbors(var)) for var in selected_variables])
            indices = np.where(degrees == degrees.max())[0]
        
        ndx = indices[0]        
        return selected_variables[ndx]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assignment is complete -> return assignment
        if self.assignment_complete(assignment):
            return assignment
        
        # select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # iterate domain values - using least-constraining heuristic
        for word in self.order_domain_values(var, assignment):
            # if value consistent with assignment
            assignment[var] = word
            inferences = dict()
            if self.consistent(assignment):  
                # maintain arc-consistency
                inferences = self.inference(var, assignment)
                if inferences:
                    # add inferences to assignment
                    assignment.update(inferences)
                # recursively run Backtrack
                result = self.backtrack(assignment)           
                if result:
                    return result
            # delete var and inferences from assignment
            assignment.pop(var)
            for inference in inferences:
                assignment.pop(inference)

        return None


    def inference(self, x, assignment):
        """
        Returns all the inferences that can be made through enforcing arc-consistency.

        @param assignment   current assignment (dictionary)
        @param x            Variable, that last assignment was made to
        @return             inferences: dict(Variable: value) or None if AC-3 was failure
        """
        # create a queue of arcs between neighbours of var and var
        arcs = Queue()
        for neighbour in self.crossword.neighbors(x):
            arc = (neighbour, x)
            arcs.put(arc)
        
        # run AC-3, check if it wasn't failure
        result = self.ac3(arcs)
        if result is None:
            return None

        # gather inferences
        inferences = self.get_inferences_from_domains(assignment)
        return inferences


    def get_inferences_from_domains(self, assignment):
        """
        Returns inferences from the domains, i.e. variables with only one value
        that are not yet in the assignment.

        @param assignment   current assignment (dictionary)
        @return             inferences: dict(Variable: value)
        """
        inferences = {
            var:tuple(words)[0] for (var, words) in self.domains.items() # 'var:words[0]' doesn't work (TypeError: 'set' object does not support indexing)
            if var not in assignment 
            if len(words) == 1
        }
        return inferences

    def get_words_to_remove(self, x, y, word_y=None):
        """
        Returns set of values to remove from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        @param x        Variable object
        @param y        Variable object
        @param word_y   if defined, function will return list of words in domain[x]
                        that conflicts with word_y
        @return         set of values (strings)
        """
        words_to_remove = set()
        i, j = self.crossword.overlaps[x, y] # where x's ith character overlaps y's jth character
        for word_x in self.domains[x]:
            char_i = word_x[i]
            # boolean mask: element is True if characters correspond
            if word_y:
                jth_chars_corresp = [(word_y[j] == char_i)]    
            else:
                jth_chars_corresp = [word_y[j] == char_i for word_y in self.domains[y]]
            if any(jth_chars_corresp):
                continue
            else:
                words_to_remove.add(word_x)
        return words_to_remove


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
