# Week 9 Project Work Session: Launch

*Thu Mar 18, after Lab 9. Not graded. Project requirements and grading are only in the Project Description and the Project Rubric.*

After the guided lab, the rest of class is for your team's project. Today the whole team opens its track together. By the end of class, every member should have run your track's starter notebook, and the team should have its first numbers and a first draft of the Milestone 1 outline, the problem and EDA.

Open your track's starter notebook in Colab from the course website, like every other notebook. Its first cell downloads your track's data from the course Box folder, checks that the download is complete, and unpacks it. If the download does not work, the cell tells you how to upload the zip yourself.

Every member runs the notebook on their own laptop. A team where one person types and three watch has trouble in the oral, where anyone can be asked about any part of the project.

The holdout stays sealed. Everything today uses the analysis cases. Write your answers in text cells in the notebook. Short sentences in your own words are fine; today is for shaping ideas, not polishing them.

## 1. Load your track

**Why this step:** before any number means anything, you need to know what one row is and how many rows you have.

Run the first code cell (starter section 1). It finds your track's folder or unpacks the zip, then prints how many analysis cases there are, how many are sealed in the holdout, and how the analysis cases are split into training and evaluation cases.

What is one unit in your track: a photo, a pair of responses, or a response? How many analysis units are there, and how many are in the holdout? Does anything in your track come in groups, such as two responses to one prompt or several pairs from one Reddit post? The datasheet says.

**Your answer:**

## 2. The floor, the baseline, and the AI system on the same cases

**Why this step:** the comparison at the center of your project starts here, with three systems scored on the same cases and an interval for each.

Run starter section 2. It scores the floor, the fitted baseline, and the AI system on the same evaluation cases, with Wilson intervals, and gives a paired interval for the AI system minus the baseline.

1. What does the floor predict, and how often is it right?
2. Which system is ahead, by how much, and does the paired interval include 0?
3. Why are all three scored on the same evaluation cases, rather than the AI system on all the analysis cases?

**Your answer:**

## 3. Check the AI system's outputs

**Why this step:** the cached outputs are measurements made by a fixed system and prompt. Missing rows, duplicates, or answers that could not be read change every number after this.

Run starter section 3. Is anything missing, duplicated, or unreadable? For the judge tracks, how often did the judge fail to give an answer the code could read, and how does the starter count those cases?

**Your answer:**

## 4. Look at cases

**Why this step:** in Lecture 9A, the most important finding came from looking at photos. Several of MegaDetector's "mistakes" were burst labels on photos the animal had left.

Run starter section 4. It picks cases by a fixed rule before showing them: half where the AI system is wrong and half where the baseline is wrong. Each member reads every case and writes the case note on their own. Then compare notes. Did someone see something the others missed? Is any "mistake" really a problem with the label?

**Your answer:**

## 5. Who is your client?

**Why this step:** Milestone 1 describes the population your client cares about and the population the benchmark describes, and says which way the difference would push the results. This is Tuesday's lecture on your own data.

Run the first cells of starter section 5. They use the same `accuracy_by_group` and `reweight` functions as Lab 9, and show the AI system's accuracy within each group: dish, cat or dog (or breed), subreddit, or type of instruction.

1. Which groups does the AI system do worst on, and how many cases are in each of them?
2. Decide as a team what your client's cases look like. The Project Description, Section 2, names your track's client. Edit `client_shares` to your client's mix, and write one or two sentences on where the mix comes from. A reasoned guess is fine if you say it is one.
3. Run the reweighting. How far does the client's estimate move from the benchmark's? Is that much or little, given how different your mix is and how much accuracy differs between groups? How many equally weighted cases is the estimate worth?
4. Try one other plausible mix. Does the estimate move in the same direction? This is a first sensitivity analysis, the topic of Week 10.
5. Name one way your client's cases could differ that no reweighting can capture: a change in the link between a case and its label.

**Your answer:**

## 6. Check with another team

Pair with a team on a different track. Each team reads its draft population paragraph aloud, and the other team asks three questions. Which population is the number about? Which way is the error likely to go, and why? What data would settle it?

If the other team cannot answer one of those from your paragraph, the paragraph needs another sentence.

## 7. Start the Milestone 1 outline

Finish the population paragraph at the end of starter section 5. Then fill in what you can of starter section 6, which is laid out as the Milestone 1 outline: the problem, who the numbers are about, EDA, ideas for the analysis, and open questions.

Most of it comes from today. Your results from sections 1 to 4 and your case note are the start of the EDA, and your population paragraph is "who the numbers are about." Draft two to four questions for your client, each with the decision it informs and the quantity that answers it. A question earns its place when a different answer would change what the client does.

For the ideas for the analysis, three prompts:

- **The floor, the baseline, and the AI system.** All three are scored on the same cases, so the comparison can be paired (Week 5). What does your fitted baseline use, and what does it ignore?
- **An interval that fits your data.** What in your track comes in groups (`photo_group` in Pets, `post_id` in Human preferences, `prompt_id` in Instruction following; nothing recorded in Food)? Resample those groups (Week 4).
- **What could most go wrong.** Name the assumption a careful client would question first. In Week 10 you turn it into a sensitivity analysis.

List what you are unsure of as open questions, with who might answer each: your team, another team on your track, the course staff, or more data. Milestone 1 is due Tue Mar 23.

A pattern for the population paragraph, from Tuesday's camera-trap example:

> The benchmark is [what it contains and how it was built]. Our client's [cases] are [how they differ]. Reweighted to the client's mix of [groups], the AI system's accuracy is [estimate] (95% interval [low] to [high]), compared with [benchmark estimate] on the benchmark's mix. This assumes [the assumption]. The benchmark's number is likely too [high or low] for the client because [reason], and [data] would check it.

**Your paragraph:**

## Exit ticket

In one sentence: what is the weakest link in your team's evidence right now, and what will you do about it before Tuesday?
