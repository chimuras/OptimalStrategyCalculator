OptimalStrategyCalculator

Background
This assignment is the kind you can expect if you work in an actuary, e.g. calculating expected return and assessing risk. Since Easy Blackjack is a game of chance, short term result may fluctuate and not be representative of the expected value of playing the game long term. There are two main methods for measuring expected value of a game: 1) by repeating a random experiment many times until the arithmetic mean of the values in the experiments converges to the expected value, and 2) by calculating it mathematically.

If you are unfamiliar with the term probability and expected value, you should review these two concepts before continuing. We suggest two YouTube videos to help you get started quickly: Probability and Expected Value.

In assignment 1, you developed a program that can estimate expected value of the game (i.e. player advantage) through repeated trials. In this assignment, you will come up with the optimal strategy table and calculate the player advantage associated with it. Fortunately, you can double check and/or debug your calculation by using your assignment 1 solution and compare the result with the theoretical player advantage that you have calculated.

Unlike in a real casino, we will be using an infinite shoe, meaning that the probability of receiving any card on the next draw remains constant and independent (e.g. probability of receiving an ace is always 1/13). This property simplifies our calculation. In the real world, removing a card would reduce the probability that a card of the same value can be drawn. For example, receiving an ace would mean that there is one fewer ace left in the shoe.

main.py: contains the main function and functions to print the result that you return. You should not change this file, but do try to understand what it's doing. Note that it imports easybj.py as a module. Our tester will also import your version of easybj.py as a module to mark your solution.
table.py: you will change this file to implement a two-dimensional, spreadsheet-like table, as part of the first milestone.
easybj.py: The meat of the assignment. It contains some basic definitions to help you start the assignment. You will have to add substantial code to finish the assignment, but as mentioned, you can do it in steps. You may also add more files and have this file import them, if it helps you organize your work better.
Approach
If you have not done so already, you should go back to assignment 1 and make sure you still have a solid understanding of the rules of Easy Blackjack. In this assignment, the same rules of the game still applies.

At a high level, we will use divide and conquer to break down the problem into smaller subproblems. For every possible action in Easy Blackjack, there is an associated expected value (EV). For example, the EV for surrendering is always -0.5, because you lose half of your bet when choosing the action. The optimal action, in each situation, is thus the action that yields the highest EV. For example, you have hard 19 versus dealer hard 20, the expected value of each action is as follows:

Action	EV
Hit	-0.768
Double	-1.538
Stand	-1.000
Surrender	-0.500
Don't worry about where these numbers come from for now. In the table above, we can see that surrender is the best option because you lose the least amount of money. Stand, for example, always results in losing the entire bet since the dealer will not hit hard 20 and your hard 19 loses to hard 20.

Now, it may become clear what the subproblems are: finding the EV of each action for every combination of player's hand and dealer's hand. For the purpose of this assignment, we call each specific combination of player/dealer hands an encounter. Once you calculated all of them, then you can determine the optimal action for every step of the game. We call the result of this set of calculations an "EV Table".

Fundamentally, there are two types of actions: terminal versus non-terminal. Terminal actions are ones where you may no longer take any more actions, i.e., surrender, stand, double, or split aces. Non-terminal actions in Blackjack are hit and split non-aces hands.

To calculate the EV tables for terminal actions, you simply need to take the action, let the dealer take his/her actions (if necessary, e.g. for surrender, dealer wins automatically), then you compare hands. For non-terminal actions, you still need to first take the action (e.g., hit). However, since the action is non-terminal, then what happens after the initial action if there are further actions (i.e., you did not bust nor did you reach 21, at which you stand automatically)?

The answer is that you should take the optimal action, meaning you are picking the best available options after the initial action based on the expected value of each action. This is logically sound because our objective is to maximize expected value, and thus every action we take should always return the highest expected value out of all available actions. If you do not know which action is optimal, then you will need to solve the subproblems (calculating the EVs of all actions) before you can solve this problem (choosing the optimal action).

Stand EV
The easiest EV table (besides surrender) to calculate is for standing. Since the player won't take any more cards, the points for his/her hand is fixed. However, the dealer may take more cards. Therefore, the EV of standing is the weighted average of all outcomes after the dealer is done. For example, if you stand on hard 18 against the dealer's hard 16, the following outcomes are possible:

Dealer	Outcome	Probability	EV
17	+1	1/13	1/13
18	0	1/13	0
19, 20, 21	-1	3/13	-3/13
bust	+1	8/13	8/13
Here, observe that the dealer can only hit one more card before standing (since his/her points will go up by at least 1, i.e. receiving an ace). The EV of each outcome is the outcome i × pi, where the sum of pi is equal to 1. Finally, the EV standing on hard 18 against dealer's hard 16 is the sum of the EV of all possible outcomes, which is 6/13 or 0.462.

