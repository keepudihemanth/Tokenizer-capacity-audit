# AI Usage

## Where AI helped

AI was used as a coding and reasoning assistant during this audit.

It helped with:

- Explaining the assignment requirements and organizing the work into Parts A, B, and C.
- Suggesting small experiments to test suspected issues in `fertility.py`.
- Helping write Python scripts used to calculate and compare tokenizer metrics.
- Helping derive the KV-cache capacity calculation from the provided model specification.
- Suggesting calculations to independently verify what `reported_tok_s` represents.
- Helping structure the recommendation memos and `NOTEBOOK.md`.

All numerical claims included in the submission were checked by running the provided scripts or calculations locally. AI-generated conclusions were not accepted without an experiment or arithmetic check.

## Where AI could have misled me

AI initially suggested interpretations before the underlying data had been fully inspected. For example, possible tokenizer issues and the serving throughput mechanism were treated as hypotheses first and then tested using the provided corpus, model specification, and benchmark log.

AI also suggested some file names and project structure changes that were not necessarily required by the assignment. These were treated as organizational suggestions rather than evidence-based findings.

For this reason, I followed the evidence rule for technical conclusions: each claimed issue was tested with a reproducible command and measured result before being included in the final analysis.

## Final responsibility

I ran the experiments, checked the outputs, and verified the arithmetic used in the submission. I am responsible for the final conclusions and recommendations.