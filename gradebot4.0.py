from re import S
from reportlab.lib import pagesizes
import telebot
import csv
import matplotlib
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import shutil
from datetime import datetime, timezone
from dotenv import load_dotenv
import pandas as pd
import sqlite3
from telebot import types
from io import BytesIO
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import PIL
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.FileHandler('gradebot.log'),
              logging.StreamHandler()
              ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
districts = {
    "Центральный": {
        'белгород': (50.595414, 36.587277),
        'брянск': (53.243400, 34.363991),
        'воронеж': (51.660781, 39.200296),
        'иваново': (56.999799, 40.973014),
        'калуга': (54.513678, 36.261341),
        'кострома': (57.767918, 40.926894),
        'липецк': (52.608826, 39.599229),
        'красногорск': (55.820369, 37.319484),
        'ярославль': (57.626559, 39.893813),
        'тула': (54.193122, 37.617348),
        'тамбов': (52.721295, 41.452750),
        'тверь': (56.858745, 35.917421),
        'владимир': (56.134710, 40.406599),
        'москва': (55.755508, 37.617187),
        'орел': (52.970756, 36.064358),
        'рязань': (54.629221, 39.737111),
        'смоленск': (54.778263, 32.051054)
    },
    'Северо-Западный': {
        'петрозаводск': (61.785021, 34.346878),
        'сывтывкар': (61.668797, 50.836497),
        'псков': (57.819307, 28.332792),
        'санкт-петербург': (59.938784, 30.314997),
        "медвежьегорск": (62.914998, 34.473101),
        'мурманск': (68.964319, 33.048633),
        'архангельск': (64.539911, 40.515762),
        'вологда': (59.220501, 39.891523),
        'великий новгород': (58.522857, 31.269816),
        'калининград': (54.710162, 20.510137),
        'нарьян-мар': (67.638050, 53.006926)
    },
    'Южный': {
        'астрахань': (46.347614, 48.030178),
        'волгоград': (48.707067, 44.516975),
        'черкесск': (44.228374, 42.048279),
        'ростов-на-дону': (47.222109, 39.718813),
        'краснодар': (45.035470, 38.975313),
        'элиста': (46.307743, 44.269759),
        'ставрополь': (45.043317, 41.969110)
    },
    'Северо-Кавказский':{
        'черкесск': (44.228374, 42.048279),
        'нальчик': (43.485259, 43.607081),
        'махачкала': (42.983100, 47.504745),
        'владикавказ': (43.024616, 44.681771),
        'магас': (43.166787, 44.803574),
        'донецк': (48.015884, 37.802850),
        'симферополь': (44.948237, 34.100327),
        'луганск': (48.573896, 39.307708),
        'майкоп': (44.606683, 40.105852),
        'грозный': (43.318366, 45.692421),
        'севастополь': (44.616020, 33.5244710)
    },
    'Приволжский': {
        'оренбург': (51.768205, 55.097000),
        'пенза': (53.195042, 45.018316),
        'самара': (53.195878, 50.10020),
        'екатеринбург': (56.837435, 60.597636),
        'нижний новгород': (56.326797, 44.006516),
        'казань': (55.796127, 49.106414),
        'пермь': (58.010543, 56.250170),
        'уфа': (54.735152, 55.958736),
        'йошкар-ола': (56.631600, 47.886178),
        'саранск': (54.187433, 45.183938),
        'ижевск': (56.845096, 53.188089),
        'чебоксары':(56.139918, 47.247728),
        'ульяновск': (54.318598, 48.405773),
        'саратов': (51.533338, 46.034176),
        'киров': (58.603595, 49.668023)
    },
    'Уральский': {
        'екатеринбург': (56.837435, 60.597636),
        'ханты-мансийск': (61.003184, 69.018911),
        'новосибирск': (58.522857, 31.269816),
        'омск': (54.989347, 73.368221),
        'салехард': (66.529866, 66.614507),
        'челябинск': (55.159902, 61.402554)


    },
    'Сибирский': {
        'томск': (56.484645, 84.947649),
        'абакан': (53.721152, 91.442396),
        'красноярск': (56.010543, 92.852581),
        'улан-удэ': (51.834809, 107.584547),
        'горно-алтайск': (51.957804, 85.960634),
        'кызыл': (51.719890, 94.437990),
        'барнаул': (53.346785, 83.776856) ,
        'чита': (52.033635, 113.501049),
        'иркутск': (52.289588, 104.280606),
        'кемерово': (55.355198, 86.086847)
    },
    'Дальновосточный': {
        'петропавловск-камчатский': (53.024265, 158.643503),
        'якутск': (62.027221, 129.732178),
        'владивосток': (43.115542, 131.885494),
        'биробиджан': (48.789920, 132.924746),
        'анадырь': (64.735814, 177.518913),
        'благовещенск': (50.249266, 127.553278),
        'хабаровск': (48.480229, 135.071917),
        'южно-сахалинск': (46.957771, 142.729587),
        'магадан': (59.565155, 150.808586)}
    }
