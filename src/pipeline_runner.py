from src.loader import load_order_cennik_placowki, load_template
from src.product_matching import build_cennik_index, build_order_maps, build_records_with_product_match
from src.facility_matching import prepare_facility_indexes, apply_facility_matching
from src.transformer import build_template_mapping, build_final_records
from src.exporter import sort_final_records, export_to_excel


def run_pipeline(
    excel_file_path,
    cennik_file_path,
    placowki_file_path,
    template_file_path,
    output_dir,
    test_data_utworzenia,
    log_callback=None,
):
    def log(message):
        if log_callback:
            log_callback(message)

    manual_product_overrides = {
        "P0806": "P0115",
        "4474": "175230",
        "120289": "100889",
    }

    manual_facility_overrides = {
        "C-18": "POL_WROC_56",
        "C-19": "POL_WROC_63",
    }

    log("Wczytywanie plików...")
    loaded = load_order_cennik_placowki(excel_file_path, cennik_file_path, placowki_file_path)
    df = loaded["df"]
    cennik_df = loaded["cennik_df"]
    placowki_df = loaded["placowki_df"]

    template_loaded = load_template(template_file_path)
    template_first_sheet_name = template_loaded["template_first_sheet_name"]
    template_columns = template_loaded["template_columns"]
    template_description_row = template_loaded["template_description_row"]

    log("Dopasowanie produktów...")
    cennik_by_code, manual_product_overrides_normalized = build_cennik_index(cennik_df, manual_product_overrides)
    osoba_rejon_by_column, placowka_by_column = build_order_maps(df)
    records = build_records_with_product_match(
        df,
        osoba_rejon_by_column,
        placowka_by_column,
        cennik_by_code,
        manual_product_overrides_normalized,
    )

    log("Dopasowanie placówek...")
    single_placowka_to_data, normalized_facility_index, facility_by_kod = prepare_facility_indexes(placowki_df)
    records = apply_facility_matching(
        records,
        single_placowka_to_data,
        normalized_facility_index,
        facility_by_kod,
        manual_facility_overrides,
    )

    log("Budowa rekordów finalnych...")
    mapped_template_columns = build_template_mapping(template_columns, template_description_row)
    final_records = build_final_records(records, template_columns, mapped_template_columns, test_data_utworzenia)
    final_records = sort_final_records(final_records)

    log("Eksport do Excela...")
    export_result = export_to_excel(
        template_file_path,
        template_first_sheet_name,
        template_columns,
        final_records,
        records,
        output_dir=output_dir,
    )

    return {
        "records_count": export_result["records_count"],
        "records_without_price": export_result["records_without_price"],
        "records_without_facility": export_result["records_without_facility"],
        "output_file_path": export_result["output_file_path"],
    }
