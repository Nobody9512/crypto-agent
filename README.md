# Crypto News Telegram Bot

Bu bot cryptocurrency yangiliklar RSS feed'larini har 5 daqiqada tekshiradi va muhim yangiliklar haqida Telegram orqali xabar yuboradi.

## Xususiyatlari

- CoinDesk va CoinTelegraph dan yangiliklari olish
- OpenAI API yordamida yangiliklar ahamiyatini tahlil qilish
- Muhim yangiliklar haqida foydalanuvchilarga Telegram xabarlari yuborish
- SQLite database orqali yangiliklar saqlash
- Har 5 daqiqada yangiliklar tekshirish
- Har bir tekshiruvda faqat 5 ta yangi yangilikni qayta ishlash (resurslarni tejash uchun)
- Yangiliklar uchun muhim nuqtalarni ajratib berish (key points) va o'zbek tilida yuborish

## O'rnatish

1. Repository'ni clone qiling:
```
git clone https://github.com/yourusername/crypto-news-bot.git
cd crypto-news-bot
```

2. Kerakli paketlarni o'rnating:
```
pip install aiogram feedparser aiosqlite openai python-dotenv schedule
```

3. `.env` faylini yarating va quyidagi ma'lumotlarni kiriting:
```
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_USER_ID=your_telegram_user_id
```

## Foydalanish

Botni ishga tushirish uchun:

```
python main.py
```

## Telegram bot komandalar

- `/start` - Botni ishga tushirish va foydalanuvchi ID'sini olish
- `/help` - Yordam xabari ko'rsatish
- `/latest` - Oxirgi muhim yangiliklar ro'yxatini ko'rsatish

## Muhimlik darajasi

Bot yangiliklar muhimligini quyidagi shkala bo'yicha baholaydi:
- 🟡 (0.7-0.8) - O'rtacha muhim, kriptovalyuta narxlarini biroz ta'sir qilishi mumkin
- 🟠 (0.8-0.9) - Muhim, kriptovalyuta narxlariga sezilarli ta'sir qilishi mumkin
- 🔴 (0.9-1.0) - Juda muhim, kriptovalyuta narxlariga katta ta'sir ko'rsatishi kutiladi

## Notes

- TELEGRAM_USER_ID ni o'z Telegram ID'yingiz bilan almashtiring. Buni @userinfobot orqali olishingiz mumkin
- OpenAI API kalitini olish uchun [OpenAI dashboard](https://platform.openai.com/api-keys) saytiga kiring
- Telegram bot yaratish uchun [@BotFather](https://t.me/botfather) dan foydalaning
- Qayta ishlash chegarasi (NEWS_LIMIT) ni main.py faylida o'zgartirishingiz mumkin 