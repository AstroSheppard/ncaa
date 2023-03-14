# marchmadness
Expected result for each bracket in a March Madness group

This file will take in a list of bracket entries for an ESPN group and a payout structure and output expected finish for member of that group. This is shown by a PNG with histograms showing distributions of points, rank, and money made as well as a csv with the frequency of cashing and winning for everyone. 

Will only work after round completion. 



NEW FEATURE:
og_simulate_bracket.py

generate_random_brackets.py

pick_winner.py


This tool will help you optimize your march madness bracket.

Step 1: fill out your bracket in mybracket.csv

Step1a: Fill out matchups in matchups.csv

Step 2: Use get_538.py to read in 538 probabilities. Common errors include slow updating and using wrong date to retrieve data.

Step 3: "\%run og_simulate_bracket.py sim" to simulate 50000 tournament results.

Step 4: from generate_random_bracket import do_stuff

do_stuff() will then read in ESPN's public pick percentages, and recreate random brackets which result in the same frequencies. By default, it simulate 1000 bracket pools of 25 people each (or 25000 unique brackets). It verifies that the frequencies match. LAter, we can update this to handle things like fandom (higher UVA freq) and maybe zero out 16 seed freq (some brackets are jokes are trying to be bad in the public). Saved to mock_bracket_pools.csv. This uses a good estimate, not exact.

Step 5: from generate_random_brackets import make_picks: make_picks()
Warning: this uses a lot of memory, so reduce size if necessary. It takes a bracket pool size and number of pools as input (in the code for now), uses all 50000 simulations to see EV of each bracket in each pool. It then's groups by winner, winner and final 2, winner final 2 and final 4, all of that and elite 8, round 1 alone, and sweet 16 alone and gives EV of each of those choices (you must set payout). Winner is informative, final 2 and final 4 are best balance of information and sampling. By eleite 8, it is difficult to get too many combinations of any but the most common elite 8 choices and is less useful.

For round 1 and sweet 16, is outputs the EV of each of pick and assumes that the rest of the bracket (outside of those picks) is similar enough that the comparison is valid.

Finally, you can uncomment some things to append your bracket to each pool and find it's EV on average. This tends to be surprisingly Gaussian. You can change picks by hand and see how the EV is impacted (this is more informative then the value of the pick in abstract). 

Outputs include "winnersXXXXev.csv', "mybracketX.csv', etc.

Notes.

Eventually, this simulated data can be used to train a model to take bracket, payouts, and pool size as inputs and give EV as output.
You can also fit some input (say, odds/freq**power) fit for the power that gives the best ev estimate.
In the same vain, "pick_winners.py round# power" gives an okay estimate using the above notation. Power of .4 is probably good. Use higher powers for bigger pools (100-1000).


This involved a lot of big data stuff. Numpy is very fast, and avoiding for loops is good, but too big uses a lot of memory. del np.array helps, but pandas can't be deleted so be mindful. Numpy is faster than pandas anyway. over 1 billion is a good limit. Groupby is good, pivot tables and handling indexes was necessary. A lot of dataframe manipilation and handling (to save simulations for later use instead of using immediately). 