load_dotenv()
TOKEN = os.getenv
valid = {'математика', 'русский', 'английский', 'физика', 'химия', 'биология', 'история', 'география', 'информатика', 'литература', 'обж', 'физкультура', 'музыка', 'рисование', 'технология'}
bot = telebot.TeleBot(TOKEN)
DB_PATH = 'grades.db'
weather_cache = {}
CACHE_DURATION = 3600
def init_db():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS grades (
  user_id INTEGER,
  subject TEXT,
  grade INTEGER,
  timestamp TEXT,
  weather TEXT
  )
  ''')
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS reminder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    remind_at TEXT
  )''')
  conn.commit()
  conn.close()
def auto_backup():
  if not os.path.exists('backups'):
    os.makedirs('backups')
  timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  backup_file = f'backups/grades_backup_{timestamp}.db'
  try:
    shutil.copy(DB_PATH, backup_file)
  except Exception as e:
    logger.error(e)
init_db()
auto_backup()
# === КОМАНДА /add ===
@bot.message_handler(commands=['add'])
def add_command(message):
  text = message.text.split()
  if len(text) < 3:
    bot.reply_to(message, "Пример: /add математика 5 4 3")
    return
  chat_id = message.chat.id
  subject = text[1]
  if subject.lower() not in valid:
    bot.reply_to(message, 'Разрешены: математика, русский, английский, физика, химия, биология, история, география, информатика, литература, обж, физкультура, музыка, рисование, технология')
    return
  try:
    grades = [int(x) for x in text[2:] if x.isdigit() and 1 <= int(x) <= 5]
    if not grades:
      bot.reply_to(message, "Нет оценок от 1 до 5")
      return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT weather_city FROM user_settings WHERE user_id = ?', (chat_id,))
    row = cursor.fetchone()
    city = row[0] if row and row[0] else 'владимир'
    weather_data = get_weather(city)
    weather_cond = weather_data['desc'] if weather_data else 'unknown'
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.cursor()
      now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
      for g in grades:
        cursor.execute(
        'INSERT INTO grades (user_id, subject, grade, timestamp, weather) VALUES (?, ?, ?, ?, ?)',(chat_id, subject, g, now, weather_cond))
      bot.reply_to(message, f"✅ Добавлено {len(grades)} оценок по '{subject}'")
  except Exception as e:
    logger.error(e)
