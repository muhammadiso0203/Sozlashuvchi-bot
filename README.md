# 🤖 Telegram Guruhlardagi Suhbatlashuvchi Bot

Ushbu Telegram bot guruhlarda kelgan xabarlarni tahlil qilib, belgilangan kalit so'zlar, iboralar yoki botga to'g'ridan-to'g'ri murojaat (reply yoki @tag) qilinganda avtomatik mos javob qaytaradi.

---

## 📋 Xususiyatlari

- 🎯 **Aniq moslik (Exact Match)**: Belgilangan so'z to'liq yozilganda javob beradi (masalan, `salom` -> `Assalomu alaykum!`).
- 🔍 **Matn ichida uchrash (Contains Match)**: Matn ichida ibora uchrashiga qarab javob beradi (masalan, `hayrli tong barchaga` -> `Xayrli tong! ☀️`).
- 🎲 **Tasodifiy javoblar (Random Replies)**: Bitta savolga bir nechta xil javob berish imkoniyati (suhbat tabiiy ko'rinishi uchun).
- 👋 **Yangi a'zolarni kutib olish (Welcome)**: Guruhga yangi qo'shilgan a'zolar bilan ismini aytib, chiroyli va samimiy salomlashish.
- 💬 **Botga reply va @mention**: Foydalanuvchi botning xabariga reply qilsa yoki `@bot_nomi` deb yozsa, alohida javob qaytaradi.
- 🛠 **Admin boshqaruvi**: Botning o'zi orqali yangi so'z va javoblarni qo'shish yoki o'chirish.

---

## ⚙️ O'rnatish va Ishga tushirish

### 1. Kutubxonalarni o'rnatish
Terminal (yoki PowerShell) ochib loyiha papkasida quyidagilarni bajaring:

```bash
pip install -r requirements.txt
```

### 2. .env faylini to'ldirish
[.env](file:///.env) faylini oching va bot tokeningizni kiriting:

```env
BOT_TOKEN=1234567890:AAHxxxxxx...
ADMIN_IDS=123456789
```

### 3. @BotFather da muhim sozlama (Group Privacy)
Bot guruhdagi **barcha** xabarlarni o'qiy olishi uchun quyidagi sozlamani o'chirish shart:
1. Telegramda **[@BotFather](https://t.me/BotFather)** ga kiring.
2. `/mybots` buyrug'ini yuboring va botingizni tanlang.
3. **Bot Settings** -> **Group Privacy** bo'limiga kiring.
4. **Turn off** tugmasini bosing (shunda `Privacy mode is disabled` yozuvi chiqadi).

### 4. Botni ishga tushirish

```bash
python main.py
```

---

## 📝 Yangi so'zlar va javoblar qo'shish

Siz yangi so'zlarni 2 xil usulda qo'shishingiz mumkin:

### 1-usul: Bot orqali admin buyruqlari bilan
- `/admin` (Tugmali admin boshqaruv paneli)
- `/groups` yoki `/guruhlar` (Bot qo'shilgan guruhlar va adminlik holatini ko'rish)
- `/stats` (baza statistikasini ko'rish)
- `/add exact | salom | Va alaykum assalom!`
- `/add contains | narxi qancha | Narxlar haqida ma'lumot olish uchun admin bilan bog'laning.`
- `/del salom` (kalit so'zni o'chirish)

### 2-usul: Fayl orqali
[data/responses.json](file:///data/responses.json) faylini ochib, istalgancha yangi so'z va javob variantlarini qo'shishingiz mumkin.
