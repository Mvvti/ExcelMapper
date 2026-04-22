import json
import os
import traceback
from datetime import datetime

import webview

from src.pipeline_runner import run_pipeline as _run_pipeline
from src.loader import load_order_cennik_placowki, load_template
from src.product_matching import build_cennik_index, build_order_maps, build_records_with_product_match
from src.facility_matching import prepare_facility_indexes, apply_facility_matching
from src.transformer import build_template_mapping, build_final_records
from src.exporter import sort_final_records


class API:
    def get_defaults(self):
        base = os.path.dirname(os.path.abspath(__file__))
        return {
            "cennik": os.path.join(base, "CENNIK POLITECHNIKA WROCŁAWSKA.xls"),
            "placowki": os.path.join(base, "POL_WROC PLACÓWKI W NASZYM SYSTEMIE.xls"),
            "template": os.path.join(base, "Template.xlsx"),
        }

    def pick_file(self, *args, **kwargs):
        try:
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=("Excel Files (*.xlsx;*.xls)",),
            )
            return result[0] if result else None
        except Exception:
            return None

    def pick_folder(self, *args, **kwargs):
        try:
            result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
            return result[0] if result else None
        except Exception:
            return None

    def validate_inputs(self, order, cennik, placowki, template, output, date):
        errors = []

        excel_fields = [
            ("order", order, "Plik zamówienia"),
            ("cennik", cennik, "Plik cennika"),
            ("placowki", placowki, "Plik placówek"),
            ("template", template, "Plik template"),
        ]

        for field_name, path, label in excel_fields:
            normalized_path = (path or "").strip()
            lower_path = normalized_path.lower()

            if not normalized_path:
                errors.append({"field": field_name, "message": f"{label}: pole jest wymagane."})
                continue

            if not os.path.exists(normalized_path):
                errors.append({"field": field_name, "message": f"{label}: wskazany plik nie istnieje."})

            if not (lower_path.endswith(".xlsx") or lower_path.endswith(".xls")):
                errors.append(
                    {"field": field_name, "message": f"{label}: dozwolone są tylko pliki .xlsx lub .xls."}
                )

        output_path = (output or "").strip()
        if not output_path:
            errors.append({"field": "output", "message": "Folder output: pole jest wymagane."})
        elif not os.path.exists(output_path):
            errors.append({"field": "output", "message": "Folder output: wskazany folder nie istnieje."})
        elif not os.path.isdir(output_path):
            errors.append({"field": "output", "message": "Folder output: podana ścieżka nie jest folderem."})

        date_value = (date or "").strip()
        if not date_value:
            errors.append({"field": "date", "message": "Data: pole jest wymagane (format YYYY-MM-DD)."})
        else:
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                errors.append({"field": "date", "message": "Data: nieprawidłowy format, użyj YYYY-MM-DD."})

        return errors

    def get_preview(self, order, cennik, placowki, template, date):
        try:
            manual_product_overrides = {
                "P0806": "P0115",
                "4474": "175230",
                "120289": "100889",
            }

            manual_facility_overrides = {
                "C-18": "POL_WROC_56",
                "C-19": "POL_WROC_63",
            }

            loaded = load_order_cennik_placowki(order, cennik, placowki)
            df = loaded["df"]
            cennik_df = loaded["cennik_df"]
            placowki_df = loaded["placowki_df"]

            template_loaded = load_template(template)
            template_columns = template_loaded["template_columns"]
            template_description_row = template_loaded["template_description_row"]

            cennik_by_code, manual_product_overrides_normalized = build_cennik_index(cennik_df, manual_product_overrides)
            osoba_rejon_by_column, placowka_by_column = build_order_maps(df)
            records = build_records_with_product_match(
                df,
                osoba_rejon_by_column,
                placowka_by_column,
                cennik_by_code,
                manual_product_overrides_normalized,
            )

            single_placowka_to_data, normalized_facility_index, facility_by_kod = prepare_facility_indexes(placowki_df)
            records = apply_facility_matching(
                records,
                single_placowka_to_data,
                normalized_facility_index,
                facility_by_kod,
                manual_facility_overrides,
            )

            mapped_template_columns = build_template_mapping(template_columns, template_description_row)
            final_records = build_final_records(records, template_columns, mapped_template_columns, date)
            final_records = sort_final_records(final_records)

            def to_preview_value(value):
                if value is None:
                    return ""
                try:
                    if value != value:
                        return ""
                except Exception:
                    pass
                return value

            rows = []
            for final_record in final_records[:20]:
                row = [to_preview_value(final_record.get(col)) for col in template_columns]
                rows.append(row)

            without_price = sum(1 for r in records if not r.get("match_found"))
            without_facility = sum(1 for r in records if not r.get("facility_match_found"))

            return {
                "columns": template_columns,
                "rows": rows,
                "total": len(final_records),
                "without_price": without_price,
                "without_facility": without_facility,
            }
        except Exception as e:
            return {"error": str(e)}

    def run_pipeline(self, order, cennik, placowki, template, output_dir, date):
        def log(msg):
            webview.windows[0].evaluate_js(f"appendLog({json.dumps(msg)})")

        try:
            result = _run_pipeline(
                excel_file_path=order,
                cennik_file_path=cennik,
                placowki_file_path=placowki,
                template_file_path=template,
                output_dir=output_dir,
                test_data_utworzenia=date,
                log_callback=log,
            )
            webview.windows[0].evaluate_js(f"onPipelineDone({json.dumps(result)})")
        except Exception:
            err = traceback.format_exc()
            webview.windows[0].evaluate_js(f"onPipelineError({json.dumps(err)})")


if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "index.html")
    html_url = f"file:///{html_path.replace(chr(92), '/')}"

    api = API()
    webview.create_window(
        title="ExcelMapper",
        url=html_url,
        width=980,
        height=760,
        resizable=True,
        js_api=api,
    )
    webview.start()
