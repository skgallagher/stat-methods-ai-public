# Week 1 practice — model bridge, boundaries, and flexibility

Complete without AI. Suggested time: 25 minutes. This is a parallel practice
problem with different numbers from HW1, not an answer key.

## 1. Intercept-only Bernoulli model

In 16 independent binary observations, 4 outcomes equal 1.

1. Write the Bernoulli likelihood and log-likelihood for the common probability
   $p$, differentiate, and find $\widehat p$.
2. If $p=\sigma(\beta_0)$, find $\widehat\beta_0$ exactly as a log ratio.
3. Explain what happens to the finite intercept MLE if all 16 outcomes are 0.

## 2. Same model class, different fit

A no-hidden-layer sigmoid model is

$$\widehat p_i=\sigma(w_0+x_i^Tw).$$

1. Apply the logit and state why this is the logistic-regression model class.
2. Explain why minimizing binary cross-entropy to its optimum gives the
   unpenalized Bernoulli MLE.
3. Now add an $L_2$ penalty. State separately whether the model class is still
   logistic regression and whether the fitted coefficients must equal the
   unpenalized MLE.

## 3. Linear decision boundary

A perceptron predicts 1 when

$$s(x)=2-x_1-2x_2>0.$$

Derive the boundary, identify the side classified as 1, and classify $(0,0)$,
$(2,0)$, and $(0,2)$. State what changes if all three coefficients are multiplied
by 5.

## 4. Bias and variance

At one $x$, suppose $p(x)=0.60$. Across repeated training datasets, Procedure A
has mean fitted probability 0.52 and variance 0.005; Procedure B has mean 0.59
and variance 0.014.

1. Compute the irreducible Bernoulli term and expected squared prediction error
   for both procedures.
2. Which procedure has lower bias? Which has lower expected squared error?
3. In two sentences, explain why “more flexible” is not enough to choose a
   procedure.

## 5. Bounded evaluation claim

A model receives frames, adjacent frames belong to trigger sequences, and the
deployment target is new camera locations. In at most three sentences, explain
why a random frame split and a camera-held-out split target different claims.
Name the expected direction of optimism without saying it is guaranteed in every
dataset.