# === КОМАНДА /stats ===
@bot.message_handler(commands=['stats'])
def stats_command(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*), AVG(grade) FROM grades WHERE user_id = ?", (chat_id,))
  row = cursor.fetchone()

  if row is None or row[0] == 0:
    bot.reply_to(message, 'Нет оценок')
    conn.close()
    return
  total, avg = row
  avg = round(avg, 2) if avg else 0.0
  df = pd.read_sql('SELECT * FROM grades', conn)
  df['date'] = pd.to_datetime(df['timestamp'])
  df['month'] = df['date'].dt.to_period('M')
  monthly_avg = df.groupby('month')['grade'].mean().round(2)
  today = datetime.now().strftime('%Y-%m-%d')
  if total == 0:
    bot.reply_to(message, "Нет оценок. Сначала добавь через /add")
    conn.close()
    return
  cursor.execute("""
  SELECT subject, COUNT(*), AVG(grade)
  FROM grades
  WHERE user_id = ?
  GROUP BY subject
  ORDER BY subject
  """, (chat_id,))
  subjects = cursor.fetchall()
  conn.close()
  if df.empty:
    bot.reply_to(message, 'Нет данных для анализа.')
    return
  plt.figure(figsize=(8, 4))
  monthly_avg.plot(kind='bar', color='skyblue')
  plt.title("Средний балл по месяцам")
  plt.ylabel('Балл')
  plt.xticks(rotation=45)
  plt.tight_layout()
  buf = BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  bot.send_photo(chat_id, buf)
  buf.close()
  plt.close()
  msg = f"📊 Статистика:\nВсего оценок: {total}\nСредний балл: {avg:.2f}\n\nПо предметам:\n"
  for subj, cnt, s_avg in subjects:
    msg += f"• ✅ {subj}: {s_avg:.2f} ({cnt} оценок)\n"
  msg += '\n📊 Средний балл по месяцам:\n'
  for month, avg in monthly_avg.items():
    msg += f'• ✅ {month}: {avg}\n'
  bot.send_message(chat_id, msg) # ← ВАЖНО: не reply_to, а send_message
@bot.message_handler(commands=['start'])
def start_command(message):
  bot.reply_to(message, '👋 Привет! Я GradeBot - твой школьный помощник по оценкам.\n\n Команды: \n•/insight - твои инсайты\n •/import - выгрузить оценки в базу\n• /add предмет оценка - добавить оценку\n• /stats - показать средний балл\n• /export - скачать CSV файл\n•/graph - присылает график твоих оценок\n•/help или /about - помощь с GradeBot\n\nУдачи в учёбе!💯')
