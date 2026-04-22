import pandas as pd
import re


def normalize_code(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text == "":
        return None
    text = " ".join(text.split())
    if text.endswith("."):
        text = text[:-1].strip()
    return text


def normalize_facility_name(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text == "":
        return None
    text = " ".join(text.split())
    text = re.sub(r"\s*-\s*", "-", text)
    return text.upper()


def normalize_template_text(value):
    if value is None or pd.isna(value):
        return ""
    return " ".join(str(value).strip().lower().split())


def get_template_rule(column_name, template_description_row):
    name_norm = normalize_template_text(column_name)
    desc_norm = normalize_template_text(template_description_row.get(column_name))

    if name_norm == "brak" or desc_norm == "brak":
        return "literal_brak"
    if name_norm == "puste" or desc_norm == "puste":
        return "literal_puste"
    if name_norm == "" and desc_norm == "":
        return "empty"
    return "map"


def sort_text(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip().upper()


def sort_number(value):
    num = pd.to_numeric(value, errors="coerce")
    if pd.isna(num):
        return float("inf")
    return float(num)


def sort_facility(value):
    text = sort_text(value)
    match = re.match(r"^([A-Z]+)-(\d+)$", text)
    if match:
        return (match.group(1), int(match.group(2)))
    return (text, float("inf"))
