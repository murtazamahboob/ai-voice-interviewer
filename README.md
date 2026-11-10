# AI Voice Interviewer — Mock Job Interviews by Voice

An **AI voice interviewer that conducts mock job interviews by voice** — it asks structured questions, listens through an offline tone codec, scores every answer on a transparent rubric, adapts its follow-ups to how strong the answer was, and ends with a hire recommendation. No microphone, no network, no API key.

**Verified result (deterministic, reproduced in a fresh venv): 20/20 tests pass, scripted Python-developer demo scores 93.0/100 — "Strong hire". Per-question: 95, 94, 98, 85.**

## Why this project is different

- **It interviews, it doesn't just chat.** Unlike a general voice assistant, this is a structured interview: 3 roles (Python Developer, Data Analyst, ML Engineer), 4 core questions each, one question at a time, with a scored report at the end.
- **The follow-ups adapt.** A strong answer (≥70) earns a stretch question; a weak answer (<40) gets a scaffolded follow-up with a hint; a good follow-up can rescue a weak first answer by up to +10 points. Tested, not just claimed.
- **The scoring is transparent, not a black box.** Every answer is scored 0–100 as keywords (40) + depth (25) + concrete examples (20) + structure (15), and the report lists exactly which keywords each answer missed — so the candidate knows what to practise.
- **It really hears and speaks — offline.** A tone codec (`src/interviewer/audio.py`) encodes each character as a sine tone and decodes it back by spectral peak-picking, so the full ask → listen → score loop runs end to end with no mic, no cloud STT/TTS and no API key.

## Demo result — Python Developer

| Question | Score | Band | Missed keywords |
|---|---:|---|---|
| py-1 — lists vs tuples | 95 | Strong | none |
| py-2 — Python memory / GC | 94 | Strong | none |
| py-3 — design a REST API | 98 | Strong | none |
| py-4 — a hard bug you found | 85 | Strong | debug |

Overall **93.0/100 — Strong hire**. Only gap in the demo: the word "debug" in question 4.

## Installation

```bash
git clone https://github.com/murtazamahboob/ai-voice-interviewer.git
cd ai-voice-interviewer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Full demo: scripted Python-developer interview + report
python examples/demo.py
# -> outputs/demo_report.md, outputs/scores.json, outputs/first_question.wav

# Your own interview: pass answers as JSON (question id -> spoken answer)
interviewer interview --role data-analyst --answers '{"da-1": "I would first check for missing values..."}'

# Another role
python examples/demo.py  # demo defaults to python-developer; use the CLI for other roles
interviewer interview --role ml-engineer --answers '{"ml-1": "Overfitting is when..."}' --followups '{"ml-1": "..."}'
```

## Example output

```
role: Python Developer
py-1: 95/100 (Strong)
py-2: 94/100 (Strong)
py-3: 98/100 (Strong)
py-4: 85/100 (Strong)
overall: 93.0/100 — Strong hire
report=outputs/demo_report.md
```

## How it works

```
question ──▶ tone codec (text → audio) ──▶ candidate answer (audio)
                                                          │
                                              decode → scored answer
                                                          │
                        stretch / scaffold / standard follow-up (by score)
                                                          │
                                              report + hire recommendation
```

- **Audio** (`src/interviewer/audio.py`): tone codec, energy VAD, WAV writer.
- **Questions** (`src/interviewer/questions.py`): 3 roles × 4 questions, each with keywords and three follow-ups.
- **Scoring** (`src/interviewer/scoring.py`): transparent 0–100 rubric + bands + hire recommendation.
- **Interview** (`src/interviewer/interview.py`): state machine — ask, listen, score, follow up, report.
- **CLI** (`src/interviewer/cli.py`): `interviewer demo` / `interviewer interview`.

## Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
# 20 passed
```

Tests cover the codec round-trip, VAD, the rubric (strong / empty / short answers, bands, recommendations), the question bank, the adaptive follow-up branches, the follow-up rescue, determinism of the demo, and report generation.

## Project structure

```
ai-voice-interviewer/
├── src/interviewer/    # audio.py, questions.py, scoring.py, interview.py, cli.py
├── tests/              # test_audio.py, test_scoring.py, test_questions.py, test_interview.py (20 tests)
├── examples/           # demo.py (scripted interview + report)
├── outputs/            # demo_report.md, scores.json, first_question.wav (generated, not committed)
├── README.md
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## License

MIT — see [LICENSE](LICENSE).
