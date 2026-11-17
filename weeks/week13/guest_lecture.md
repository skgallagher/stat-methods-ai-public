# Week 13: Guest lecture by Carol J. Smith

Tuesday, April 13, 11:00 am to 12:20 pm, GHC 4307. There is no class on Thursday, April 15, because of Spring Carnival.

## Our guest

Carol J. Smith leads the AI Trust Lab in the AI Division of Carnegie Mellon's Software Engineering Institute (SEI), where Carol is a principal research scientist in human-machine interaction, and teaches in CMU's Human-Computer Interaction Institute. Carol's work is on building AI systems that people can trust: who stays in control of a decision, who is responsible when the system is wrong, and how a team finds problems before the system reaches the people it affects.

The Department of Defense adopted ethical principles for AI in February 2020. Carol is one of the five authors of the Defense Innovation Unit's *Responsible AI Guidelines in Practice* (2021), which turned those principles into questions a project team answers before, during, and after building a system. Carol also gave a keynote, "Trustworthy by Design," at ICSE 2024, the main international conference in software engineering.

## Why this talk, this week

For twelve weeks we have treated an evaluation as a measurement. An accuracy is an estimate, a benchmark is a sample, and a label is one rater's reading. Every one of those numbers came from people. Crowdworkers labeled DynaSent in Week 2, experts judged the MT-Bench answers you studied in Week 12, and in your project a client decides what counts as success. Once a system is deployed, more people enter: the ones who use its output and the ones its decisions affect. Carol studies those people, and this talk is about the part of an evaluation that sits outside the data table.

## Read before class (about twelve pages)

Jared Dunnmon, Bryce Goodman, Peter Kirechu, Carol Smith, and Alexandrea Van Deusen (2021), [*Responsible AI Guidelines in Practice*](https://s3.us-gov-west-1.amazonaws.com/publicdocs.diu.mil/2021_RAI_Report-v3.pdf), Defense Innovation Unit. Read the executive summary (page 4), the three phases with their workflow figures (pages 7 to 10), and the Predictive Health case study (pages 11 and 12), in which a team plans a model that reorders the queue of chest X-rays radiologists read. Read it for two things. First, the planning questions about the task, the success metric, and the baseline, which will look familiar from your project. Second, the populations the case study's vendor tests its models on, and what happens when the deployed population differs.

Nithya Sambasivan, Shivani Kapania, Hannah Highfill, Diana Akrong, Praveen Paritosh, and Lora Aroyo (2021), ["'Everyone wants to do the model work, not the data work': Data Cascades in High-Stakes AI"](https://doi.org/10.1145/3411764.3445518), CHI 2021 ([free PDF from Google Research](https://research.google/pubs/everyone-wants-to-do-the-model-work-not-the-data-work-data-cascades-in-high-stakes-ai/)). Read Section 1, Section 4.1 with Figure 1, Table 2 on page 6, and Section 4.3.2 on pages 7 and 8. The authors interviewed 53 people who build AI systems for health care, farming, conservation, and other high-stakes uses. Read it for two things. First, how the 53 people were found, and what the percentages in Table 2 describe. Second, the point in Figure 1 where an evaluation metric would have caught each problem, or why it would not have.

If you want more of Carol's work, Carol J. Smith (2019), ["Designing Trustworthy AI: A Human-Machine Teaming Framework to Guide Development"](https://arxiv.org/abs/1910.03515), is five pages and ends with a checklist a team signs. It is optional.

## Come with a question

Carol has the session, and it may include a short activity, so sit with your project team. Each team should bring one question that connects Carol's work to its project. For example: who are the people inside our evaluation (the raters behind our reference labels, the client, the people the system's decisions affect), and what would they need to see before trusting our recommendation?

## Checkpoint 11

Checkpoint 11 opens after class on Tuesday and is due Tuesday, April 20, at 11:59 pm. About half of it comes from the two readings and about half from the talk and our discussion in class. The practice questions are in `lecture_checks.md`.
