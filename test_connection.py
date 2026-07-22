import gspread

SPREADSHEET_ID = "1Edb7JJ6Iu-k7zwRhlAeXJ900wVbo-KgOj4LsqVtuO1A"

gc = gspread.service_account(filename="service_account.json")
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.sheet1

test_row = ["test-id-001", "接続テスト", "疎通確認用のダミーデータ", "2026-07-22", "未完了", "2026-07-22 17:00:00"]
worksheet.append_row(test_row)
print("書き込み成功")

all_values = worksheet.get_all_values()
print("現在のシートの中身:")
for row in all_values:
    print(row)
