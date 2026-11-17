# Week 14 Self-Check (optional, multiple choice)

*Week 14 has no graded weekly checkpoint (checkpoints run in Weeks 1–6 and 9–13). These optional questions check ideas you will use when you build your slides. Ask about any of them in your team's meeting on Thursday.*

**Check 1 (easy).** A team's Results slide shows a reliability diagram under the title "Calibration analysis." Which title passes the title test?

A. "Calibration results"
B. "We carried out a thorough calibration analysis"
C. "When the model says 90%, it is right about 78% of the time (95% interval 74% to 82%), so its confidence is too high to use as a review threshold"
D. "Calibration: reliability diagram and expected calibration error"

**Check 2 (easy).** A team's paired analysis gives a difference of 1.5 points with a 95% interval from −0.2 to 3.2 points. Which slide title matches this evidence?

A. "The AI system is better and should be adopted."
B. "There is no difference between the models."
C. "The AI system answered 1.5 points more cases correctly, but it is not shown to be better: the 95% interval runs from −0.2 to +3.2 points."
D. "The AI system is 1.5 points better, guaranteed within the interval."

**Check 3 (harder).** In Lab 5, Qwen answered 2.9 points more questions correctly than Llama, with a task-bootstrap 95% interval from −0.6 to +6.6 points over 5,761 questions in 24 tasks. A teammate proposes collecting twice as many questions from the same 24 tasks to settle whether Qwen is better. Why would that barely narrow the interval?

A. The bootstrap already uses 2,000 resamples, so more data cannot change it.
B. Most of the uncertainty comes from how much the gap changes from task to task, and new questions from the same tasks add no new tasks.
C. McNemar's test is already significant, so the interval is not needed.
D. Accuracy cannot go above 100%, so the interval cannot shrink.
