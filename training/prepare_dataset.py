"""
training/prepare_dataset.py — gộp Jigsaw Toxic Comment (tiếng Anh) và
ViHSD/UIT-ViCTSD (tiếng Việt) thành một tập huấn luyện chung, quy về cùng
thang nhãn nhị phân toxic/not_toxic, đúng Chương I mục III.2 của báo cáo.
Không tự thu thập dữ liệu mới, chỉ dùng lại 2 nguồn công khai đã duyệt.
"""

import pandas as pd


def load_jigsaw(path: str) -> pd.DataFrame:
    # TODO(DEV): đọc CSV Jigsaw, quy các cột toxic/severe_toxic/... về 1 nhãn toxic/not_toxic
    df = pd.read_csv(path)
    label_cols = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    df["label"] = (df[label_cols].sum(axis=1) > 0).astype(int)
    df = df.rename(columns={"comment_text": "text"})[["text", "label"]]
    df = df.dropna(subset=["text"])
    return df


def load_vihsd(path: str) -> pd.DataFrame:
    # TODO(DEV): đọc ViHSD (Clean/Offensive/Hate), quy về toxic/not_toxic
    df = pd.read_csv(path)
    text_col = "free_text" if "free_text" in df.columns else "text"
    label_col = "label_id" if "label_id" in df.columns else "label"
    df["label"] = (df[label_col] != 0).astype(int)
    df = df.rename(columns={text_col: "text"})[["text", "label"]]
    df = df.dropna(subset=["text"])
    return df


def merge_and_export(jigsaw_path: str, vihsd_path: str, out_path: str) -> None:
    df_en = load_jigsaw(jigsaw_path)
    df_vi = load_vihsd(vihsd_path)
    merged = pd.concat([df_en, df_vi], ignore_index=True)
    merged.to_csv(out_path, index=False)


if __name__ == "__main__":
    merge_and_export("data/jigsaw.csv", "data/vihsd.csv", "data/merged_train.csv")
