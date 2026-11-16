# Week 10 lecture checks

These questions come straight from the Week 10 lectures and lab. Checkpoint 8 uses the same reasoning with new numbers.

## After Lecture A

1. Label each as an ablation, a robustness test, a sensitivity analysis, a supplementary analysis, or none of these.
   A. Report the best of ten algorithms.
   B. Reweight with two defensible groupings of the cases, both chosen before seeing results.
   C. Blur every test photo and measure accuracy again.
   D. Remove one input feature from the model and measure the drop.
   E. Report accuracy on color photos only.

2. When should the flip rule, the result that would change the decision, be written down?
   A. After seeing the alternative's result.
   B. Before running any analysis.
   C. Only if the result changes.
   D. Only for continuous choices.

3. A benchmark has two kinds of case. The model is right on 92% of kind A and 70% of kind B. A client's share of kind B, $b$, is somewhere between 10% and 30%, and the client adopts the model only if its accuracy is at least 0.85. Write the reweighted accuracy as a function of $b$, find the flip point, and say whether the decision is sensitive to the client's mix.

## After Lecture B and Lab 10

4. A reweighted accuracy is 0.91, and the client's line is 0.85. Leaving out each of three benchmark sites in turn gives within-group gaps of $-2$, $+1$, and $-3$ points. What is the tipping point $\delta^\ast$, and how safe is the decision? About how many independent labeled cases from the client would show a gap as big as $\delta^\ast$?

5. A model is right on 90% of benchmark cases. Reweighted to a client's mix, it predicts 88%. On the client's own labeled cases it is right on 80%. Split the 10-point gap into the mix part and the within-group part, and say what each part means.

6. An analyst runs four defensible analyses of the same data and reports the one with the highest lower bound. Why is the reported bound too optimistic, and what should the analyst report instead?

7. A colleague asks: "If stain color affects whether the model is right, why not just put stain color into the model?" Answer in 2 sentences.

8. Name two conditions under which you would use a reweighted accuracy without labeling any of the client's cases. Which one could you check from the client's unlabeled cases?
