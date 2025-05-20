import pandas as pd
import zipfile
import io
import hashlib
import xml.etree.ElementTree as ET

def csv_to_zip(csv_file: str) -> bytes:
    with open(csv_file, "rb") as f:
        csv_bytes = f.read()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr(csv_file.split("/")[-1], csv_bytes)

    zip_buffer.seek(0)

    return zip_buffer.read()

def csv_to_xml(csv_file: str) -> str:
    df = pd.read_csv(csv_file)

    tag = csv_file.split("/")[-1].split(".")[0]
    root = ET.Element(tag + "s")

    for _, row in df.iterrows():
        elem = ET.SubElement(root, tag)
        for key, value in row.items():
            ET.SubElement(elem, key).text = str(value)

    return ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

def get_quantidade_total(csv_file: str) -> bytes:
    return {"quantidade": len(pd.read_csv(csv_file, index_col=False))}

def get_sha256(csv_file: str) -> str:
    with open(csv_file, 'rb') as f:
        file_data = f.read()
        sha256_hash = hashlib.sha256(file_data).hexdigest()
    return sha256_hash