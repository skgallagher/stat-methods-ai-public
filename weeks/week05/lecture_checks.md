# Week 5 lecture checks

These questions come straight from the Week 5 lectures. The weekly checkpoint uses the same reasoning with new numbers.

## After Lecture A

1. Two models answer the same 600 questions. Both get 410 right, only A gets 35 right, only B gets 52 right, and both get 103 wrong. Compute $\widehat\Delta = \hat p_B - \hat p_A$ in percentage points, and McNemar's $z$. Is the difference significant at the 5% level?

2. When two models answer the same questions, which questions decide which model is more accurate?
   A. the questions both got right
   B. the questions both got wrong
   C. the questions where they disagree
   D. all questions, counted separately for each model

3. A pilot gives model A 10 questions and model B 10 different questions. A gets 9 right and B gets 5 right. Which exact test fits, and what does it hold fixed?

4. A smaller model has $\widehat\Delta = -0.3$ points against the current model, with a standard error of 0.4 points. The margin is 1 point. Is the smaller model shown to be non-inferior? Are the two models shown to differ?

5. In one sentence, why is the null hypothesis of a non-inferiority test "the new model is worse by at least $\delta$" rather than "the two models are equally accurate"?

6. A team sees a one-sided lower bound of $-1.3$ points and then sets its margin at 1.5 points. What is wrong with that?

## After Lecture B

7. Why does the task bootstrap resample whole tasks instead of single questions? And why does it keep both models' results for each question together?

8. A team tries ten prompts that are equally good and reports the best one's accuracy. Will the reported number tend to be too high, too low, or about right? Would scoring all ten prompts on the same questions make the problem larger or smaller?

9. A blog post reports the three tasks where its model beats a rival by the most. Describe one check that would show whether that advantage holds up.

10. Name two costs of running a model other than accuracy, and one pair of costs that cannot be chosen separately.
