import json
from openpyxl.workbook import workbook
from openpyxl.worksheet import worksheet
import rich
import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import Font, Alignment
from typing import List, Dict
import sys


def get_active_worksheet(wb: Workbook) -> Worksheet or None:
    return wb.worksheets[0]


def get_cell(col: int, row: int) -> str:
    return f'{get_column_letter(col)}{row}'


def write_data(worksheet: Worksheet, data: Dict):
    for i, (header, data) in enumerate(family.items(), start=1):
        col = i * 2 - 1 if i > 1 else 1
        col = col if header != 'Риски' else col - 1
        
        header_cell = worksheet.cell(column=col, row=1)
        header_cell.value = header
        header_cell.alignment = Alignment(horizontal='center')
        header_cell.font = Font(bold=True)

        if header not in ['Рекомендации', 'Риски']:
            worksheet.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col + 1)

        if type(data) == dict:
            for row, (key, val) in enumerate(data.items(), start=1):
                worksheet[get_cell(col=col, row=row + 1)] = key
                cell = worksheet.cell(column=col + 1, row=row + 1)
                cell.value = val
                cell.alignment = Alignment(horizontal='right')
        else:
            for row, el in enumerate(data, start=1):
                if type(el) == dict:
                    worksheet[get_cell(col=col, row=row + 1)] = el['ФИО']
                    worksheet[get_cell(col=col + 1, row=row + 1)] = el['ИИН']
                else:
                    worksheet[get_cell(col=col, row=row + 1)] = el


def get_max_col_width(worksheet: Worksheet) -> List[int]:
    max_col_width_list = []

    max_col, max_row = worksheet.max_column, worksheet.max_row
    for col in worksheet.iter_cols(min_col=1, max_col=max_col, min_row=1, max_row=max_row, values_only=True):
        max_col_width = 0
        for row_value in col:
            if not row_value:
                continue
            cell_width = len(str(row_value))
            if cell_width > max_col_width:
                max_col_width = cell_width
        max_col_width_list.append(max_col_width)

    return max_col_width_list


def auto_width(worksheet: Worksheet, padding: int = 5):
    max_col_width_list = get_max_col_width(worksheet=worksheet)

    for i, width in enumerate(max_col_width_list, start=1):
        worksheet.column_dimensions[get_column_letter(i)].width = width + padding


if __name__ == '__main__':
    with open('excel/family.json', 'r', encoding='utf-8') as f:
        family = json.load(f)['data']

    family = {
            'Члены семьи': family['Члены семьи'],
            'Общие сведения': family['Общие сведения'],
            'Доход за квартал': family['Доход за квартал'],
            'Активы семьи': family['Активы семьи'],
            'Социальные статусы (кол-во человек)': family['Социальные статусы (кол-во человек)'],
            'Рекомендации': family['Рекомендации'],
            'Риски': family['Риски'],
            }

    workbook = Workbook()
    worksheet = get_active_worksheet(wb=workbook)

    write_data(worksheet=worksheet, data=family)
    auto_width(worksheet=worksheet)

    workbook.save('excel/test.xlsx')


