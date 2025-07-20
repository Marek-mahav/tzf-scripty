import os
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table

def write_reports(metrics_df, price_df, cfg):
    out_dir = cfg["reporting"]["output_dir"]
    os.makedirs(out_dir, exist_ok=True)

    # 1) XLSX
    with pd.ExcelWriter(f"{out_dir}/metrics.xlsx", engine="openpyxl") as writer:
        metrics_df.to_excel(writer, sheet_name="Metrics", index_label="symbol")
        price_df.tail(10).to_excel(writer, sheet_name="Prices")

    # 2) PDF
    pdf_path = f"{out_dir}/metrics.pdf"
    doc = SimpleDocTemplate(pdf_path)
    data = [metrics_df.reset_index().columns.tolist()] + metrics_df.reset_index().round(4).values.tolist()
    table = Table(data)
    doc.build([table])
