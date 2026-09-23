# Model and dataset registry review — 2026-09-23

Public registry metadata only; no credentials inspected, terms accepted, accounts registered, weights or dataset rows downloaded. Observed candidate revisions are not an approved empirical freeze. Observed revisions and source URLs are recorded in registry-observations.json. Raw registry responses were retained locally; their hashes are included for provenance.

| Resource | Observed revision | Registry access | Declared license |
|---|---|---|---|
| meta-llama/Llama-3.1-8B-Instruct | `0e9e39f249a16976918f6564b8830bc894c89659` | manual | llama3.1 |
| mandarjoshi/trivia_qa | `0f7faf33a3908546c6fd5b73a660e0f8ff173c2f` | False | ['unknown'] |
| Salesforce/FaithEval-counterfactual-v1.0 | `e655f7c8750aabe431eeeda63fa5c019a2567b18` | False | None |
| google-research-datasets/nq_open | `5dd9790a83002ad084ddeb7c420dc716852c6f28` | False | ['cc-by-sa-3.0'] |
| Salesforce/wikitext | `b08601e04326c79dfdd32d625aee71d232d685c3` | False | ['cc-by-sa-3.0', 'gfdl'] |

## Findings and unresolved choices

- Llama-3.1-8B-Instruct: manual access gate, llama3.1 license. The model/tokenizer repository revision is observed; authenticated file access and actual tokenizer behavior remain unverified. Do not assume public metadata grants weight access. Official source: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
- TriviaQA rc.nocontext exists: train 138384, validation 17944, test 17210 rows according to metadata. These are source rows, not eligible unique questions. Answer availability, deduplication and sample IDs remain to inspect. Registry declares unknown license. Primary project page https://nlp.cs.washington.edu/triviaqa/ did not resolve licensing in this review.
- FaithEval counterfactual v1.0: 1000 test rows, fields id/question/answer/answerKey/choices/context/justification/num of options. It has no declared training split; do not use evaluation rows for tuning without an explicit held-out design. Dataset license metadata is absent. Official code repository https://github.com/SalesforceAIResearch/FaithEval declares Apache-2.0; that alone does not establish licensing for all underlying data.
- NQ-Open: candidate registry google-research-datasets/nq_open, config nq_open, train 87925 and validation 3610; metadata has no separate test split or stable question-ID column. A versioned content/row identity policy is needed before cohort selection. Source mapping to the exact upstream OOD distribution remains open.
- WikiText: both wikitext-103-raw-v1 and wikitext-103-v1 exist. Do not choose between raw/processed variants silently. Sequence length, concatenation/stride and tokenizer treatment must be fixed for comparable perplexity.
- BioASQ: official https://participants-area.bioasq.org/datasets/ lists multiple Task B editions and requires registration for training downloads. Exact upstream edition/subset has not been established; no substitute mirror selected.
- NonExist: exact source/generation protocol still unresolved.

## Next bounded task

Inspect pinned H-Neurons paper/source references for exact OOD dataset distributions and regularization C grid; separate recoverable source facts from choices requiring an explicit protocol amendment. In parallel with later preparation, model access must be verified by the account owner before a paid Pod is provisioned. No empirical execution is authorized by this review.

Validation: all five raw registry snapshots match their stored SHA-256; each observed revision is a 40-character identifier. No code changed, so the preceding 68-test result remains the last test result; tests were not rerun for metadata-only work.
