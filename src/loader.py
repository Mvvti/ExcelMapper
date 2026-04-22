import pandas as pd


def load_order_cennik_placowki(excel_file_path, cennik_file_path, placowki_file_path):
    xls = pd.ExcelFile(excel_file_path)
    first_sheet_name = xls.sheet_names[0]
    df = pd.read_excel(excel_file_path, sheet_name=first_sheet_name)

    cennik_xls = pd.ExcelFile(cennik_file_path)
    cennik_first_sheet_name = cennik_xls.sheet_names[0]
    cennik_df = pd.read_excel(cennik_file_path, sheet_name=cennik_first_sheet_name)

    placowki_xls = pd.ExcelFile(placowki_file_path)
    placowki_first_sheet_name = placowki_xls.sheet_names[0]
    placowki_df = pd.read_excel(placowki_file_path, sheet_name=placowki_first_sheet_name)

    return {
        "first_sheet_name": first_sheet_name,
        "df": df,
        "cennik_first_sheet_name": cennik_first_sheet_name,
        "cennik_df": cennik_df,
        "placowki_first_sheet_name": placowki_first_sheet_name,
        "placowki_df": placowki_df,
    }


def load_template(template_file_path):
    template_xls = pd.ExcelFile(template_file_path)
    template_first_sheet_name = template_xls.sheet_names[0]
    template_df = pd.read_excel(template_file_path, sheet_name=template_first_sheet_name)
    template_columns = list(template_df.columns)

    template_description_row = {}
    if len(template_df) > 1:
        for col in template_columns:
            template_description_row[col] = template_df.iloc[1][col]
    else:
        for col in template_columns:
            template_description_row[col] = None

    return {
        "template_first_sheet_name": template_first_sheet_name,
        "template_df": template_df,
        "template_columns": template_columns,
        "template_description_row": template_description_row,
    }
