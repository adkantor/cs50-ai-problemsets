# Knights

Write a program to solve logic puzzles.

## Background
In a *Knights and Knaves* puzzle, the following information is given: Each character is either a *knight* or a *knave*.A *knight* will always tell the truth: if *knight* states a sentence, then that sentence is true. Conversely, a *knave* will always lie: if a *knave* states a sentence, then that sentence is false.

The objective of the puzzle is, given a set of sentences spoken by each of the characters, determine, for each  character, whether that character is a *knight* or a *knave*.

## Specification
Add knowledge to knowledge bases ```knowledge0``` , ```knowledge1``` , ```knowledge2``` , and ```knowledge3``` to solve the following puzzles.

- ```Puzzle 0``` contains a single character, **A**.
    - **A** says *"I am both a knight and a knave."*
</br></br>
- ```Puzzle 1``` has two characters:**A**and **B**.
    - **A** says *"We are both knaves."*
    - **B** says nothing.
</br></br>
- ```Puzzle 2``` has two characters:**A**and **B**.
    - **A** says *"We are the same kind."*
    - **B** says *"We are of different kinds."*
</br></br>
- ```Puzzle 3``` has three characters: **A**, **B**, and **C**.
    - **A** says either *"I am a knight."* or *"I am a knave."*, but you don?t know which.
    - **B** says *"A said 'I am a knave.'"*
    - **B** then says *"C is a knave."*
    - **C** says *"A is a knight."*