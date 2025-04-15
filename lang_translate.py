language_names = {
    'uz': "O'zbek",
    'ru': "Русский",
    'en': "English",
    'tr': "Türkçe"
}

translations = {
    'uz': {
        'welcome_admin': "Salom, Admin! Men crypto yangiliklari botiman. Sizning ID: {user_id}",
        'welcome_user': "Salom! Men crypto yangiliklari botiman. Sizning ID: {user_id}",
        'help_text': """
Men har 5 daqiqada crypto yangiliklari tahlil qilib, muhim yangiliklar haqida xabar beraman.

Mavjud buyruqlar:
/start - Botni ishga tushirish
/help - Yordam ko'rsatish
/latest - Oxirgi muhim yangiliklar
/settings - Sozlamalar
        """,
        'admin_help': """
Admin buyruqlari:
/current_threshold - Hozirgi muhimlik darajasini ko'rsatish
/threshold - Muhimlik darajasini o'zgartirish (0.0-1.0)
/users - Foydalanuvchilar ro'yxati
/stats - Bot statistikasi
/set_balance - Foydalanuvchi balansini o'zgartirish
        """,
        'balance': "Sizning balans: {balance} USDT",
        'not_registered': "Siz hali ro'yxatdan o'tmagansiz. /start buyrug'ini yuborib ro'yxatdan o'ting.",
        'btn_stats': "📊 Statistika",
        'btn_users': "👥 Foydalanuvchilar",
        'btn_settings': "⚙️ Sozlamalar",
        'btn_latest': "📰 Oxirgi yangiliklar",
        'btn_balance': "💰 Balans",
        'btn_help': "ℹ️ Yordam",
        'stats_title': "📊 Bot Statistikasi",
        'stats_users': "👥 Foydalanuvchilar soni: {count}",
        'stats_news': "📰 So'nggi 24 soat ichidagi yangiliklar: {count}",
        'stats_important': "🔔 Muhim yangiliklar (score >= {threshold:.2f}): {count}",
        'users_title': "👥 Foydalanuvchilar ro'yxati:",
        'no_users': "Hozircha foydalanuvchilar yo'q.",
        'user_admin': "👑 Admin",
        'user_regular': "👤 Foydalanuvchi",
        'username_none': "username yo'q",
        'name_none': "ism yo'q",
        'btn_add_balance': "💰 Balans qo'shish",
        'btn_refresh': "🔄 Yangilash",
        'settings_title': "⚙️ Bot Sozlamalari",
        'settings_threshold': "🔢 Muhimlik darajasi: {threshold:.2f}",
        'settings_language': "🌐 Til: {language}",
        'settings_notifications': "🔔 Bildirishnomalar: {status}",
        'btn_change_threshold': "🔢 Muhimlik darajasini o'zgartirish",
        'btn_change_language': "🌐 Tilni o'zgartirish",
        'btn_change_notifications': "🔔 Bildirishnomalarni {action}",
        'notifications_enabled': "Yoqilgan",
        'notifications_disabled': "O'chirilgan",
        'notifications_enable': "yoqish",
        'notifications_disable': "o'chirish",
        'notifications_enabled_message': "✅ Bildirishnomalar yoqildi. Endi siz muhim yangiliklar haqida xabar olasiz.",
        'notifications_disabled_message': "❌ Bildirishnomalar o'chirildi. Endi siz muhim yangiliklar haqida xabar olmaysiz.",
        'no_news': "Hozirda muhim yangiliklar yo'q.",
        'admin_only': "Bu buyruqni faqat bot egasi ishlatishi mumkin.",
        'threshold_current': "Hozirgi muhimlik darajasi: {threshold:.2f}\n\nYangi qiymatni kiriting (0.0-1.0 oralig'ida):",
        'threshold_updated': "✅ Muhimlik darajasi muvaffaqiyatli o'zgartirildi: {threshold:.2f}",
        'threshold_error': "❌ Xato: {error}\n\nIltimos, 0.0 dan 1.0 gacha bo'lgan son kiriting.",
        'cancel_command': "🛑 Amal bekor qilindi.",
        'no_action': "⚠️ Hech qanday amal bajarilmayapti.",
        'enter_user_id': "Foydalanuvchi ID raqamini kiriting:",
        'user_not_found': "❌ Bunday foydalanuvchi topilmadi. Qaytadan urinib ko'ring yoki bekor qilish uchun /cancel buyrug'ini yuboring.",
        'user_info': "Foydalanuvchi: {name} (@{username})\nHozirgi balans: {balance} USDT\n\nYangi balans qiymatini kiriting yoki bekor qilish uchun /cancel buyrug'ini yuboring:",
        'invalid_user_id': "❌ Xato: Foydalanuvchi ID raqami butun son bo'lishi kerak. Bekor qilish uchun /cancel buyrug'ini yuboring.",
        'cancel_balance': "🛑 Balans o'zgartirish amaliyoti bekor qilindi.",
        'balance_updated': "✅ Foydalanuvchi balansi muvaffaqiyatli yangilandi:\n\nFoydalanuvchi: {name} (@{username})\nYangi balans: {balance} USDT",
        'balance_error': "❌ Balansni yangilashda xatolik yuz berdi. Qaytadan urinib ko'ring.",
        'invalid_amount': "❌ Xato: Balans son bo'lishi kerak. Bekor qilish uchun /cancel buyrug'ini yuboring.",
        'choose_language': "🌐 Tilni tanlang:",
        'language_set': "✅ Til muvaffaqiyatli o'zgartirildi: {language}",
        'language_uz': "🇺🇿 O'zbek",
        'language_ru': "🇷🇺 Русский",
        'language_en': "🇬🇧 English",
        'importance': "Muhimlik: {importance}/1.0",
        'source': "Manba: {source}",
        'read_more': "Batafsil o'qish",
        'btn_cancel': "❌ Bekor qilish",
        'btn_analyze': "📊 Analiz",
        'cancel_news': "Bekor qilindi",
        'analyzing': "Tahlil qilinmoqda...",
        'error_data_not_found': "Xatolik: Ma'lumot topilmadi.",
        'price_impact_analysis': "💹 Narx ta'siri tahlili:",
        'insufficient_balance': "❌ Balans yetarli emas. Analiz uchun kamida 0.01 USDT kerak.\n\nJoriy balans: {balance} USDT\n\nHisobingizni to'ldiring va qaytadan urinib ko'ring.",
        'analysis_fee': "💰 Analiz narxi: 0.01 USDT\n\n"
    },
    'tr': {
        'welcome_admin': "Merhaba, Admin! Ben bir kripto haber botuyum. Kimliğiniz: {user_id}",
        'welcome_user': "Merhaba! Ben bir kripto haber botuyum. Kimliğiniz: {user_id}",
        'help_text': """
Her 5 dakikada bir kripto haberlerini analiz eder ve önemli haberler hakkında sizi bilgilendiririm.

Mevcut komutlar:
/start - Botu başlat
/help - Yardım göster
/latest - Son önemli haberler
/settings - Ayarlar
        """,
        'admin_help': """
Admin komutları:
/current_threshold - Mevcut önem eşiğini göster
/threshold - Önem eşiğini değiştir (0.0-1.0)
/users - Kullanıcı listesi
/stats - Bot istatistikleri
/set_balance - Kullanıcı bakiyesini değiştir
        """,
        'balance': "Bakiyeniz: {balance} USDT",
        'not_registered': "Henüz kayıt olmadınız. Kayıt olmak için /start komutunu gönderin.",
        'btn_stats': "📊 İstatistikler",
        'btn_users': "👥 Kullanıcılar",
        'btn_settings': "⚙️ Ayarlar",
        'btn_latest': "📰 Son haberler",
        'btn_balance': "💰 Bakiye",
        'btn_help': "ℹ️ Yardım",
        'stats_title': "📊 Bot İstatistikleri",
        'stats_users': "👥 Kullanıcı sayısı: {count}",
        'stats_news': "📰 Son 24 saatteki haberler: {count}",
        'stats_important': "🔔 Önemli haberler (puan >= {threshold:.2f}): {count}",
        'users_title': "👥 Kullanıcı listesi:",
        'no_users': "Henüz kullanıcı yok.",
        'user_admin': "👑 Admin",
        'user_regular': "👤 Kullanıcı",
        'username_none': "kullanıcı adı yok",
        'name_none': "isim yok",
        'btn_add_balance': "💰 Bakiye ekle",
        'btn_refresh': "🔄 Yenile",
        'settings_title': "⚙️ Bot Ayarları",
        'settings_threshold': "🔢 Önem eşiği: {threshold:.2f}",
        'settings_language': "🌐 Dil: {language}",
        'settings_notifications': "🔔 Bildirimler: {status}",
        'btn_change_threshold': "🔢 Önem eşiğini değiştir",
        'btn_change_language': "🌐 Dili değiştir",
        'btn_change_notifications': "🔔 Bildirimleri {action}",
        'notifications_enabled': "Açık",
        'notifications_disabled': "Kapalı",
        'notifications_enable': "aç",
        'notifications_disable': "kapat",
        'notifications_enabled_message': "✅ Bildirimler açıldı. Artık önemli haberler hakkında bilgilendirileceksiniz.",
        'notifications_disabled_message': "❌ Bildirimler kapatıldı. Artık önemli haberler hakkında bilgilendirilmeyeceksiniz.",
        'no_news': "Şu anda önemli bir haber yok.",
        'admin_only': "Bu komutu yalnızca bot sahibi kullanabilir.",
        'threshold_current': "Mevcut önem eşiği: {threshold:.2f}\n\nYeni değeri girin (0.0-1.0 aralığında):",
        'threshold_updated': "✅ Önem eşiği başarıyla güncellendi: {threshold:.2f}",
        'threshold_error': "❌ Hata: {error}\n\nLütfen 0.0 ile 1.0 arasında bir sayı girin.",
        'cancel_command': "🛑 İşlem iptal edildi.",
        'no_action': "⚠️ Herhangi bir işlem yapılmıyor.",
        'enter_user_id': "Kullanıcı ID'sini girin:",
        'user_not_found': "❌ Böyle bir kullanıcı bulunamadı. Tekrar deneyin veya iptal için /cancel komutunu gönderin.",
        'user_info': "Kullanıcı: {name} (@{username})\nMevcut bakiye: {balance} USDT\n\nYeni bakiye değerini girin veya iptal için /cancel komutunu gönderin:",
        'invalid_user_id': "❌ Hata: Kullanıcı ID'si tam sayı olmalıdır. İptal için /cancel komutunu gönderin.",
        'cancel_balance': "🛑 Bakiye değiştirme işlemi iptal edildi.",
        'balance_updated': "✅ Kullanıcı bakiyesi başarıyla güncellendi:\n\nKullanıcı: {name} (@{username})\nYeni bakiye: {balance} USDT",
        'balance_error': "❌ Bakiye güncellenirken bir hata oluştu. Lütfen tekrar deneyin.",
        'invalid_amount': "❌ Hata: Bakiye bir sayı olmalıdır. İptal için /cancel komutunu gönderin.",
        'choose_language': "🌐 Dil seçin:",
        'language_set': "✅ Dil başarıyla değiştirildi: {language}",
        'language_uz': "🇺🇿 Özbekçe",
        'language_ru': "🇷🇺 Rusça",
        'language_en': "🇬🇧 İngilizce",
        'language_tr': "🇹🇷 Türkçe",
        'importance': "Önem: {importance}/1.0",
        'source': "Kaynak: {source}",
        'read_more': "Daha fazla oku",
        'btn_cancel': "❌ İptal",
        'btn_analyze': "📊 Analiz",
        'cancel_news': "İptal edildi",
        'analyzing': "Analiz ediliyor...",
        'error_data_not_found': "Hata: Veri bulunamadı.",
        'price_impact_analysis': "💹 Fiyat etkisi analizi:",
        'insufficient_balance': "❌ Bakiye yetersiz. Analiz için en az 0.01 USDT gereklidir.\n\nMevcut bakiye: {balance} USDT\n\nLütfen hesabınızı doldurun ve tekrar deneyin.",
        'analysis_fee': "💰 Analiz ücreti: 0.01 USDT\n\n"
    },
    'ru': {
        'welcome_admin': "Привет, Администратор! Я бот криптовалютных новостей. Ваш ID: {user_id}",
        'welcome_user': "Привет! Я бот криптовалютных новостей. Ваш ID: {user_id}",
        'help_text': """
Я анализирую новости криптовалют каждые 5 минут и сообщаю о важных новостях.

Доступные команды:
/start - Запустить бота
/help - Показать помощь
/latest - Последние важные новости
/settings - Настройки
        """,
        'admin_help': """
Команды администратора:
/current_threshold - Показать текущий порог важности
/threshold - Изменить порог важности (0.0-1.0)
/users - Список пользователей
/stats - Статистика бота
/set_balance - Изменить баланс пользователя
        """,
        'balance': "Ваш баланс: {balance} USDT",
        'not_registered': "Вы еще не зарегистрированы. Отправьте команду /start для регистрации.",
        'btn_stats': "📊 Статистика",
        'btn_users': "👥 Пользователи",
        'btn_settings': "⚙️ Настройки",
        'btn_latest': "📰 Последние новости",
        'btn_balance': "💰 Баланс",
        'btn_help': "ℹ️ Помощь",
        'stats_title': "📊 Статистика бота",
        'stats_users': "👥 Количество пользователей: {count}",
        'stats_news': "📰 Новости за последние 24 часа: {count}",
        'stats_important': "🔔 Важные новости (score >= {threshold:.2f}): {count}",
        'users_title': "👥 Список пользователей:",
        'no_users': "Пока нет пользователей.",
        'user_admin': "👑 Админ",
        'user_regular': "👤 Пользователь",
        'username_none': "нет username",
        'name_none': "нет имени",
        'btn_add_balance': "💰 Добавить баланс",
        'btn_refresh': "🔄 Обновить",
        'settings_title': "⚙️ Настройки бота",
        'settings_threshold': "🔢 Порог важности: {threshold:.2f}",
        'settings_language': "🌐 Язык: {language}",
        'settings_notifications': "🔔 Уведомления: {status}",
        'btn_change_threshold': "🔢 Изменить порог важности",
        'btn_change_language': "🌐 Изменить язык",
        'btn_change_notifications': "🔔 {action} уведомления",
        'notifications_enabled': "Включены",
        'notifications_disabled': "Выключены",
        'notifications_enable': "Включить",
        'notifications_disable': "Выключить",
        'notifications_enabled_message': "✅ Уведомления включены. Теперь вы будете получать важные новости.",
        'notifications_disabled_message': "❌ Уведомления выключены. Вы больше не будете получать важные новости.",
        'no_news': "В настоящее время нет важных новостей.",
        'admin_only': "Эта команда доступна только владельцу бота.",
        'threshold_current': "Текущий порог важности: {threshold:.2f}\n\nВведите новое значение (в диапазоне 0.0-1.0):",
        'threshold_updated': "✅ Порог важности успешно изменен: {threshold:.2f}",
        'threshold_error': "❌ Ошибка: {error}\n\nПожалуйста, введите число в диапазоне от 0.0 до 1.0.",
        'cancel_command': "🛑 Действие отменено.",
        'no_action': "⚠️ Нет активных действий.",
        'enter_user_id': "Введите ID пользователя:",
        'user_not_found': "❌ Пользователь не найден. Попробуйте снова или отправьте /cancel для отмены.",
        'user_info': "Пользователь: {name} (@{username})\nТекущий баланс: {balance} USDT\n\nВведите новое значение баланса или отправьте /cancel для отмены:",
        'invalid_user_id': "❌ Ошибка: ID пользователя должен быть целым числом. Отправьте /cancel для отмены.",
        'cancel_balance': "🛑 Изменение баланса отменено.",
        'balance_updated': "✅ Баланс пользователя успешно обновлен:\n\nПользователь: {name} (@{username})\nНовый баланс: {balance} USDT",
        'balance_error': "❌ Ошибка при обновлении баланса. Попробуйте снова.",
        'invalid_amount': "❌ Ошибка: Баланс должен быть числом. Отправьте /cancel для отмены.",
        'choose_language': "🌐 Выберите язык:",
        'language_set': "✅ Язык успешно изменен: {language}",
        'language_uz': "🇺🇿 O'zbek",
        'language_ru': "🇷🇺 Русский",
        'language_en': "🇬🇧 English",
        'language_tr': "🇹🇷 Türkçe",
        'importance': "Важность: {importance}/1.0",
        'source': "Источник: {source}",
        'read_more': "Подробнее",
        'btn_cancel': "❌ Отмена",
        'btn_analyze': "📊 Анализ",
        'cancel_news': "Отменено",
        'analyzing': "Анализирую...",
        'error_data_not_found': "Ошибка: Данные не найдены.",
        'price_impact_analysis': "💹 Анализ влияния на цену:",
        'insufficient_balance': "❌ Недостаточно средств. Для анализа требуется минимум 0.01 USDT.\n\nТекущий баланс: {balance} USDT\n\nПополните счет и попробуйте снова.",
        'analysis_fee': "💰 Стоимость анализа: 0.01 USDT\n\n"
    },
    'en': {
        'welcome_admin': "Hello, Admin! I'm a crypto news bot. Your ID: {user_id}",
        'welcome_user': "Hello! I'm a crypto news bot. Your ID: {user_id}",
        'help_text': """
I analyze crypto news every 5 minutes and notify about important news.

Available commands:
/start - Start the bot
/help - Show help
/latest - Latest important news
/settings - Settings
        """,
        'admin_help': """
Admin commands:
/current_threshold - Show current importance threshold
/threshold - Change importance threshold (0.0-1.0)
/users - List users
/stats - Bot statistics
/set_balance - Set user balance
        """,
        'balance': "Your balance: {balance} USDT",
        'not_registered': "You are not registered yet. Send /start command to register.",
        'btn_stats': "📊 Statistics",
        'btn_users': "👥 Users",
        'btn_settings': "⚙️ Settings",
        'btn_latest': "📰 Latest News",
        'btn_balance': "💰 Balance",
        'btn_help': "ℹ️ Help",
        'stats_title': "📊 Bot Statistics",
        'stats_users': "👥 Number of users: {count}",
        'stats_news': "📰 News in the last 24 hours: {count}",
        'stats_important': "🔔 Important news (score >= {threshold:.2f}): {count}",
        'users_title': "👥 Users list:",
        'no_users': "No users yet.",
        'user_admin': "👑 Admin",
        'user_regular': "👤 User",
        'username_none': "no username",
        'name_none': "no name",
        'btn_add_balance': "💰 Add Balance",
        'btn_refresh': "🔄 Refresh",
        'settings_title': "⚙️ Bot Settings",
        'settings_threshold': "🔢 Importance threshold: {threshold:.2f}",
        'settings_language': "🌐 Language: {language}",
        'settings_notifications': "🔔 Notifications: {status}",
        'btn_change_threshold': "🔢 Change importance threshold",
        'btn_change_language': "🌐 Change language",
        'btn_change_notifications': "🔔 {action} notifications",
        'notifications_enabled': "Enabled",
        'notifications_disabled': "Disabled",
        'notifications_enable': "Enable",
        'notifications_disable': "Disable",
        'notifications_enabled_message': "✅ Notifications enabled. You will now receive important news.",
        'notifications_disabled_message': "❌ Notifications disabled. You will no longer receive important news.",
        'no_news': "There are no important news at the moment.",
        'admin_only': "This command is available only to the bot owner.",
        'threshold_current': "Current importance threshold: {threshold:.2f}\n\nEnter a new value (in the range 0.0-1.0):",
        'threshold_updated': "✅ Importance threshold successfully changed: {threshold:.2f}",
        'threshold_error': "❌ Error: {error}\n\nPlease enter a number in the range 0.0 to 1.0.",
        'cancel_command': "🛑 Action cancelled.",
        'no_action': "⚠️ No active actions.",
        'enter_user_id': "Enter user ID:",
        'user_not_found': "❌ User not found. Try again or send /cancel to cancel.",
        'user_info': "User: {name} (@{username})\nCurrent balance: {balance} USDT\n\nEnter a new balance value or send /cancel to cancel:",
        'invalid_user_id': "❌ Error: User ID must be an integer. Send /cancel to cancel.",
        'cancel_balance': "🛑 Balance change canceled.",
        'balance_updated': "✅ User balance successfully updated:\n\nUser: {name} (@{username})\nNew balance: {balance} USDT",
        'balance_error': "❌ Error updating balance. Please try again.",
        'invalid_amount': "❌ Error: Balance must be a number. Send /cancel to cancel.",
        'choose_language': "🌐 Choose a language:",
        'language_set': "✅ Language successfully changed: {language}",
        'language_uz': "🇺🇿 O'zbek",
        'language_ru': "🇷🇺 Русский",
        'language_en': "🇬🇧 English",
        'language_tr': "🇹🇷 Türkçe",
        'importance': "Importance: {importance}/1.0",
        'source': "Source: {source}",
        'read_more': "Read more",
        'btn_cancel': "❌ Cancel",
        'btn_analyze': "📊 Analyze",
        'cancel_news': "Cancelled",
        'analyzing': "Analyzing...",
        'error_data_not_found': "Error: Data not found.",
        'price_impact_analysis': "💹 Price impact analysis:",
        'insufficient_balance': "❌ Insufficient balance. Analysis requires at least 0.01 USDT.\n\nCurrent balance: {balance} USDT\n\nPlease top up your account and try again.",
        'analysis_fee': "💰 Analysis fee: 0.01 USDT\n\n"
    }
}

