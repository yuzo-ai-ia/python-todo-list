import uuid
from datetime import datetime

import gspread
import streamlit as st

SPREADSHEET_ID = "1Edb7JJ6Iu-k7zwRhlAeXJ900wVbo-KgOj4LsqVtuO1A"


class SheetsError(Exception):
    """スプレッドシートとの通信に失敗した場合の例外"""


class TaskNotFoundError(Exception):
    """指定したタスクが見つからなかった場合の例外"""


@st.cache_resource
def _get_worksheet():
    try:
        credentials = dict(st.secrets["gcp_service_account"])
        gc = gspread.service_account_from_dict(credentials)
        sh = gc.open_by_key(SPREADSHEET_ID)
        return sh.sheet1
    except KeyError as e:
        raise SheetsError(
            "認証情報（gcp_service_account）がSecretsに設定されていません。"
        ) from e
    except gspread.exceptions.APIError as e:
        raise SheetsError(
            "Googleスプレッドシートへの接続に失敗しました。しばらくしてから再度お試しください。"
        ) from e


def _find_row(worksheet, task_id: str) -> int:
    cell = worksheet.find(task_id, in_column=1)
    if cell is None:
        raise TaskNotFoundError(
            "対象のタスクが見つかりませんでした。すでに削除されている可能性があります。"
        )
    return cell.row


def add_task(title: str, content: str, due_date: str) -> None:
    worksheet = _get_worksheet()
    task_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        worksheet.append_row([task_id, title, content, due_date, "未完了", created_at])
    except gspread.exceptions.APIError as e:
        raise SheetsError("タスクの登録に失敗しました。しばらくしてから再度お試しください。") from e


def get_all_tasks() -> list[dict]:
    worksheet = _get_worksheet()
    try:
        return worksheet.get_all_records()
    except gspread.exceptions.APIError as e:
        raise SheetsError(
            "タスク一覧の取得に失敗しました。しばらくしてから再度お試しください。"
        ) from e


def update_task(task_id: str, title: str, content: str, due_date: str, status: str) -> None:
    worksheet = _get_worksheet()
    try:
        row = _find_row(worksheet, task_id)
        worksheet.update(f"B{row}:E{row}", [[title, content, due_date, status]])
    except gspread.exceptions.APIError as e:
        raise SheetsError("タスクの更新に失敗しました。しばらくしてから再度お試しください。") from e


def delete_task(task_id: str) -> None:
    worksheet = _get_worksheet()
    try:
        row = _find_row(worksheet, task_id)
        worksheet.delete_rows(row)
    except gspread.exceptions.APIError as e:
        raise SheetsError("タスクの削除に失敗しました。しばらくしてから再度お試しください。") from e
