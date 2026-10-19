# Week 6 lecture checks

These questions come straight from the Week 6 lectures. The weekly checkpoint uses the same reasoning with new numbers.

## After Lecture A

1. A model gave one photo a confidence of 0.95, and its call was wrong. Does this show that the model is overconfident? Explain in one sentence.

2. Which statement says that a model is calibrated?
   A. its accuracy is above 90%
   B. among cases where it states confidence $c$, about a fraction $c$ of its calls are right
   C. its confidence is high whenever its call is right
   D. its accuracy on test data equals its accuracy on training data

3. 250 photos have average confidence 0.92, and 215 of the calls are right. The 95% Wilson interval for accuracy is [0.81, 0.90]. Is the model overconfident on these photos? Could the gap be chance?

4. A model's 1,000 photos fall into three bins:

   | Bin | Photos | Average confidence | Accuracy |
   |---|---:|---:|---:|
   | low | 100 | 0.60 | 0.60 |
   | middle | 400 | 0.80 | 0.75 |
   | high | 500 | 0.95 | 0.90 |

   Compute the ECE and the overall accuracy.

5. Two bins each hold 500 photos. In the first, average confidence is 0.70 and accuracy is 0.80. In the second, average confidence is 0.90 and accuracy is 0.80. Compute the overall average confidence, the overall accuracy, and the ECE. What would someone miss by comparing only the overall average confidence with the overall accuracy?

6. On photos that are half animals, a model gives every photo $p = 0.5$. Is it calibrated? Is it useful? Explain.

7. The true probability that a call is right is $q = 0.8$. Compute the expected Brier score if the model states 0.8, 1.0, or 0.6. Why can't accuracy tell a model that states 0.8 from one that states 1.0?

8. Of 1,000 photos, 400 have confidence of at least 0.9, and 20 of those 400 calls are wrong. Over all 1,000 photos, 120 calls are wrong. Under the rule "accept the call when confidence is at least 0.9," what share of photos does the model handle, and what is the error rate among them? A classmate reports the error rate as $20/1000 = 2\%$. What is wrong with that?

9. At some threshold the model handles 400 photos and gets 6 wrong. The 95% Wilson interval for the error rate is [0.7%, 3.2%]. The team will accept at most 3% errors. Write two sentences for the team.

## After Lecture B

10. Two threshold rules for 1,000 photos: under rule A a person looks at 600 photos and the model makes 10 wrong calls; under rule B a person looks at 300 photos and the model makes 40 wrong calls. Measuring cost in units of one person's look, which rule is cheaper if a wrong call costs $r = 5$? If $r = 15$? At what value of $r$ do they cost the same?

11. A missed animal costs 9 times as much as a false alarm. Above what probability $p$ should the team call a photo "animal"? What has to be true of $p$ for that cutoff to work as planned?

12. A team fits temperature scaling on its test photos, then shows a nearly perfect reliability diagram for those same photos. Name two problems. Does temperature scaling change which photos the model handles under the rule "the 30% it is most sure of"?

13. One language model's answer says "I'm 95% sure." Another model assigns probability 0.95 to answer B in its token probabilities. Which of these can go directly into a reliability diagram with token probabilities from other questions, and why should the two kinds not be mixed?
