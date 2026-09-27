"""
training/finetune.py — fine-tune XLM-R trên tập gộp đã tạo ở prepare_dataset.py,
chạy trên Google Colab theo Chương I mục III.3. Chỉ fine-tune phần đầu phân
loại, không train model từ đầu.
"""

from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

MODEL_NAME = "xlm-roberta-base"


def finetune(train_csv: str, output_dir: str) -> None:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    # TODO(DEV): load train_csv thành Dataset, tokenize, tạo TrainingArguments,
    # chạy Trainer.train(), rồi lưu model + tokenizer vào output_dir.
    # Sau khi xong: thêm 1 dòng mới vào bảng model_version (version_tag mới,
    # f1_score đo trên tập validation trộn Anh-Việt), đặt is_current=true cho
    # bản mới và false cho bản cũ, đúng quy trình cập nhật model ở Chương V mục II.
    raise NotImplementedError


if __name__ == "__main__":
    finetune("data/merged_train.csv", "models/xlmr-finetuned")
