"""
Базовый класс для всех callback handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class BaseCallbackHandler:
    """Базовый класс для обработчиков callbacks"""
    
    def __init__(self):
        self.logger = logger
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
        """Обработка ошибок"""
        user_id = update.callback_query.from_user.id if update.callback_query else None
        self.logger.error(f"Ошибка в callback для пользователя {user_id}: {error}", exc_info=True)
        
        try:
            from keyboards import keyboards
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка. Попробуйте еще раз.",
                reply_markup=keyboards.main_menu()
            )
        except:
            pass


