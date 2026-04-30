# 🎓 EduBot — Telegram-бот з Google Sheets
### Хостинг: Render.com (безкоштовно, назавжди) + UptimeRobot

---

## 📊 Структура Google Sheets

### Аркуш `Users`
| phone | name | paid | used |
|---|---|---|---|
| +380971234567 | Діана | 8 | 5 |
| +380501234568 | Олег | 10 | 3 |

### Аркуш `Schedule`
| date | time | is_booked | booked_by_phone |
|---|---|---|---|
| 2025-05-05 | 10:00 | | |
| 2025-05-05 | 14:00 | TRUE | +380971234567 |

---

## 🚀 ПОКРОКОВА ІНСТРУКЦІЯ

---

### КРОК 1 — Створити Google Таблицю

1. Відкрийте [sheets.google.com](https://sheets.google.com) → **Нова таблиця**
2. Перейменуйте перший аркуш: правий клік на вкладці → **Перейменувати** → `Users`
3. Додайте другий аркуш → назвіть `Schedule`
4. Заповніть заголовки (перший рядок):
   - `Users`: `phone` | `name` | `paid` | `used`
   - `Schedule`: `date` | `time` | `is_booked` | `booked_by_phone`
5. Додайте тестові дані
6. **Скопіюйте ID таблиці** з адресного рядка:
   ```
   https://docs.google.com/spreadsheets/d/ВОТ_ЦЕЙ_РЯДОК/edit
   ```

---

### КРОК 2 — Налаштувати Google API

1. Перейдіть на [console.cloud.google.com](https://console.cloud.google.com)
2. Вгорі → **Select a project** → **New Project** → введіть назву → **Create**
3. Зліва → **APIs & Services** → **Library**
4. Знайдіть і увімкніть:
   - `Google Sheets API` → **Enable**
   - `Google Drive API` → **Enable**
5. Зліва → **Credentials** → **+ Create Credentials** → **Service Account**
6. Введіть будь-яке ім'я → **Create and Continue** → **Done**
7. Клікніть на створений service account → вкладка **Keys**
8. **Add Key** → **Create new key** → **JSON** → **Create**
9. Завантажиться файл `credentials.json` — збережіть його!

---

### КРОК 3 — Дати боту доступ до таблиці

1. Відкрийте `credentials.json` текстовим редактором
2. Знайдіть `"client_email"` — скопіюйте email
3. Відкрийте Google Таблицю → **Поділитися** → вставте email → роль **Редактор** → **Надіслати**

---

### КРОК 4 — Створити Telegram-бота

1. Telegram → **@BotFather** → `/newbot`
2. Введіть назву та username бота
3. Скопіюйте **токен**

---

### КРОК 5 — Дізнатись свій Telegram ID

1. Напишіть **@userinfobot** у Telegram
2. Скопіюйте ваш ID

---

### КРОК 6 — Завантажити код на GitHub

1. Зареєструйтесь на [github.com](https://github.com)
2. **+** → **New repository** → назва → **Create**
3. **uploading an existing file** → перетягніть всі файли проекту
4. ⚠️ **НЕ завантажуйте** `credentials.json` та `.env`!
5. **Commit changes**

---

### КРОК 7 — Задеплоїти на Render.com

1. Зареєструйтесь на [render.com](https://render.com) через GitHub
2. **New +** → **Web Service** → підключіть репозиторій → **Connect**
3. Налаштування:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Plan:** `Free`
4. Додайте **Environment Variables**:

| Key | Value |
|---|---|
| `BOT_TOKEN` | токен від BotFather |
| `ADMIN_IDS` | ваш Telegram ID |
| `SPREADSHEET_ID` | ID вашої Google таблиці |
| `GOOGLE_CREDENTIALS_JSON` | весь вміст credentials.json |

> Як вставити credentials.json: відкрийте файл → виділіть весь текст → скопіюйте → вставте у поле значення

5. **Create Web Service** → зачекайте 2-3 хв
6. Скопіюйте URL сервісу: `https://edubot.onrender.com`

---

### КРОК 8 — UptimeRobot (щоб не засинав)

Render безкоштовно засипає через 15 хв. UptimeRobot пінгує кожні 5 хв — бот завжди активний.

1. Зареєструйтесь на [uptimerobot.com](https://uptimerobot.com)
2. **+ Add New Monitor**:
   - **Monitor Type:** `HTTP(s)`
   - **URL:** `https://ВАШ_СЕРВІС.onrender.com/health`
   - **Interval:** `5 minutes`
3. **Create Monitor**

✅ **Бот працює 24/7 безкоштовно і назавжди.**

---

## ⚙️ Що робить адмін у Google Sheets

| Потрібно | Дія |
|---|---|
| Додати вільне заняття | Новий рядок у `Schedule` (date + time) |
| Учень оплатив | Збільшити `paid` в `Users` |
| Заняття відбулось | Збільшити `used` в `Users` |
| Новий учень | Новий рядок у `Users` |

---

## 🔄 Оновлення коду

Завантажте змінені файли на GitHub → Render перезапустить автоматично.
