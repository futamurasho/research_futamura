import os
from pypdf import PdfReader

# # PDF が置いてあるフォルダ
# PDF_DIR = "../data/report/SF/000010"

# for fname in os.listdir(PDF_DIR):
#     if not fname.lower().endswith(".pdf"):
#         continue
#     path = os.path.join(PDF_DIR, fname)
#     reader = PdfReader(path)
#     print(f"{fname}: {len(reader.pages)} pages")


def count_pdf_pages(base_dir):
    """
    base_dir 以下の PDF をすべて走査し、
    各ファイルのページ数と合計ページ数を表示する。
    """
    total_pages = 0
    pdf_count = 0

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue

            path = os.path.join(root, fname)
            try:
                reader = PdfReader(path)
                pages = len(reader.pages)
            except Exception as e:
                print(f"WARNING: {path} が読み込めませんでした: {e}")
                pages = 0

            rel_path = os.path.relpath(path, base_dir)
            print(f"{rel_path}: {pages} ページ")
            total_pages += pages
            pdf_count += 1

    print(f"\n合計ページ数: {total_pages} ページ")
    print(f"\n合計pdf数: {pdf_count}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("使用方法: python count_pages.py /path/to/SF")
        sys.exit(1)

    sf_dir = sys.argv[1]
    if not os.path.isdir(sf_dir):
        print(f"ERROR: {sf_dir} が見つかりません。正しいパスを指定してください。")
        sys.exit(1)

    count_pdf_pages(sf_dir)
