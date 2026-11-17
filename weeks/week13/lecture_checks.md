# Week 13 reading and lecture checks

These questions come from the two readings and Tuesday's talk. Checkpoint 11 uses the same reasoning with new numbers and new cases.

## Before class: the readings

1. Sambasivan et al. report that 92% of the 53 practitioners they interviewed had experienced at least one data cascade.
   (a) How many practitioners is that?
   (b) The authors found participants through developer communities, mailing lists, professional networks, and personal contacts, using snowball and purposive sampling. What group of people does the 92% describe? What would you need before it described AI practitioners in high-stakes domains in general?

2. In Table 2, cascades from inadequate application-domain expertise were reported by 47.8% of the 23 participants in India and 25% of the 16 in the US.
   (a) Turn both percentages into counts.
   (b) Find the difference in proportions and its standard error, treating the two groups as independent samples.
   (c) Give two reasons, other than the sample sizes, that this comparison cannot tell you whether practitioners in the US rely less on technical expertise than practitioners in India.

3. Sambasivan et al. write that, lacking better signals, practitioners relied on accuracy, precision, or F1, "where the unit of measurement is the entire system." A team trains and tests a skin-lesion classifier on clean clinic photographs, then deploys it on phone photos taken in rural health posts. Its test accuracy is 94%. In the language of Week 9, why would that 94% fail to warn the team about the cascade that follows?

4. In the Predictive Health case study, the vendor re-evaluates a model "if the class balance changes by more than two standard deviations." The report does not say what the standard deviation is of, so suppose it is the binomial standard deviation of the weekly share of remarkable X-rays. In the testing data 10% of X-rays are remarkable, and a hospital sends 400 X-rays a week.
   (a) What is the standard deviation of the weekly share if the hospital's true rate is also 10%?
   (b) How many remarkable X-rays in one week would trip the rule on the high side?
   (c) If the hospital checks every week for a year and nothing changes, about how many weeks would trip the rule on the high side anyway?
   (d) Suppose the hospital's share of remarkable X-rays really does rise, and the model's sensitivity and specificity stay the same. Why does the rise still matter for the queue?

5. In the same case study, the team decided the system should be judged by turnaround time for treating remarkable disease, not by the model's accuracy on images. Why does that quantity fit the decision better? What would you need to estimate it that a labeled test set of X-rays cannot give you?

6. Both readings ask for a way to catch a system's errors after it is deployed. Here is a made-up example. A loan-screening model denies applications. 4% of denials are appealed, and 30% of the appeals are overturned.
   (a) If every overturned denial was a real error, what is the smallest share of all denials that were errors?
   (b) Why can't the 30% be used as the error rate among all denials?
   (c) Describe a small study that would estimate the error rate among all denials.

## After the talk

7. Pick one idea from Tuesday's talk or activity. Which step of your team's evaluation would it change (the question, the exploratory analysis, the modeling, the sensitivity analysis, or the recommendation), and how?
