"""
training/finetune.py — fine-tune XLM-R trên tập gộp đã tạo ở prepare_dataset.py,
chạy trên Google Colab theo Chương I mục III.3. Chỉ fine-tune phần đầu phân
loại, không train model từ đầu.
"""

import os
from datetime import datetime

import datasets
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from db.models import ModelVersion

MODEL_NAME = "xlm-roberta-base"


def finetune(train_csv: str, output_dir: str) -> None:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    # 1. Đọc train_csv và chia train/val (stratified 90/10)
    df = pd.read_csv(train_csv)
    train_df, eval_df = train_test_split(
        df, test_size=0.1, stratify=df["label"], random_state=42
    )

    # 2. Convert thành datasets.Dataset
    train_ds = datasets.Dataset.from_pandas(train_df, preserve_index=False)
    eval_ds = datasets.Dataset.from_pandas(eval_df, preserve_index=False)

    # 3. Tokenize nội bộ
    def tokenize_fn(batch):
        return tokenizer(batch["text"], truncation=True, max_length=128)

    train_ds = train_ds.map(tokenize_fn, batched=True)
    eval_ds = eval_ds.map(tokenize_fn, batched=True)

    # 4. Compute metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        preds = np.argmax(predictions, axis=1)
        f1 = f1_score(labels, preds, average="binary")
        return {"f1": float(f1)}

    # 5. TrainingArguments & Trainer
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    eval_results = trainer.evaluate()
    eval_f1 = eval_results.get("eval_f1", 0.0)

    # 6. Ghi ModelVersion mới vào DB
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        engine = create_engine(database_url)
        with Session(engine) as session:
            session.execute(update(ModelVersion).values(is_current=False))
            version_tag = f"xlmr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            new_version = ModelVersion(
                version_tag=version_tag,
                trained_at=datetime.utcnow(),
                training_set_size=len(train_df),
                f1_score=eval_f1,
                is_current=True,
            )
            session.add(new_version)
            session.commit()


if __name__ == "__main__":
    finetune("data/merged_train.csv", "models/xlmr-finetuned")
