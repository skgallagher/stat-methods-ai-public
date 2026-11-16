# Week 12 lecture checks

These questions come straight from the Week 12 lectures and lab. Checkpoint 10 uses the same reasoning with new numbers.

## After Lecture A

1. Two graders read 60 chatbot answers. Both mark 30 acceptable, only the first marks 9, only the second marks 3, and both mark 18 not acceptable. Find their agreement, their chance agreement, and $\kappa$.

2. On a task where 95% of answers are acceptable, an LLM judge agrees with a staff member on 94% of answers. Which conclusion is justified?
   A. The judge is right 92% of the time.
   B. The judge's $\kappa$ with the staff member could still be close to 0.
   C. The judge is better than the staff member.
   D. Agreement above 90% means $\kappa$ is above 0.9.

3. Raters of an answer have $\rho=0.25$.
   (a) What is the reliability of the average of 3 raters?
   (b) How many raters does a reliability of 0.8 take?

4. An LLM judge runs at temperature 0. Why does averaging 5 of its verdicts on the same answer not give the reliability of 5 raters?

5. A judge sees 80 pairs of answers in both orders. It picks A both times on 30, B both times on 35, the answer shown first on 11, and the answer shown second on 4.
   (a) What is the flip rate?
   (b) What is McNemar's $z$, and which position does the judge seem to favor?
   (c) Why do only the 15 flips carry evidence about the order?

6. Two LLM judges agree on essays with $\kappa=0.8$. Give one reason both could still be poor judges of essay quality, and describe an experiment that would check it.

## After Lecture B and Lab 12

7. In Lab 12, resampling questions gave a wider interval for GPT-4's $\kappa$ than resampling items. In one sentence, why?

8. In Lab 12, GPT-4's verdicts flipped least on writing questions, where experts agreed with each other least. How can a judge be consistent with itself and still disagree with people?
