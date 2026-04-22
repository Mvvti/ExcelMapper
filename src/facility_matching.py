import pandas as pd
import re

from src.utils import normalize_facility_name


range_pattern = re.compile(r"^\s*([A-Za-z]+)\s*-\s*(\d+)\s*-\s*([A-Za-z]+)\s*-\s*(\d+)\s*$")
single_pattern = re.compile(r"^\s*([A-Za-z]+)\s*-\s*(\d+)\s*$")


def _expand_facility_value(raw_value):
    if pd.isna(raw_value):
        return []

    text = " ".join(str(raw_value).split())
    if text == "":
        return []

    expanded = []
    segments = re.split(r"[,;/]", text)

    for segment in segments:
        segment = " ".join(segment.split())
        if segment == "":
            continue

        range_match = range_pattern.match(segment)
        if range_match:
            prefix_start = range_match.group(1).upper()
            number_start = int(range_match.group(2))
            prefix_end = range_match.group(3).upper()
            number_end = int(range_match.group(4))

            if prefix_start == prefix_end:
                step = 1 if number_end >= number_start else -1
                for num in range(number_start, number_end + step, step):
                    expanded.append(f"{prefix_start}-{num}")
            continue

        single_match = single_pattern.match(segment)
        if single_match:
            prefix = single_match.group(1).upper()
            number = int(single_match.group(2))
            expanded.append(f"{prefix}-{number}")

    return expanded


def prepare_facility_indexes(placowki_df):
    placowka_code_column = None
    best_score = -1

    for col_name in placowki_df.columns:
        score = 0
        col_name_lower = str(col_name).lower()

        if "nazwa" in col_name_lower:
            score += 6
        if "plac" in col_name_lower or "obiekt" in col_name_lower or "zakres" in col_name_lower:
            score += 5
        if "kod" in col_name_lower or "symbol" in col_name_lower:
            score += 1

        sample_values = placowki_df[col_name].dropna().astype(str).head(200)
        for value in sample_values:
            value_clean = " ".join(value.split())
            if range_pattern.match(value_clean):
                score += 3
            elif single_pattern.match(value_clean):
                score += 1

        if score > best_score:
            best_score = score
            placowka_code_column = col_name

    single_placowka_to_data = {}
    if placowka_code_column is not None:
        for _, placowka_row in placowki_df.iterrows():
            expanded_values = _expand_facility_value(placowka_row[placowka_code_column])
            for single_placowka in expanded_values:
                if single_placowka not in single_placowka_to_data:
                    single_placowka_to_data[single_placowka] = []
                single_placowka_to_data[single_placowka].append(placowka_row.to_dict())

    normalized_facility_index = {}
    for single_placowka, placowka_data_list in single_placowka_to_data.items():
        if not placowka_data_list:
            continue

        base_norm = normalize_facility_name(single_placowka)
        if base_norm is None:
            continue

        variants = {base_norm}
        if base_norm.startswith("BUDYNEK "):
            variants.add(base_norm.replace("BUDYNEK ", "", 1).strip())
        else:
            variants.add(f"BUDYNEK {base_norm}")

        for variant in variants:
            if variant not in normalized_facility_index:
                normalized_facility_index[variant] = placowka_data_list[0]

    facility_by_kod = {}
    for _, placowka_row in placowki_df.iterrows():
        facility_kod = placowka_row.get("Kod")
        if pd.isna(facility_kod):
            continue
        facility_kod = str(facility_kod).strip()
        if facility_kod != "" and facility_kod not in facility_by_kod:
            facility_by_kod[facility_kod] = placowka_row.to_dict()

    return single_placowka_to_data, normalized_facility_index, facility_by_kod


def apply_facility_matching(records, single_placowka_to_data, normalized_facility_index, facility_by_kod, manual_facility_overrides):
    for record in records:
        raw_placowka = record.get("placowka")
        matched_facility_data = None

        if raw_placowka in single_placowka_to_data and single_placowka_to_data[raw_placowka]:
            matched_facility_data = single_placowka_to_data[raw_placowka][0]
            record["facility_match_found"] = True
            record["facility_match_source"] = "exact_match"
        else:
            normalized_placowka = normalize_facility_name(raw_placowka)
            normalized_matched = normalized_facility_index.get(normalized_placowka)

            if normalized_matched is not None:
                matched_facility_data = normalized_matched
                record["facility_match_found"] = True
                record["facility_match_source"] = "normalized_match"
            else:
                override_code = manual_facility_overrides.get(normalized_placowka)
                override_data = facility_by_kod.get(override_code)

                if override_data is not None:
                    matched_facility_data = override_data
                    record["facility_match_found"] = True
                    record["facility_match_source"] = "manual_override"
                else:
                    record["facility_match_found"] = False
                    record["facility_match_source"] = "unmatched"

        if matched_facility_data is not None:
            record["facility_kod"] = matched_facility_data.get("Kod")
            record["facility_nazwa"] = matched_facility_data.get("Nazwa")
            record["facility_kod_pocztowy"] = matched_facility_data.get("Kod pocztowy")
            record["facility_miasto"] = matched_facility_data.get("Miasto")
            record["facility_ulica"] = matched_facility_data.get("Ulica")
        else:
            record["facility_kod"] = None
            record["facility_nazwa"] = None
            record["facility_kod_pocztowy"] = None
            record["facility_miasto"] = None
            record["facility_ulica"] = None

    return records


def print_facility_summary(records):
    facility_exact_count = sum(1 for r in records if r["facility_match_source"] == "exact_match")
    facility_normalized_count = sum(1 for r in records if r["facility_match_source"] == "normalized_match")
    facility_manual_count = sum(1 for r in records if r["facility_match_source"] == "manual_override")
    facility_unmatched_count = sum(1 for r in records if r["facility_match_source"] == "unmatched")

    facility_unmatched_placowki = sorted(
        {
            r["placowka"]
            for r in records
            if r["facility_match_source"] == "unmatched" and r["placowka"] is not None
        }
    )

    print("=== PODSUMOWANIE DOPASOWANIA PLACÓWEK ===")
    print(f"Liczba rekordów dopasowanych przez exact_match: {facility_exact_count}")
    print(f"Liczba rekordów dopasowanych przez normalized_match: {facility_normalized_count}")
    print(f"Liczba rekordów dopasowanych przez manual_override: {facility_manual_count}")
    print(f"Liczba rekordów nadal niedopasowanych: {facility_unmatched_count}")

    print("\n=== UNIKALNE NADAL NIEDOPASOWANE placowka ===")
    print(facility_unmatched_placowki)

    print("\n=== PIERWSZE 50 REKORDÓW Z DOPASOWANIEM PLACÓWEK ===")
    if records:
        facility_preview_columns = [
            "placowka",
            "facility_match_found",
            "facility_match_source",
            "facility_kod",
            "facility_nazwa",
            "facility_kod_pocztowy",
            "facility_miasto",
            "facility_ulica",
        ]
        print(pd.DataFrame(records[:50])[facility_preview_columns].to_string(index=False))
    else:
        print("Brak rekordów.")
