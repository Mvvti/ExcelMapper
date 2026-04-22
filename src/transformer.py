import pandas as pd

from src.utils import normalize_template_text, get_template_rule


def build_template_mapping(template_columns, template_description_row):
    mapped_template_columns = {}

    for col in template_columns:
        rule = get_template_rule(col, template_description_row)
        col_norm = normalize_template_text(col)

        if rule == "literal_brak":
            mapped_template_columns[col] = "literal_brak"
            continue
        if rule == "literal_puste":
            mapped_template_columns[col] = "literal_puste"
            continue
        if rule == "empty":
            mapped_template_columns[col] = "empty"
            continue

        explicit_map = {
            "zamowienie_nr": "osoba_rejon",
            "odbierajacy_towar": "osoba_rejon",
            "data_utworzenia": "test_data_utworzenia",
            "termin_dostawy": "test_data_utworzenia",
            "zamawiajacy_imie_nazwisko": "osoba_rejon",
            "oddzial_id": "const_oddzial_id",
            "oddzial_nazwa": "const_oddzial_nazwa",
            "obiekt_id": "facility_kod",
            "obiekt_adres_ulica": "facility_ulica",
            "obiekt_adres_miasto": "facility_miasto",
            "obiekt_adres_kod_pocztowy": "facility_kod_pocztowy",
            "obiekt_id_dostawcy": "facility_kod",
            "nazwa_miejsca_dostaw.": "placowka",
            "artykul_pozycja_na_zamowieniu": "lp",
            "artykul_kod": "matched_cennik_code",
            "artykul_nazwa": "nazwa_produktu",
            "artykul_ilosc": "ilosc_dla_placowki",
            "artykul_jednostka": "const_artykul_jednostka",
            "artykul_cena_netto": "matched_price_from_cennik",
            "art.wartosc_netto": "calc_art_wartosc_netto",
            "artykul_waluta": "const_artykul_waluta",
        }

        mapped_template_columns[col] = explicit_map.get(col_norm, "unmapped")

    return mapped_template_columns


def build_final_records(records, template_columns, mapped_template_columns, test_data_utworzenia):
    final_records = []

    for record in records:
        final_record = {}

        for col in template_columns:
            mapping = mapped_template_columns[col]

            if mapping == "literal_brak":
                final_record[col] = None
            elif mapping == "literal_puste":
                final_record[col] = None
            elif mapping == "empty":
                final_record[col] = None
            elif mapping == "test_data_utworzenia":
                final_record[col] = test_data_utworzenia
            elif mapping == "const_oddzial_nazwa":
                final_record[col] = "Politechnika Wrocławska"
            elif mapping == "const_oddzial_id":
                final_record[col] = "8960005851"
            elif mapping == "const_artykul_jednostka":
                final_record[col] = "SZT"
            elif mapping == "const_artykul_waluta":
                final_record[col] = "PLN"
            elif mapping == "calc_art_wartosc_netto":
                if record.get("match_found"):
                    price = record.get("matched_price_from_cennik")
                    qty = record.get("ilosc_dla_placowki")
                    if price is not None and qty is not None:
                        final_record[col] = price * qty
                    else:
                        final_record[col] = None
                else:
                    final_record[col] = None
            elif mapping == "matched_cennik_code":
                final_record[col] = record.get("matched_cennik_code") if record.get("match_found") else None
            elif mapping == "matched_price_from_cennik":
                final_record[col] = record.get("matched_price_from_cennik") if record.get("match_found") else None
            elif mapping.startswith("facility_"):
                final_record[col] = record.get(mapping) if record.get("facility_match_found") else None
            elif mapping == "unmapped":
                final_record[col] = None
            else:
                final_record[col] = record.get(mapping)

        final_records.append(final_record)

    return final_records


def print_template_summary(template_columns, mapped_template_columns, final_records):
    print("\n=== KOLUMNY TEMPLATE ===")
    for col in template_columns:
        print(col)

    print("\n=== ZMAPOWANE KOLUMNY TEMPLATE ===")
    for col in template_columns:
        print(f"{col} -> {mapped_template_columns[col]}")

    print("\n=== PODSUMOWANIE FINALNYCH REKORDÓW ===")
    print(f"Liczba przygotowanych finalnych rekordów: {len(final_records)}")

    print("\n=== PIERWSZE 10 FINALNYCH REKORDÓW (UKŁAD TEMPLATE) ===")
    if final_records:
        print(pd.DataFrame(final_records[:10], columns=template_columns).to_string(index=False))
    else:
        print("Brak finalnych rekordów.")