@bot.message_handler(commands=['export'])
def export_command(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("SELECT subject, grade, timestamp FROM grades WHERE user_id = ?", (chat_id,))
  rows = cursor.fetchall()
  conn.close()
  if not rows:
    bot.reply_to(message,'📎 У тебя пока нет оценок для экспорта.')
    return
  output = io.StringIO()
  writer = csv.writer(output)
  writer.writerow(['subject', 'grade', 'timestamp'])
  writer.writerows(rows)
  output.seek(0)
  csv_data = output.getvalue().encode('utf-8-sig')
  bot.send_document(
      message.chat.id,
      io.BytesIO(csv_data),
      caption='📤 Твои оценки (CSV)',
      visible_file_name ='оценки.csv'
  )
@bot.message_handler(commands=['help', 'about'])
def help_command(message):
  bot.reply_to(message,'❓🤖 Помощь по GradeBot\n\n/insight\n→ Твои инсайты\n/add предмет оценка\n→ Добавить одну или несколько оценок.\nПример: /add математика 5 или: /add русский 4 5 3\n\n/today\n→ Показать оценки по дням\n\n/stats\n→ Показать средний балл по всем предметам.\n\n/import - затем присылай csv и все оценки выгрузятся в базу\n\n/export\n→ Получить файл с оценками (CSV).\n\n/graph\n→ Присылает график твоих оценок\n\n⚠️ Советы:\n• Предмет пиши строчными буквами (без заглавных).\n• Оценки - только цифры от 1 до 5.\n• Бот не работает ночью - как и ты! 😴')
@bot.message_handler(commands=['graph'])
def graph_command(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT grade  FROM grades WHERE user_id = ? ORDER BY timestamp', (chat_id,))
  rows = cursor.fetchall()
  conn.close()
  if not rows:
    bot.reply_to(message,'📎 У тебя пока нет оценок для графика.')
    return
  grades = [row[0] for row in rows]
  x = list(range(1, len(grades) + 1))
  y = grades
  plt.figure(figsize=(6,4))
  plt.plot(x, y, 'o-', color='b')
  plt.title("Твои оценки", fontsize=14)
  plt.xlabel("№ оценки")
  plt.ylabel("Балл")
  plt.ylim(0,5.5)
  plt.yticks([1,2,3,4,5])
  plt.grid(True)
  buf = BytesIO()
  plt.savefig(buf, format='png', bbox_inches='tight')
  buf.seek(0)
  plt.close()
  bot.send_photo(chat_id, buf, caption="График 📈")
@bot.message_handler(commands=['import'])
def import_command(message):
  bot.reply_to(message, 'Пришлите CSV-файл с колонками: subject, grade, timestamp')
@bot.message_handler(content_types=['document'])
def document_command(message):
  if not message.document:
    bot.reply_to(message, '❌ Не получилось прочитать файл. Пришлите .csv напрямую.')
  if not message.document.file_name.endswith('.csv'):
    bot.reply_to(message,'❌ Нужен файл .csv' )
    return
  try:
    file_info = bot.get_file(message.document.file_id)
    download_file = bot.download_file(file_info.file_path)
    csv_data = download_file.decode("utf-8")
    df = pd.read_csv(io.StringIO(csv_data), skipinitialspace=True)
    if 'subject' not in df.columns or 'grade' not in df.columns or 'timestamp' not in df.columns:
      bot.reply_to(message, 'В CSV должны быть колонки: subject, grade, timestamp')
      return
    df = df[['subject', 'grade', 'timestamp']]
    df = df[pd.to_numeric(df['grade'], errors='coerce').between(1, 5)]
    df = df.dropna(subset=['grade'])
    if df.empty:
      bot.reply_to(message, 'Нет корректных данных для импорта')
      return
    chat_id = message.chat.id
    conn = sqlite3.connect('grades.db')
    cursor = conn.cursor()
    for _, row in df.iterrows():
      cursor.execute(
        'INSERT INTO grades (user_id, subject, grade, timestamp) VALUES (?, ?, ?, ?)',
        (chat_id, str(row['subject']), int(row['grade']), row['timestamp'])
      )
    conn.commit()
    conn.close()
    bot.reply_to(message, f'✅ Импортировано {len(df)} оценок')
  except Exception as e:
    bot.reply_to(message, '❌ Ошибка при импорте')
    logger.error(e)

def todas(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  today = datetime.now().strftime("%Y-%m-%d")
  cursor.execute("""
  SELECT subject, grade
  FROM grades
  WHERE user_id = ?
  AND timestamp IS NOT NULL
  AND strftime('%Y-%m-%d', timestamp) = ?
  """, (chat_id, today))
  rows = cursor.fetchall()
  conn.close()
  return rows
@bot.message_handler(commands=['today'])
def send_today_stats(message):
  grades = todas(message)
  if not grades:
    bot.reply_to(message, 'Сегодня еще нет оценок.')
  else:
    text = '📚 Сегодня:\n'
    for subj, gr in grades:
      text += f'• {subj}: {gr}\n'
    bot.reply_to(message, text)
@bot.message_handler(commands=['insight'])
def insight(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  df = pd.read_sql('SELECT * FROM grades', conn)
  conn.close()

  if df.empty:
    bot.reply_to(message, 'Нет данных для анализа.')
    return

  w_text = 'Баллы по погоде\n'
  weather_groups = {}
  if 'weather' in df.columns:
    weather_groups = {
        '☀️ Ясно': ['ясно', 'clear', 'солнечно'],
        '⛅ Облачно': ['облачно', 'clouds', 'пасмурно'],
        '🌧️ Дождь': ['дождь', 'rain', 'дождливо'],
        '❄️ Снег': ['снег', 'snow'],
    }
  weather_stats = {}
  for label, keywords in weather_groups.items():
    mask = df['weather'].str.lower().str.contains('|'.join(keywords), na=False)
    subset = df[mask]
    if not subset.empty:
      avg = round(subset['grade'].mean(), 2)
      count = len(subset)
      weather_stats[label] = (avg, count)
  if weather_stats:
    for weather_label, (avg, count) in weather_stats.items():
      w_text += f'{weather_label}: {avg} ({count} оценок)\n'
  else:
    w_text += 'Колонка weather не найдена. Обновите БД!\n'

  df['date'] = pd.to_datetime(df['timestamp'])
  df = df.dropna(subset=['date'])

# Анализ по дням недели
  df['weekday'] = df['date'].dt.dayofweek
  weekday_names = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда',
3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
  df['weekday_name'] = df['weekday'].map(weekday_names)

  weekday_avg = df.groupby('weekday_name')['grade'].mean().round(2).dropna()

# Определяем лучший и худший день
  if len(weekday_avg) > 0:
    if len(weekday_avg) == 1:
      best = worst = weekday_avg.index[0]
      bestv = worstv = float(weekday_avg.iloc[0])
    else:
      best = weekday_avg.idxmax()
      worst = weekday_avg.idxmin()
      bestv = float(weekday_avg[best])
      worstv = float(weekday_avg[worst])

# Анализ по месяцам
  df['month'] = df['date'].dt.to_period('M')
  monthly_avg = df.groupby('month')['grade'].mean().round(2)

# Анализ по предметам
  subject_stats = df.groupby('subject')['grade'].agg(mean='mean', std='std', count='count').round(2)
  subject_stats = subject_stats.sort_values('std')

# Анализ по неделям
  df['week'] = df['date'].dt.isocalendar().week
  weekly_avg = df.groupby('week')['grade'].mean().round(2)

# График стабильности по предметам
  weeks = weekly_avg.index.astype(int).tolist()
  values = weekly_avg.values.tolist()

  plt.figure(figsize=(8, 4))
  subjects = subject_stats.index.astype(str).tolist()
  stds = subject_stats['std'].fillna(0).round(2).tolist()
  plt.bar(subjects, stds, color='lightgray')
  plt.title('Стабильность оценок по предметам')
  plt.ylabel('Стандартное отклонение (σ)')
  plt.xticks(rotation=45)
  plt.tight_layout()

  buf1 = BytesIO()
  plt.savefig(buf1, format='png')
  buf1.seek(0)
  plt.close()

# График динамики по неделям
  plt.figure(figsize=(8, 4))
  plt.plot(weeks, values, marker='o', color='darkgreen')
  plt.xticks(weeks)
  plt.title('Динамика среднего балла по неделям')
  plt.xlabel('Неделя года')
  plt.ylabel('Средний балл')
  plt.grid(True)
  plt.tight_layout()

  buf2 = BytesIO()
  plt.savefig(buf2, format='png')
  buf2.seek(0)
  plt.close()

# Формирование текстового отчета
  growth = ''
  if len(monthly_avg) >= 2:
    last = monthly_avg.iloc[-1]
    prev = monthly_avg.iloc[-2]
    if prev > 0:
      growth = f' ({round((last - prev)/prev*100, 1)}%)'
  text = f"📊 Инсайт по успеваемости:\n\n"
  text += w_text + '\n'
  text += f"📈 Лучший день: {best} (средний балл {bestv})\n"
  text += f"📉 Худший день: {worst} (средний балл {worstv})\n"
  text += f"📅 Текущий месяц: {monthly_avg.iloc[-1]}{growth}\n"
  text += f"📚 Всего оценок: {len(df)}"

# Отправка результатов
  bot.send_photo(chat_id, buf1)
  bot.send_photo(chat_id, buf2)
  bot.reply_to(message, text)
@bot.message_handler(commands=['weather'])
def weather_start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  for region in districts.keys():
    markup.add(types.KeyboardButton(region))
  bot.send_message(message.chat.id, '⛅ Выбери федеральный округ:',
                   reply_markup=markup
                   )
  bot.register_next_step_handler(message, weather_choose_city)
def weather_choose_city(message):
  region = message.text
  if region not in districts:
    bot.send_message(message.chat.id, '❌ Не нашел такой округ. Попробуйте /weather снова.')
    return
  cities = districts[region]
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  for city in cities:
    markup.add(types.KeyboardButton(city))
  bot.send_message(message.chat.id, f'Выбери город в {region} округе:', reply_markup=markup)
  bot.register_next_step_handler(message, weather_save_city, region)
def weather_save_city(message, region):
  city = message.text
  if city not in districts[region]:
    bot.send_message(message.chat.id,'❌ Город не найден в базе. Выбери из списка.')
    return
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, weather_city TEXT)''')
  cursor.execute(''' INSERT OR REPLACE INTO user_settings (user_id, weather_city) VALUES (?, ?)''', (message.chat.id, city))
  conn.commit()
  conn.close()
  bot.send_message(message.chat.id, f'✅ Выбран город: {city}\nТеперь я могу учитывать данные при анализе!', reply_markup=types.ReplyKeyboardRemove())
def coor(city_name):
  city_name = city_name.strip().lower()
  for reg in districts.values():
    for name, coords in reg.items():
      if name.lower() == city_name:
        return coords
  return None
def get_weather(city_name):
  city_name = city_name.strip().lower()
  coords = coor(city_name)
  if not coords:
    logger.warning(f'Город не найден: {city_name}')
    return None
  logger.info(list(weather_cache.keys()))
  if city_name in weather_cache:
    cache_time = weather_cache[city_name]['timestamp']
    if (datetime.now() - cache_time).total_seconds() < CACHE_DURATION:
      logger.info(f'Погода для {city_name} взята из кеша')
      return weather_cache[city_name]['data']
  lat, lon = coords
  api_key = YOUR_API_KEY
  url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru'
  try:
    responce = requests.get(url, timeout=5)
    if responce.status_code == 200:
      data = responce.json()
      weather = {
      'city_name': data.get('name', city_name.title()),
      'temp': data['main']['temp'],
      'desc': data['weather'][0]['description'],
      'feels_like': data['main']['feels_like'],
      'humidity' : data['main']['humidity'],
      'pressure': data['main']['pressure']
      }
      weather_cache[city_name] = {
          'data': weather,
          'timestamp': datetime.now()
      }
      logger.info(f'Погода для {city_name} сохранена в кеш', weather)
      return weather
    else:
      logger.error(f'Ошибка API: {responce.status_code}')
  except Exception as e:
    logger.error(f'Ошибка получение погоды: {e}')
    return None
@bot.message_handler(commands=['weather_now'])
def weather_now(message):
  try:
    chat_id = message.chat.id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT weather_city FROM user_settings WHERE user_id = ?', (chat_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row[0]:
      bot.reply_to(message, 'Сначала выбери город через /weather')
      return
    city = row[0]
    weather = get_weather(city)
    if not weather:
      bot.reply_to(message, f'Не удалось получить погоду для {city}. Проверь интернет или попробуй позже.')
      return
    text = f'''
    ⛅ Погода в {weather.get('city_name')}:
    🌡️ Температура: {weather.get('temp')}°C
    Ощущается как: {weather.get('feels_like')}°C
    Описание: {weather.get('desc')}'''
    bot.reply_to(message, text)
  except Exception as e:
    logger.error(e)
@bot.message_handler(commands=['backup'])
def backup(message):
  chat_id = message.chat.id
  if not os.path.exists('backups'):
    os.makedirs('backups')
  timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  backup_file = f'backups/grades_backup_{timestamp}.db'
  try:
    shutil.copy(DB_PATH, backup_file)
    with open(backup_file, 'rb') as file:
      bot.send_document(
          chat_id,
          file,
          caption=f'Бэкап создан!\n {backup_file}',
          visible_file_name = f'grades_backup_{timestamp}.db'
      )
  except Exception as e:
    logger.error(e)
@bot.message_handler(commands=['remind'])
def remind(message):
  try:
    text = message.text.split()
    if len(text) < 4:
      bot.reply_to(message,'Пример:\n/remind 2026-01-20 15:00 сделать домашку или:\n/remind завтра 15:00 контра по матеше')
      return
    chat_id = message.chat.id
    date_str = text[1]
    time_str = text [2]
    remind_datetime = datetime.strptime(f'{date_str} {time_str[:5]}', '%Y-%m-%d %H:%M')
    remind_text = ' '.join(text[3:])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reminder (user_id, text, remind_at) VALUES (?, ?, ?)',(chat_id, remind_text, remind_datetime.strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    bot.reply_to(message, f'🔔 Напоминание установлено!\n'
    f'{remind_datetime.strftime('%d.%m.%Y в %H:%M')}\n'
    f'{remind_text}')
  except ValueError as e:
    bot.reply_to(message, e)
@bot.message_handler(commands=['reminders'])
def list_reminders(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT id, text, remind_at FROM reminder WHERE user_id = ? ORDER BY remind_at',
                 (chat_id,))
  reminders = cursor.fetchall()
  conn.close()
  if not reminders:
    bot.reply_to(message, '📧 У тебя нет напоминаний')
    return
  tex = '🔔 Твои напоминания:\n\n'
  for i, (id, text, remind_at) in enumerate(reminders, 1):
    tex += f'✅{i}. {remind_at} - {text}\n'
  bot.reply_to(message, tex)
@bot.message_handler(commands=['clearremind'])
def delete(message):
  chat_id = message.chat.id
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('DELETE FROM reminder WHERE user_id = ?', (chat_id,))
  conn.commit()
  deleted = cursor.rowcount
  conn.close()
  bot.reply_to(message, f'✅ Удалено {deleted} напоминаний.')
def check():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  now = datetime.now().strftime('%Y-%m-%d %H:%M')
  cursor.execute('SELECT id, user_id, text FROM reminder WHERE remind_at <= ?', (now,))
  due_reminders = cursor.fetchall()
  if due_reminders:
    for remind in due_reminders:
      id, user_id, tex = remind
      bot.send_message(user_id, f'🔔 Напоминание \n{tex}')
      cursor.execute('DELETE FROM reminder WHERE id = ?', (id,))
      conn.commit()
  conn.close()
@bot.message_handler(commands=['pdf'])
def pdf(message):
  chat_id = message.chat.id
  bot.reply_to(message, 'Генерирую отчет...')
  try:
    filename = f'report_{chat_id}_{datetime.now().strftime('%Y%m%d')}.pdf'
    doc = SimpleDocTemplate(filename, pagesizes=A4)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    elements.append(Paragraph('GradeBot Report', title_style))
    elements.append(Spacer(1, 0.5*cm))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*), AVG(grade) from grades WHERE user_id = ?', (chat_id,))
    total, avg = cursor.fetchone()
    if total == 0:
      bot.reply_to(message, 'Нет оценок для отчета')
      return
    elements.append(Paragraph('GENERAL STATISTICS ', styles['Heading2']))
    stats_data = [
        ['Total average:', str(total)],
        ['Average score:', f'{avg:.2f}'],
        ['Last update:', datetime.now().strftime('%d.%m.%Y')]
    ]
    stats_table = Table(stats_data, colWidths=[4*cm, 3*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph('Grades by subject', styles['Heading2']))
    cursor.execute('''
    SELECT timestamp, grade
    FROM grades
    WHERE user_id = ?
    ORDER BY timestamp
    ''', (chat_id,))
    grades_data = cursor.fetchall()
    if grades_data:
      dates = [datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S').strftime('%d.%m')for d in grades_data]
      grades = [g[1] for g in grades_data]
      plt.figure(figsize=(10, 5))
      plt.plot(dates, grades, marker='o', linewidth=2, markersize=5)
      plt.title('Динамика оценок', fontsize=14)
      plt.xlabel('Дата')
      plt.ylabel('Оценка')
      plt.ylim(1, 5)
      plt.yticks([1, 2, 3, 4, 5, 5.5])
      plt.grid(True, alpha=0.3)
      plt.xticks(rotation=45)
      plt.tight_layout()
      graph_path = f'graph_{chat_id}.png'
      plt.savefig(graph_path, dpi=100)
      plt.close()
      elements.append(Image(graph_path, width=15*cm, height=7*cm))
      elements.append(Spacer(1, 1*cm))
    conn.close()
    doc.build(elements)
    with open(filename, 'rb') as pdf_file:
      bot.send_document(chat_id, pdf_file, caption=f'✅ Твой отчет за {datetime.now().strftime('%d.%m.%Y')}', visible_file_name=f'GradeBot_Report_{datetime.now().strftime('%Y%m%d')}.pdf')
    os.remove(filename)
    if os.path.exists(graph_path):
      os.remove(graph_path)
  except Exception as e:
    logger.error(e)
    import traceback
    traceback.print_exc()
scheduler = BackgroundScheduler()
scheduler.add_job(func=check, trigger='interval', seconds=60)
scheduler.start()
bot.polling(none_stop=True)