# Week 9 lecture checks

These questions come straight from the Week 9 lectures. Checkpoint 7 uses the same reasoning with new numbers.

## After Lecture A

1. A model is right on 80% of a benchmark's questions. In one sentence, explain why that number does not tell a client whose questions differ how often the model will be right for them.

2. A benchmark has 600 questions of type A, where a model is right 85% of the time, and 200 of type B, where it is right 55% of the time. A client's questions are 40% type A and 60% type B. Compute the model's accuracy on the benchmark and its reweighted accuracy for the client.

3. For the client in question 2, compute the standard error of the reweighted accuracy and a 95% interval. Which type contributes more to the variance, and why?

4. For the client in question 2, compute Kish's effective sample size. How does it compare with the benchmark's 800 questions?

5. A fraud detector is right on 98% of legitimate transactions and 60% of fraudulent ones. On the benchmark, 30% of transactions are fraud. At the client's bank, about 5% are. Compute the detector's accuracy on the benchmark and for the client. Is the benchmark's accuracy too high or too low for this client? What must be true for the reweighted number to be right?

6. For each situation, say which part of the joint distribution of a case $X$ and its right answer $Y$ changed: $P(X)$, the mix of cases (covariate shift); $P(Y)$, the mix of right answers (label shift); or $P(Y \mid X)$, what the right answer is for a given case (concept shift).
   a. A homework helper's client asks more geometry questions and fewer algebra questions than the benchmark does.
   b. A spam filter's client receives three times as much spam as the benchmark contains.
   c. A client's moderators call a comment "toxic" in situations the benchmark's raters would not.

7. A classifier tells benchmark photos from a client's photos with 90% accuracy, where 50% would be chance. Which statement does this support?
   A. The model's accuracy on the client's photos is lower.
   B. The two sets of photos differ in a way the classifier can detect.
   C. Reweighting by the classifier's output will give the client's accuracy.
   D. The benchmark's labels are wrong.

8. A partner asks how well a model will do on its own new cameras. Should you resample photos within each of your cameras, or whole cameras? In one or two sentences, say why, and say when the other choice would be right.

9. Using your answers to questions 2 and 3, write three or four sentences for the client. Name both populations, give the reweighted accuracy with its interval, state the assumption it rests on, and say what data would check it.

## After Lecture B

10. Rewrite this project question so that it names a decision and the quantity that answers it: "How accurate is the speech-to-text system?" The client is a call center deciding whether to stop paying people to type call notes.

11. A team reports its AI system's accuracy on all 1,000 analysis cases and its fitted baseline's accuracy on a 250-case test split, then subtracts the two to compare them. What is wrong with that comparison, and how should the team fix it?

## From Lab 9

12. In Lab 9, a quarter of hospital 5's patches were bluer than every patch in the benchmark. The reweighting put them in the "most blue" group anyway. What did that assume about those patches, and why can the benchmark not check it?

13. In Lab 9, the model was right on 91% of benchmark patches, and reweighting to hospital 5's colors also gave about 91%. Hospital 5's own labels gave 85%, and its tumor patches were caught 77% of the time compared with 89% on the benchmark. Why could reweighting by color not predict this? With only 10 slides at hospital 5, how sure can you be that the model does worse there, and why do the intervals resample slides instead of patches?

