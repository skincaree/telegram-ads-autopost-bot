# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# إعدادات البوت الأساسية
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

# إعدادات قاعدة البيانات
DATABASE_PATH = 'bot_database.db'

# إعدادات الجدولة
DEFAULT_INTERVAL = 60  # دقيقة
MAX_RETRIES = 3

# إعدادات النشر
PARSE_MODES = ['HTML', 'Markdown', 'MarkdownV2']
SUPPORTED_MEDIA = ['photo', 'video', 'document', 'audio']

# رسائل النظام
MESSAGES = {
    'ar': {
        'welcome': 'مرحباً بك في بوت الإعلانات!',
        'unauthorized': 'ليس لديك صلاحية!',
        'success': 'تمت العملية بنجاح ✅',
        'error': 'حدث خطأ ❌'
    },
    'en': {
        'welcome': 'Welcome to Ads Bot!',
        'unauthorized': 'Unauthorized access!',
        'success': 'Operation completed successfully ✅',
        'error': 'An error occurred ❌'
    }
}
