# Week 11 lecture checks

These questions come straight from the Week 11 lectures and lab. Checkpoint 9 uses the same reasoning with new numbers.

## After Lecture A

1. A chatbot answers one question right with probability 0.8. For that question, find the chance that two answers disagree (one right and one wrong), the chance that at least one of 2 answers is right, and the chance that the majority of 3 answers is right.

2. Users of a chatbot see one answer to each question they ask. Which number should its evaluation report?
   A. pass@1
   B. pass@5
   C. The accuracy of the majority of 5 answers
   D. The best of 5 runs of the benchmark

3. For a chatbot, the between-question variance is $\tau^2=0.07$ and the within-question variance is $\sigma^2=0.14$.
   (a) What is the standard error of the accuracy from 80 questions with 5 answers to each?
   (b) What are $\rho$ and the design effect, and how many independent answers are the 400 worth?
   (c) With the same 400 calls, what is the standard error from 400 questions with 1 answer to each?

4. For the chatbot in question 3, a checked question costs as much as 40 calls, and the budget counts both. About how many answers per question are best?

4b. Every design in question 3 estimates the chatbot's accuracy without bias. Why choose the one with the smallest standard error, and when might you pick one whose standard error is slightly larger?

5. A team runs prompt A in March on 100 questions and prompt B in April on 100 different questions. Name two problems with this design, and say how to fix each.

6. Why can a check with one answer per question not estimate how often two answers disagree?

## After Lecture B and Lab 11

7. In Lab 11, 1,270 answers to 127 problems were worth only about 237 independent answers. In one sentence, why?

8. In Lab 11, the 70B model could make only 200 calls. Why did one answer to each of many problems beat several answers to each of fewer problems, while extra answers from the 8B model still helped?
