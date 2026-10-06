# Week 4 lecture checks

These questions come straight from the Week 4 lectures. The weekly checkpoint uses the same reasoning with new numbers.

## After Lecture A

1. A leaderboard reports 91.2% and 90.5% for two models on 800 test questions. About how uncertain is each score (give the $\pm$ for a 95% Wald interval)? Does the gap show that one model is better?

2. What does a benchmark accuracy estimate?
   A. accuracy on the exact test questions, and nothing beyond them
   B. accuracy on the population of questions the benchmark is meant to represent
   C. the model's accuracy on its training data

3. A system gets 29 of 30 right. Compute the 95% Wald interval. What goes wrong with it?

4. True or false: the Wilson center always lies between $\hat p$ and $1/2$. Explain using the weight the center gives to $1/2$.

5. Which interval is guaranteed to cover the true accuracy at least 95% of the time for every true value, and what does that guarantee cost?

6. A model makes no mistakes on 75 independent photos. Give a rough 95% upper bound on its error rate, and say what you would tell someone who claims it never makes mistakes.

## After Lecture B

7. A reading benchmark has 50 passages with 6 questions each, and the within-passage correlation is 0.1. What are the design effect and the effective sample size?

8. A "cluster bootstrap" accidentally resamples individual questions instead of whole passages. Will its interval be too wide or too narrow? Explain in one sentence.

9. Name one problem that a passage-bootstrap interval cannot fix.