format_instructions = {
        'uz': """
    Format your response as follows:
    
    Bitcoin (BTC): [prediction emoji] [short explanation in Uzbek]
    Ethereum (ETH): [prediction emoji] [short explanation in Uzbek]
    Solana (SOL): [prediction emoji] [short explanation in Uzbek]
    Litecoin (LTC): [prediction emoji] [short explanation in Uzbek]
    
    Umumiy xulosa: [general conclusion about overall market impact in Uzbek]
    """,
        'ru': """
    Format your response as follows:
    
    Bitcoin (BTC): [prediction emoji] [short explanation in Russian]
    Ethereum (ETH): [prediction emoji] [short explanation in Russian]
    Solana (SOL): [prediction emoji] [short explanation in Russian]
    Litecoin (LTC): [prediction emoji] [short explanation in Russian]
    
    Общий вывод: [general conclusion about overall market impact in Russian]
    """,
        'en': """
    Format your response as follows:
    
    Bitcoin (BTC): [prediction emoji] [short explanation in English]
    Ethereum (ETH): [prediction emoji] [short explanation in English]
    Solana (SOL): [prediction emoji] [short explanation in English]
    Litecoin (LTC): [prediction emoji] [short explanation in English]
    
    General conclusion: [general conclusion about overall market impact in English]
    """,
    'tr': """
    Yanıtınızı şu şekilde biçimlendirin:
    
    Bitcoin (BTC): [tahmin emojisi] [Türkçe kısa açıklama]
    Ethereum (ETH): [tahmin emojisi] [Türkçe kısa açıklama]
    Solana (SOL): [tahmin emojisi] [Türkçe kısa açıklama]
    Litecoin (LTC): [tahmin emojisi] [Türkçe kısa açıklama]
    
    Genel sonuç: [Türkçe genel piyasa etkisi hakkında sonuç]
    """
}

language_instructions = {
    'uz': "Provide a detailed analysis in UZBEK LANGUAGE with reasoning for each cryptocurrency's price prediction.",
    'ru': "Provide a detailed analysis in RUSSIAN LANGUAGE with reasoning for each cryptocurrency's price prediction.",
    'en': "Provide a detailed analysis in ENGLISH LANGUAGE with reasoning for each cryptocurrency's price prediction.",
    'tr': "Her bir kripto para fiyat tahmini için gerekçeleriyle birlikte TÜRKÇE DİLİNDE ayrıntılı bir analiz yapın."
}