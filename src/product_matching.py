import pandas as pd
import re

from src.utils import normalize_code


def build_cennik_index(cennik_df, manual_product_overrides):
    cennik_code_column = None
    for col_name in cennik_df.columns:
        col_name_lower = str(col_name).lower()
        if "kod" in col_name_lower or "id" in col_name_lower:
            cennik_code_column = col_name
            break

    cennik_price_column = "Cena" if "Cena" in cennik_df.columns else None
    cennik_by_code = {}

    if cennik_code_column is not None and cennik_price_column is not None:
        for _, cennik_row in cennik_df.iterrows():
            normalized_code = normalize_code(cennik_row[cennik_code_column])
            if normalized_code is None:
                continue

            if normalized_code not in cennik_by_code:
                cennik_by_code[normalized_code] = {
                    "matched_cennik_code": normalized_code,
                    "matched_price_from_cennik": cennik_row[cennik_price_column],
                }

    manual_product_overrides_normalized = {}
    for source_code, target_code in manual_product_overrides.items():
        source_norm = normalize_code(source_code)
        target_norm = normalize_code(target_code)
        if source_norm is not None and target_norm is not None:
            manual_product_overrides_normalized[source_norm] = target_norm

    return cennik_by_code, manual_product_overrides_normalized


def build_order_maps(df):
    osoba_rejon_by_column = {}
    placowka_by_column = {}
    last_osoba_rejon = None

    for col_index in range(6, df.shape[1]):
        osoba_value = df.iat[0, col_index]
        placowka_value = df.iat[1, col_index]

        if pd.notna(osoba_value) and str(osoba_value).strip() != "":
            last_osoba_rejon = str(osoba_value).strip()

        osoba_rejon_by_column[col_index] = last_osoba_rejon
        placowka_by_column[col_index] = None if pd.isna(placowka_value) else str(placowka_value).strip()

    return osoba_rejon_by_column, placowka_by_column


def build_records_with_product_match(df, osoba_rejon_by_column, placowka_by_column, cennik_by_code, manual_product_overrides_normalized):
    records = []

    for row_index in range(6, df.shape[0]):
        lp = None if pd.isna(df.iat[row_index, 0]) else df.iat[row_index, 0]
        nazwa_produktu = None if pd.isna(df.iat[row_index, 1]) else df.iat[row_index, 1]
        producent_kod = None if pd.isna(df.iat[row_index, 2]) else df.iat[row_index, 2]
        cena_zamowienia = None if pd.isna(df.iat[row_index, 3]) else df.iat[row_index, 3]
        ilosc_w_umowie = None if pd.isna(df.iat[row_index, 4]) else df.iat[row_index, 4]
        ilosc_w_zamowieniu = None if pd.isna(df.iat[row_index, 5]) else df.iat[row_index, 5]

        for col_index in range(6, df.shape[1]):
            ilosc_raw = df.iat[row_index, col_index]
            ilosc_num = pd.to_numeric(ilosc_raw, errors="coerce")

            if pd.notna(ilosc_num) and ilosc_num > 0:
                parsed_product_code = None
                producent_kod_text = "" if producent_kod is None else str(producent_kod)
                tokens = re.findall(r"[A-Za-z0-9]+", producent_kod_text)

                for token in reversed(tokens):
                    if any(ch.isdigit() for ch in token) and len(token) >= 3:
                        parsed_product_code = token
                        break

                record = {
                    "row_index": row_index,
                    "lp": lp,
                    "nazwa_produktu": nazwa_produktu,
                    "producent_kod": producent_kod,
                    "cena_zamowienia": cena_zamowienia,
                    "ilosc_w_umowie": ilosc_w_umowie,
                    "ilosc_w_zamowieniu": ilosc_w_zamowieniu,
                    "osoba_rejon": osoba_rejon_by_column[col_index],
                    "placowka": placowka_by_column[col_index],
                    "ilosc_dla_placowki": ilosc_num,
                    "parsed_product_code": parsed_product_code,
                }

                parsed_norm = normalize_code(parsed_product_code)
                matched_data = cennik_by_code.get(parsed_norm)

                if matched_data is not None:
                    record["matched_price_from_cennik"] = matched_data["matched_price_from_cennik"]
                    record["matched_cennik_code"] = matched_data["matched_cennik_code"]
                    record["match_found"] = True
                    record["match_source"] = "code_match"
                else:
                    override_target = manual_product_overrides_normalized.get(parsed_norm)
                    override_matched = cennik_by_code.get(override_target)

                    if override_matched is not None:
                        record["matched_price_from_cennik"] = override_matched["matched_price_from_cennik"]
                        record["matched_cennik_code"] = override_matched["matched_cennik_code"]
                        record["match_found"] = True
                        record["match_source"] = "manual_override"
                    else:
                        record["matched_price_from_cennik"] = None
                        record["matched_cennik_code"] = None
                        record["match_found"] = False
                        record["match_source"] = "unmatched"

                records.append(record)

    return records
