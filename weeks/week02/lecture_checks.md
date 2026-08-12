# Week 2 lecture checks — individual, no AI

1. Which statement best treats a label statistically?  
   A. labels are always ground truth · B. labels are measurements produced by a protocol · C. disagreement should always be deleted · D. majority vote removes measurement uncertainty

2. A model probability vector is scored once against a one-hot majority label and once against five-rater proportions. Why can the Brier scores differ?  
   A. the model probabilities changed · B. the number of classes changed · C. the operational definition of the outcome changed · D. Brier scores cannot use soft outcomes

3. **Transfer check:** A model performs worse on model-in-the-loop Round 2 than natural Round 1. Explain why this does not identify a causal effect of collection round, and name one feature of the construction process that could explain the difference.

4. An expert and a novice label sentences separately and cannot see one another's
   answers, but they have different response probabilities. Which description is
   most defensible?  
   A. independent and exchangeable · B. independence may hold but exchangeability
   does not · C. exchangeable but necessarily dependent · D. neither can ever hold

5. **Transfer check:** Draw a sentence $X$ at random, then obtain sentiment
   forecasts from a student and two frozen classifiers on that same $X$. Explain
   how their forecasts can be dependent marginally over $X$ even if separate
   human raters would work independently conditional on $X=x$. Why are the
   three forecasters also not exchangeable?
