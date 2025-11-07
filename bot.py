#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تليجرام لنشر الإعلانات تلقائياً
Telegram Ads Auto-Posting Bot
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from config import BOT_TOKEN, ADMIN_IDS
from database import Database
from scheduler import SchedulerManager
from handlers.admin_panel import AdminPanel
from handlers.scheduler_handler import SchedulerHandler
from handlers.stats import StatsHandler

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramAdsBot:
    def __init__(self):
        self.db = Database()
        self.scheduler_manager = SchedulerManager(self.db)
        self.admin_panel = AdminPanel(self.db)
        self.scheduler_handler = SchedulerHandler(self.db, self.scheduler_manager)
        self.stats_handler = StatsHandler(self.db)
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        user_id = user.id
        
        # حفظ المستخدم في قاعدة البيانات
        self.db.add_user(user_id, user.username, user.first_name)
        
        keyboard = []
        
        # إظهار لوحة التحكم للمسؤولين فقط
        if user_id in ADMIN_IDS:
            keyboard = [
                [InlineKeyboardButton("📋 لوحة التحكم", callback_data="admin_panel")],
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="statistics")],
                [InlineKeyboardButton("⏰ إدارة الجدولة", callback_data="manage_schedule")],
                [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🤖 **مرحباً {user.first_name}!**

أنا بوت نشر الإعلانات التلقائي
أقدم لك خدمات نشر الإعلانات بشكل آلي ومجدول

**المميزات:**
✅ نشر تلقائي للإعلانات
✅ جدولة متقدمة
✅ دعم الوسائط المتعددة
✅ إحصائيات تفصيلية

اختر من القائمة أدناه:
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_text = """
📖 **دليل استخدام البوت**

**للمسؤولين:**
/start - بدء البوت
/admin - لوحة التحكم
/schedule - إدارة الجدولة
/stats - عرض الإحصائيات
/addpost - إضافة منشور جديد
/listposts - عرض المنشورات
/channels - إدارة القنوات

**الجدولة:**
- وضع الفاصل الزمني: نشر كل X دقيقة/ساعة
- وضع الوقت المحدد: نشر في أوقات محددة يومياً

**الدعم:**
للمساعدة تواصل مع المطور
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # التحقق من صلاحيات المسؤول
        if data.startswith('admin_') and user_id not in ADMIN_IDS:
            await query.edit_message_text("⛔ ليس لديك صلاحية للوصول!")
            return
        
        # توجيه الطلبات للمعالجات المناسبة
        if data == "admin_panel":
            await self.admin_panel.show_panel(update, context)
        elif data == "statistics":
            await self.stats_handler.show_stats(update, context)
        elif data == "manage_schedule":
            await self.scheduler_handler.show_schedule_menu(update, context)
        elif data == "help":
            await self.help_command(update, context)
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        
        # تسجيل المعالجات
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.callback_handler))
        
        # تسجيل معالجات إضافية
        self.admin_panel.register_handlers(application)
        self.scheduler_handler.register_handlers(application)
        self.stats_handler.register_handlers(application)
        
        # بدء المجدول
        self.scheduler_manager.start()
        
        # تشغيل البوت
        logger.info("🚀 تم بدء البوت بنجاح!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = TelegramAdsBot()
    bot.run()