Of course, if the dealer has a low starting hand, then it is possible that the dealer will hit multiple times. In this case, you will need recursion and dynamic programming to help you solve the problem more elegantly. Since you should already be familiar with recursion, we will explain dynamic programming and how it works.

Dynamic Programming
Dynamic programming is an optimization technique where the result of a function is cached (saved) so that the cached result is returned on future invocation. This technique will greatly speed up the calculation by avoiding redundant and possibly expensive recomputation. There are some restrictions as to when dynamic programming can be used (i.e. the function must be "pure" -- see lecture note for more thorough explanation). For our purposes, you only need to know that the function may not depend on any mutable non-local variables (constant ones are fine).

Continuing from previous example, suppose this time the dealer has hard 15 (the player's hand is not relevant), and we want to calculate the probability distribution F(hard 15) for all possible points that the dealer ends with. We would arrive at the following table:

Next Card	Dealer	Probability
A	16	1/13
2-6	17-21	5/13
7-K	bust	7/13
There is a 1/13 chance that the dealer gets an ace, where he/she would have to keep hitting. However, from previous example, we already calculated F(hard 16)! Therefore, if we have saved the result for F(hard 16), we can use it immediately and merge the two tables together, where F(hard 15) = 1/13*F(hard 16) + F(hard 15|not ace) for the following final table.

Dealer	Probability
17	1/13 + 1/13 * 1/13
...	...
21	1/13 + 1/13 * 1/13
bust	7/13 + 1/13 * 8/13
A general suggestion for this assignment is make use of the assert function to make sure your assumptions hold. Your program will crash if the assertion fails, which allows you to debug the problem immediately. For example, the sum of the probabilities in all dealer probability tables should be equal to 1. Assuming you are using a Python dictionary to store the table, you can check this using the following snippet of code:

# 
# use math.isclose() for Python 3.5 or later
# use this for earlier versions of Python
#
def isclose(a, b=1., rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)    

def make_dealer_table(table):    
   # ...
   # make sure the probabilities add up to 1
   assert(isclose(sum(table.values()), 1.0))
Lastly, we would save the result for F(hard 15) so that future calculation that uses it does not require recomputation. There are many opportunities to take advantage of dynamic programming in this assignment, and you will see as you continue reading.

Question: How many dealer probability tables do you need to complete the stand EV table?

Hit EV
Correctly calculating the Hit EV table requires that you first complete the Stand EV table. The reason is that the EV for hitting depends on the optimal action between hitting and standing, i.e. it is a non-terminal action. Let's suppose you hit on hard 17 against dealer's hard 18. Your possible outcomes are as follows:

Player	Probability	Outcome	EV
18-20	3/13	?	?
21	1/13	+1	1/13
bust	9/13	-1	-9/13
You may be asking, why is the outcome of achieving 18 to 20 points unknown? It is because the algorithm is unsure whether it is better to hit or stand after the initial hit, for example, on hard 20 against dealer's hard 18. On the surface, it seems obvious that you would stand in this case, but there are many other situations where it may be a close call. Therefore, your algorithm must cast aside all doubt and verify that it is indeed better to stand than to hit, or vice versa.

There are always two base cases in the recursion where you would stop hitting: arriving at 21 points or busting. In the above example, hitting on hard 20 results in an EV of 1/13 - 12/13 (only an ace will save you) = -11/13. On the other hand, standing on hard 20 guarantees a win because the dealer does not hit hard 18, so it's EV is +1.000. In this case, it is now clear that you should pick stand and not hit.

Both memoisation and dynamic programming can be effective for calculating hit EV. Using memoisation, you would make the initial hit, and for all subsequent encounters, recursively calculate the hit EVs if they are not in the hit EV table, or just use the value straight from the table and compare with the stand EV, which you have already calculated. For dynamic programming, you would iterate through all hands, starting from the base case (hard 20), and ending at hard 4.

Double EV
Since doubling down is a terminal action, it is very similar to stand, except you would hit before you stand, making it possible that you bust in the process. Otherwise, the algorithm is similar, except the expected value is doubled since the player is risking twice the amount of money to take this action.

Split EV
Because split is a non-terminal action, except in the case of splitting aces, again, you will need to make the optimal decision after the initial split occurs. However, because of the hand limit of up to 4, using recursion and memoisation may not be intuitive. Therefore, we suggest that you use dynamic programming, where you start from the smallest subproblem and work our way up.

Assuming you have already completed all other tables, then split EV's base subproblem is deciding the optimal action after you cannot split anymore, either because the hand cannot be split or the hand limit has been reached. At this point, the valid actions remaining are hit, double, or stand. Therefore, using the existing tables, you can calculate a base table for splitting. You should use STAND_CODE for the ylabels of this table since one of the actions includes standing and none of the actions involves splitting (you can't split anymore!).

