# Week 1 lecture checks — individual, no AI

1. Moving a classification threshold from 0.5 to 0.8 changes which object?  
   A. fitted probability model · B. decision rule · C. target population · D. image representation

2. What is the main statistical role of the logistic baseline when the vision system is more accurate?  
   A. prove causality · B. eliminate uncertainty · C. show what documented simple information already explains · D. tune the vision system

3. **Transfer check:** Why can a random frame split overstate performance for a new camera location? Answer using the frame, sequence, and camera units.

4. **Boundary check:** Suppose $\widehat p(x)=\sigma(1+x_1-2x_2)$ and the classification threshold is 0.5. Derive the decision boundary, identify the side classified as 1, and state what changes if the threshold is raised.

5. **Exploratory-extension check:** After seeing a locked baseline's holdout score, an analyst asks AI for a new classifier and obtains a higher score on that same holdout. State one claim the analyst may make and one claim that still requires new held-out evidence.

6. **Equivalence check:** A sigmoid model has no hidden layer but is fitted with
   an $L_2$ penalty. Is its model class still logistic regression? Must its fitted
   coefficients equal the unpenalized logistic-regression MLE? Explain both
   answers.

7. **Bias–variance check:** At one $x$, $p(x)=0.50$. Procedure A has mean fitted
   probability $0.45$ and variance $0.010$; Procedure B has mean $0.49$ and
   variance $0.016$. Compute the expected squared prediction error for each and
   identify which has lower bias and which has lower expected error.
