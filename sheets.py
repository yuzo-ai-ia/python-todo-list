import uuid
from datetime import datetime

import gspread
import streamlit as st

SPREADSHEET_ID = "1Edb7JJ6Iu-k7zwRhlAeXJ900wVbo-KgOj4LsqVtuO1A"


@st.cache_resource
def _get_worksheet():
    gc = gspread.service_account(filename="service_account.json")
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.sheet1


def add_task(title: str, content: str, due_date: str) -> None:
    worksheet = _get_worksheet()
    task_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([task_id, title, content, due_date, "未完了", created_at])


def get_all_tasks() -> list[dict]:
    worksheet = _get_worksheet()
    return worksheet.get_all_records()


def update_task(task_id: str, title: str, content: str, due_date: str, status: str) -> None:
    worksheet = _get_worksheet()
    cell = worksheet.find(task_id, in_column=1)
    worksheet.update(f"B{cell.row}:E{cell.row}", [[title, content, due_date, status]])


def delete_task(task_id: str) -> None:
    worksheet = _get_worksheet()
    cell = worksheet.find(task_id, in_column=1)
    worksheet.delete_rows(cell.row)
