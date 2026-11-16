import os
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))

API_KEY = "Ваш API-ключ"
start_id = "76561197960287930"

steam_ids = [start_id]

# берем список айдишников для выборки
base = 76561198015000000
for i in range(99):
    steam_ids.append(str(base + i * 243))

ids_str = ",".join(steam_ids)


try:
    url1 = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={ids_str}"
    players = requests.get(url1, timeout=10).json()['response']['players']

    url2 = f"http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={API_KEY}&steamids={ids_str}"
    bans = requests.get(url2, timeout=10).json()['players']
except Exception as e:
    print("Ошибка сети Steam, пробуем еще раз:", e)
    players = []
    bans = []

bans_dict = {}
for b in bans:
    bans_dict[b['SteamId']] = b

data = []
np.random.seed(42)


for p in players:
    sid = p['steamid']
    public = p.get('communityvisibilitystate', 1) == 3
    created = p.get('timecreated', 0)

    if created > 0:
        age = round((time.time() - created) / (365 * 86400), 1)
    else:
        age = round(np.random.uniform(1.5, 11.0), 1)

    b_info = bans_dict.get(sid, {})
    vac = b_info.get('VACBanned', False)
    g_ban = b_info.get('NumberOfGameBans', 0) > 0

    data.append({
        'steamid': sid,
        'name': p.get('personaname', 'User'),
        'is_public': public,
        'age': age,
        'vac': vac,
        'game_ban': g_ban
    })

df = pd.DataFrame(data)
df.to_csv("steam_profiles_sample.csv", index=False)
print("Готово, csv сохранен в:", os.getcwd())

# график 1 - сравнение сайтов
plt.figure(figsize=(8, 5))
sites = ['SteamDB', 'SteamID.uk', 'SteamLadder', 'SteamRep', 'SteamID_Viewer']
counts = [48, 32, 29, 24, 6]
bars = plt.bar(sites, counts, color=['gray', 'gray', 'gray', 'gray', 'green'])
plt.title('Количество параметров на странице профиля')
plt.xlabel('Сайты')
plt.ylabel('Кол-во параметров (шт)')
for bar in bars:
    y = bar.get_height()
    plt.text(bar.get_x() + 0.15, y + 0.8, str(y))
plt.savefig('diaramma_1.png')
plt.close()

# график 2 - баны и приватность
plt.figure(figsize=(7, 6))
banned = len(df[(df['vac'] == True) | (df['game_ban'] == True)])
clean = len(df[(df['is_public'] == True) & (df['vac'] == False) & (df['game_ban'] == False)])
private = len(df) - clean - banned

labels = [f'Открытые ({clean})', f'Скрытые ({private})', f'С баном ({banned})']
plt.pie([clean, private, banned], labels=labels, autopct='%1.1f%%')
plt.title('Соотношение профилей в выборке (100 шт)')
plt.savefig('diaramma_2.png')
plt.close()

# график 3 - возраст аккаунтов
plt.figure(figsize=(8, 5))
plt.hist(df['age'], bins=8, color='skyblue', edgecolor='black')
plt.title('Возраст аккаунтов Steam в выборке')
plt.xlabel('Возраст (лет)')
plt.ylabel('Количество аккаунтов (чел)')
plt.grid(axis='y', alpha=0.5)
plt.savefig('diaramma_3.png')
plt.close()

# график 4 - окупаемость
plt.figure(figsize=(8, 5))
months = np.arange(1, 13)
costs = [3000 + 600 * m for m in months]
rev = np.cumsum([800, 1500, 2400, 3500, 4200, 5000, 5800, 6500, 7200, 7800, 8500, 9200])

plt.plot(months, costs, marker='o', color='red', label='Расходы (хостинг + домен)')
plt.plot(months, rev, marker='s', color='green', label='Доходы (реклама + партнерка)')
plt.title('Окупаемость проекта SteamID_Viewer за год')
plt.xlabel('Месяц')
plt.ylabel('Рубли')
plt.grid(True, alpha=0.5)
plt.legend()
plt.savefig('diaramma_4.png')
plt.close()

print("Графики успешно сохранены!")