One complication of splitting is dealing with the many ways where the hand limit can be reached. Fortunately, it is actually not an issue you need to worry about, because unlike in assignment 1, we are exploring all possible outcomes of having N hands. As such, how we arrived at N hands has no impact on the expected value having N hands.

As an example, suppose you have 99 and 99. Assuming the hand limit is only 3, you may only split one more time. Now, does it matter which of the 99 you split? No. Because the expected value of splitting the first 99 and the second 99 is exactly the same. With this insight, then the problem of splitting up to 4 times is a lot more tractable. While you are going through the set of hands that can result from a split, always split a hand as long as the hand limit has not been reached. So in the case where the initial XX is split into XX1 and XX2, you should assume that both of them will be split, meaning that no subsequent split after the two resplits are possible.

The only situation that you have to worry about is when you split into two hands, both of which can be split again, but there's only room for one more. For example, 880 splits into 8T and 881, and 881 is split into 882 and 883. In this case, one of the 88 cannot be split again and must be treated as base case.

Since there are multiple levels after the initial split to consider, you will actually need a total of 4 tables for the split action. The base case table (discussed earlier), split1, split2, and split3, where the subscript of each split table is the number of hands remaining that can be split. The split3 table represents the initial split from one hand, and is the one that the tester expects. split3 will include the EV for splitting AA, whereas split2 and split1 should not, since you are not allowed to resplit AA.

Player Advantage
Once you have calculated the EV of all possible actions for all combinations of hands, you would be able to generate a compact table of the optimal actions and their associated EV. To calculate the player advantage, you need the weighted average of the optimal EV of all possible starting hand combinations (sum of pi pj EVij, where pi is the probability of the player's starting hand i, and pj is the probability of the dealer's starting hand j).

Solution Requirements
To help you with this assignment, we have broken it up into multiple milestones. The program will take zero or more arguments, with the argument being the name of the table that you wish to print. For example:

python3 main.py stand optimal
This will print both the stand EV table and the optimal EV table. Partial marks will be given for completing some of the milestones. The list of all accepted arguments are as follows:

initial: print the initial probability table (see subsection for more detail)
dealer: print the dealer probability table (see subsection for more detail)
stand: print the stand EV table
hit: print the hit EV table
double: print the double EV table
split: print the split EV table
optimal: print the optimal EV table
strategy: print the strategy table
advantage: print the theoretical player advantage
If no arguments are given, the program will print everything. Note that all of the argument parsing has been done for you. You just need to produce the correct results for each of the milestone.

Table class
The first milestone of the assignment is to complete the implementation for table.py. In the file is an incomplete implementation of an ordered, homogeneous, two-dimensional table, similar to an spreadsheet. The table takes a 2-tuple (a tuple with two elements) and either raises an error or returns the value in the corresponding cell. A cell is to a spreadsheet (2D) what an element is to a list (1D). The 2-tuple is in the form (y, x), where y is the row name and x is the column name. For example, table["a","m"] will return the cell value for row a column m. Let's now describe the interface of the Table class.

Table.__init__(self, celltype, xlabels, ylabels, unit="")
celltype: the data type of each cell, e.g., str, int, or float. It is an error to set a cell with a value that is not specified cell type.
xlabels: a sequence of all x-axis labels (i.e. column names) accepted by the table.
ylabels: a sequence of all y-axis labels (i.e. row names) accepted by the table.
unit: this argument is used to print the table. You do not need to do anything about it.
For example, the table Table(str, "abcd", range(1,5)) will create the following table:

  a  b  c  d
1 -- -- -- --
2 -- -- -- --
3 -- -- -- --
4 -- -- -- --
Notice that the cell values are "empty", that is because their values by default is set to None unless you set it. For example, table[3,'b'] = "HI" will update the table:

  a  b  c  d
1 -- -- -- --
2 -- -- -- --
3 -- HI -- --
4 -- -- -- --
You must create a suitable data structure to store data for the table, and implement all operations supportd by the index operator: get, set, and delete.

__getitem__(self, idx): return the cell value given a valid 2-tuple, or None if the cell is empty.
__setitem__(self, idx, val): set the cell value to val given a valid 2-tuple. Note that type checking on val is already done for you.
__delitem__(self, idx): set the cell value to None given a valid 2-tuple.
Hand class
We provide you the skeleton code for the hand class in easybj.py, which currently stores the cards that are in the hand and specifies whether the hand belongs to player or dealer. With this, it is enough for you to complete an important method, Hand.code, which will be used throughout this assignment to fill the table.

