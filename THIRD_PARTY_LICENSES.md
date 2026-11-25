# Third-Party Licenses & Model Attributions

Toxic-Mod-Bot builds upon open-source libraries and pretrained NLP models. Respect each upstream project's license and terms when redistributing or deploying:

## Pretrained NLP Models (Hugging Face)

| Model | Purpose | Upstream Source |
|---|---|---|
| `xlm-roberta-base` | Multilingual transformer backbone | https://huggingface.co/FacebookAI/xlm-roberta-base |
| `thong7d/vihsd-xlmr-base-hate-speech` | Vietnamese hate speech & toxicity classification | https://huggingface.co/thong7d/vihsd-xlmr-base-hate-speech |
| `EIStakovskii/xlm_roberta_base_multilingual_toxicity_classifier_plus` | Multilingual/English toxicity classification | https://huggingface.co/EIStakovskii/xlm_roberta_base_multilingual_toxicity_classifier_plus |

## Key Python & Runtime Dependencies

- **`discord.py`** — MIT License
- **`FastAPI`** & **`Pydantic`** — MIT License
- **`Uvicorn`** — BSD-3-Clause License
- **`SQLAlchemy`** — MIT License
- **`aiohttp`** — Apache-2.0 License
- **`PyTorch`** — BSD-3-Clause License
- **`Hugging Face transformers`** — Apache-2.0 License
- **`psycopg2-binary`** — LGPL-3.0-or-later License (dynamically linked Python wheel)
- **`python-dotenv`** — BSD-3-Clause License
- **`PostgreSQL 15`** (`postgres:15-alpine`) — PostgreSQL License

Users deploying fine-tuned weights with Jigsaw or ViHSD datasets are responsible for reviewing those respective dataset terms before public redistribution of trained model artifacts.
