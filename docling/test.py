import os

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    # OCRエンジンのオプションをインポート
    EasyOcrOptions,  # EasyOCR
    OcrMacOptions,  # Mac OCR (Mac専用)
    PdfPipelineOptions,
    RapidOcrOptions,  # RapidOCR
    TableFormerMode,
    TesseractCliOcrOptions,  # Tesseract (CLI)
    TesseractOcrOptions,  # Tesseract (Python)
)
from docling.document_converter import DocumentConverter, PdfFormatOption

base_dir = os.path.dirname(__file__)  # test.py の場所を基準にする
pdf_path = os.path.join(base_dir, "../data/report/SF/000010/000010_0012.pdf")
output_dir = os.path.join(base_dir, "docling_result")
os.makedirs(output_dir, exist_ok=True)

# PDF パイプラインオプションの設定
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True  # OCRを有効化
pipeline_options.do_table_structure = True  # 表構造認識を有効化
pipeline_options.table_structure_options.do_cell_matching = True  # セルマッチング有効
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE


# OCRエンジンの選択（以下から選択）
# Option 1: EasyOCR (デフォルト、最も一般的)
# ocr_options = EasyOcrOptions(lang=["ja"])

# Option 2: Tesseract (Python API)
# ocr_options = TesseractOcrOptions(lang=["ja"])

# Option 3: Tesseract CLI (コマンドライン版)
# ocr_options = TesseractCliOcrOptions(lang=["jpn"])

# Option 4: RapidOCR (軽量・高速)
# ocr_options = RapidOcrOptions(lang=["ja"])

# Option 5: Mac OCR (Mac専用、高品質)
ocr_options = OcrMacOptions(lang=["ja-JP"])  # Macでのみ利用可能

# OCRオプションをパイプラインに設定
pipeline_options.ocr_options = ocr_options

# ドキュメントコンバーターの初期化（正しい方法）
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# PDFファイルの変換
result = converter.convert(pdf_path)

# 結果の出力（例）
print("変換完了!")
print("ドキュメント内容:")
print(result.document.export_to_markdown())
# Markdownとして保存
markdown_content = result.document.export_to_markdown()
filename = os.path.basename(pdf_path).replace(".pdf", "_converted.md")
output_path = os.path.join(output_dir, filename)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(markdown_content)
print(f"Markdownファイルを保存しました: {output_path}")