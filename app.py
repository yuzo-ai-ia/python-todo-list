import datetime as dt

import pandas as pd
import streamlit as st

from sheets import add_task, delete_task, get_all_tasks, update_task

STATUS_STYLE = {
    "gray": {"mark": "⚪", "bg": "#e0e0e0"},
    "red": {"mark": "🔴", "bg": "#ffcdd2"},
    "orange": {"mark": "🟠", "bg": "#ffe0b2"},
    "green": {"mark": "🟢", "bg": "#c8e6c9"},
}


def _status_key(task: dict, today: dt.date) -> str:
    try:
        due = dt.date.fromisoformat(task["due_date"])
    except ValueError:
        due = None

    if task["status"] == "完了":
        return "gray"
    if due is not None and due < today:
        return "red"
    if due is not None and due <= today + dt.timedelta(days=3):
        return "orange"
    return "green"

st.set_page_config(page_title="TODOリスト", page_icon="✅")
st.title("TODOリスト")

st.header("タスクを登録する")
with st.form("add_task_form", clear_on_submit=True):
    title = st.text_input("タイトル（必須）")
    content = st.text_area("内容", height=100)
    due_date = st.date_input("期日")
    submitted = st.form_submit_button("登録する")

    if submitted:
        if not title:
            st.error("タイトルは必須です")
        else:
            add_task(title, content, due_date.strftime("%Y-%m-%d"))
            st.success("登録しました！")

st.header("タスク一覧")

sort_option = st.selectbox("並び替え", ["期日が近い順", "登録が新しい順"])

tasks = get_all_tasks()

if sort_option == "期日が近い順":
    tasks.sort(key=lambda t: t["due_date"])
else:
    tasks.sort(key=lambda t: t["created_at"], reverse=True)

if not tasks:
    st.info("タスクはまだ登録されていません")
else:
    today = dt.date.today()

    rows = []
    status_keys = []
    for task in tasks:
        status_key = _status_key(task, today)
        status_keys.append(status_key)
        rows.append(
            {
                "印": STATUS_STYLE[status_key]["mark"],
                "タイトル": task["title"],
                "内容": task["content"],
                "期日": task["due_date"],
                "ステータス": task["status"],
            }
        )

    df = pd.DataFrame(rows)

    def _highlight_row(row: pd.Series) -> list[str]:
        bg = STATUS_STYLE[status_keys[row.name]]["bg"]
        return [f"background-color: {bg}"] * len(row)

    st.dataframe(
        df.style.apply(_highlight_row, axis=1),
        hide_index=True,
        width="stretch",
    )

    st.header("完了チェック")

    for task in tasks:
        checked = st.checkbox(
            task["title"],
            value=(task["status"] == "完了"),
            key=f"complete_{task['id']}",
        )
        if checked != (task["status"] == "完了"):
            update_task(
                task["id"],
                task["title"],
                task["content"],
                task["due_date"],
                "完了" if checked else "未完了",
            )
            st.rerun()

    st.header("タスクを編集する")

    task_options = {f"{t['title']}（{t['due_date']}）": t for t in tasks}
    selected_label = st.selectbox("編集するタスク", list(task_options.keys()))
    selected_task = task_options[selected_label]

    with st.form("edit_task_form"):
        edit_title = st.text_input("タイトル（必須）", value=selected_task["title"])
        edit_content = st.text_area("内容", value=selected_task["content"], height=100)
        edit_due_date = st.date_input(
            "期日", value=dt.date.fromisoformat(selected_task["due_date"])
        )
        edit_status = st.selectbox(
            "ステータス",
            ["未完了", "完了"],
            index=["未完了", "完了"].index(selected_task["status"]),
        )
        edit_submitted = st.form_submit_button("更新する")

        if edit_submitted:
            if not edit_title:
                st.error("タイトルは必須です")
            else:
                update_task(
                    selected_task["id"],
                    edit_title,
                    edit_content,
                    edit_due_date.strftime("%Y-%m-%d"),
                    edit_status,
                )
                st.success("更新しました！")
                st.rerun()

    st.header("タスクを削除する")

    delete_label = st.selectbox(
        "削除するタスク", list(task_options.keys()), key="delete_select"
    )
    delete_task_target = task_options[delete_label]
    confirm_delete = st.checkbox("本当に削除しますか？")

    if st.button("削除する", disabled=not confirm_delete):
        delete_task(delete_task_target["id"])
        st.success("削除しました！")
        st.rerun()
