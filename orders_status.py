import sqlite3

# Подключаемся к базе данных (создаем, если нет)
conn = sqlite3.connect('db_campaigns.sqlite')
cursor = conn.cursor()

# Создаем таблицу CampaignResults, если не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS CampaignResults (
    campaign_id INTEGER PRIMARY KEY,
    clicks INTEGER,
    conversions INTEGER,
    budget REAL,
    ROI REAL,
    success_level TEXT
)
''')

# Вставляем примеры данных (удобно для демонстрации)
cursor.executemany('''
INSERT INTO CampaignResults (campaign_id, clicks, conversions, budget)
VALUES (?, ?, ?, ?)
''', [
    (1, 1000, 150, 100),
    (2, 500, 30, 50),
    (3, 2000, 100, 250),
    (4, 1200, 80, 60)
])

conn.commit()

# Функция для расчета ROI
def calculate_roi(conversions, budget):
    if budget == 0:
        return 0
    return (conversions * 100) / budget

# Функция для определения уровня успеха
def determine_success_level(roi):
    if roi > 120:
        return "Успех"
    elif 80 <= roi <= 120:
        return "Средне"
    else:
        return "Провал"

# Получаем все кампании
cursor.execute("SELECT campaign_id, conversions, budget FROM CampaignResults")
campaigns = cursor.fetchall()

# Обновляем ROI и success_level для каждой кампании
for campaign in campaigns:
    campaign_id, conversions, budget = campaign
    roi = calculate_roi(conversions, budget)
    success_level = determine_success_level(roi)
    cursor.execute('''
    UPDATE CampaignResults
    SET ROI = ?, success_level = ?
    WHERE campaign_id = ?
    ''', (roi, success_level, campaign_id))

conn.commit()

# Вывод результатов
cursor.execute("SELECT campaign_id, ROI, success_level FROM CampaignResults")
results = cursor.fetchall()

print("campaign_id | ROI    | success_level")
print("------------------------------------")
for row in results:
    print(f"{row[0]:11} | {row[1]:6.2f} | {row[2]}")

conn.close()