For the purpose of this assignment, the code of a hand represents its strength and potential. It comes in three forms: hard hands, soft hands, and split hands. For hard hands, the code is the score of the hand. We define the score of a hand to be equal to the point value of the hand, except that the score is zero if the hand is busted. This simplifies comparing hand strength using integer comparison. As an example, the code '15' represents hard 15. For soft hands, it will start with an ace 'A'. For example, 'A6' denotes soft 17, and 'A9' denotes soft 20. Note that the actual hand can have more cards than what the code depicts. For example, A45 is also soft 20. If the point value of the hand is 21, then if it is also blackjack, the hand code is 'BJ', otherwise it is '21', regardless of whether it is hard or soft. Lastly, split hands are always two of the same number or letter, for example, 'AA', '55', or 'TT'. Remember that 'AA' is both a soft hand and a split hand.

Hand code can vary based on whether split is possible and who owns the hand. In the first case, if split is not possible, then the hand code is the correponding hard or soft hand code. For example, '22' becomes '4', and '99' becomes '18'. However, 'AA' remains 'AA' since it has dual meanings. In the second case, if the hand belongs to a dealer, then there are two adjustments. 1) the dealer never splits, so he/she does not use any split codes. 2) the dealer treats soft 18 or above as hard 18, so 'A7' or higher becomes '18' and higher, respectively.

Your next milestone is to complete Hand.code according to the above specificaiton. Once this is done, it will automatically finish the implementation for calculating the initial probability table. This table shows the probability of receiving a specific hand against a specific dealer hand. You can see it via the following command:

python3 main.py initial
At this point, you may have already noticed how these codes are used by the table. The x-axis is a list of all possible starting hands for the dealer, and the y-axis is a list of all possible hands for the player for a particular situation. At the top of easybj.py are a list of codes. For example, INITIAL_CODE is a list of player's hand code for the initial deal. We will explain what other lists are used for in the next few subsections.

Dealer Table
The dealer probabilities table is a collection of subtables that contain the exact probability of each dealer outcome for a particular dealer starting hand. For example, if the dealer starts with hard 17, then there would only be one entry in the subtable: 17: 1.000, since the dealer does not hit hard 17 or higher. You will need this table to be able to complete the stand EV table (it is also possible to complete both tables together using memoisation technique instead of dynamic programming).

The format of the dealer table is different from other EV tables: it is a dictionary of dictionaries. At the top level, the key is the dealer's starting hand code and the value is the associated subtable (also a dictionary). At the bottom level, the dictionary stores each outcome in score (using zero for busted hands) and the value of each outcome is its probability. Use the methodology as described in the Approach section to complete this table. Below is out of the example output for dealer hard 16:

Dealer 16
 0: 0.615385  17: 0.076923  18: 0.076923  19: 0.076923  20: 0.076923  21: 0.076923
EV Tables
You will need to produce an EV table for each of the actions: stand, hit, double, and split. Note that surrender is not necessary since all entries will be filled with -0.5. The tables have already been initialized for you in the Calculator class constructor. Your task is to populate the cells of each table with the correct expected value for each player/dealer encounter. Notice that these tables ignore the situation if either the player or dealer (or both) has blackjack. This is done mainly to compact the table since the game ends immediately and no actions need to be taken. You should study how the initial probability table was populated and use a similar method to work on the other tables.

There are two irregularities worth mentioning in these tables that may help you gain a better understanding of the process. First, the stand table has an extra entry, 21, for the player. While the player stands on 21 automatically, the game continues and the player is not guaranteed to win in this situation (e.g., if the dealer also gets 21). Second, the split table only contains entries for split hands. This may be more obvious since all other hand types cannot be split. You should return the initial split table, as described in the Split EV section, and not the resplit tables.

Lastly, for the optimal table, as described in the Approach section, you will need to compare all available actions (including surrender) for each player/dealer encounter and choose the one with the highest expected value.

Strategy Table
This part can be done as part of calculating the optimal EV table. Instead of entering numbers into the table, you enter the exact action that should be taken for each encounter. For double and surrender, an alternative action (hit or stand only) needs to be specified in case the primary is unavailable. Split does not need an alternative action since the reader of the strategy table should instead look up the hand as a hard total. The format of the strategy table is the same as described in assignment 1.

Player Advantage
Calculate the theoretical player advantage using the optimal EV table and the initial probability table, as described in the Approach section.



point: refers to the point value of the hand. For example, 88 is 16 and 999 is 27 (which is busted)
score: refers to the relative strength of the hand when compared with another. Score and point are the same for a hand that has not busted. If a hand is busted, it's score is zero.
code: a two character name used to signify the strength and the potential of the hand.
encounter: a player having a particular hand versus the dealer's particular hand.



