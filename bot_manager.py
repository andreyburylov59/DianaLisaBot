#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DianaLisa Bot Manager - Автоматическая настройка и запуск
"""

import subprocess
import time
import os
import sys
import signal
import psutil
from datetime import datetime, timedelta

# Автоматическая настройка при импорте
def auto_setup():
    """Автоматическая настройка при запуске"""
    # Настройка кодировки для Windows
    if sys.platform == "win32":
        import codecs
        try:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
        except:
            pass  # Игнорируем ошибки кодировки
    
    # Автоматическое переключение в папку проекта
    project_dir = r"E:\Cursor\DianaLisaBot"
    if not os.path.exists('main.py'):
        try:
            os.chdir(project_dir)
        except:
            pass  # Игнорируем ошибки переключения
    
    # Создание папки логов
    os.makedirs('logs', exist_ok=True)

# Выполняем автоматическую настройку
auto_setup()

class BotManager:
    """Простой менеджер для управления ботом"""
    
    def __init__(self):
        self.bot_process = None
        self.running = True
        self.restart_count = 0
        self.restart_times = []
        self.max_restarts = 10
        self.restart_window = 3600
        
        # Устанавливаем обработчики сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def is_bot_running(self):
        """Проверка, запущен ли бот"""
        if self.bot_process is None:
            return False
        
        if self.bot_process.poll() is not None:
            return False
        
        try:
            if self.bot_process.pid:
                proc = psutil.Process(self.bot_process.pid)
                return proc.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return False
    
    def start_bot(self):
        """Запуск бота"""
        try:
            print("Запуск DianaLisa Bot...")
            
            self.bot_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            print(f"Бот запущен с PID: {self.bot_process.pid}")
            return True
            
        except Exception as e:
            print(f"Ошибка запуска бота: {e}")
            return False
    
    def stop_bot(self):
        """Остановка бота"""
        try:
            if self.bot_process and self.is_bot_running():
                print("Остановка бота...")
                self.bot_process.terminate()
                
                try:
                    self.bot_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("Принудительное завершение процесса...")
                    self.bot_process.kill()
                    self.bot_process.wait()
                
                print("Бот остановлен")
            
            # Убиваем все процессы main.py
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'main.py' in ' '.join(proc.info['cmdline']):
                        print(f"Завершение процесса {proc.info['pid']}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
        except Exception as e:
            print(f"Ошибка остановки бота: {e}")
    
    def restart_bot(self):
        """Перезапуск бота"""
        current_time = datetime.now()
        self.restart_times = [t for t in self.restart_times if current_time - t < timedelta(seconds=self.restart_window)]
        
        if len(self.restart_times) >= self.max_restarts:
            print(f"Превышен лимит перезапусков ({self.max_restarts} за час). Остановка.")
            self.running = False
            return False
        
        self.restart_times.append(current_time)
        self.restart_count += 1
        
        print(f"Перезапуск бота #{self.restart_count}")
        
        self.stop_bot()
        time.sleep(5)
        return self.start_bot()
    
    def monitor(self):
        """Мониторинг работы бота"""
        print("Начинаем мониторинг бота...")
        
        while self.running:
            try:
                if not self.is_bot_running():
                    print("Бот не отвечает! Перезапуск...")
                    if not self.restart_bot():
                        break
                else:
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("Получен сигнал остановки...")
                break
            except Exception as e:
                print(f"Ошибка мониторинга: {e}")
                time.sleep(10)
        
        self.stop_bot()
        print("Bot Manager завершен")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        print(f"Получен сигнал {signum}")
        self.running = False

def main():
    """Основная функция - все уже настроено автоматически"""
    print("DianaLisa Bot Manager")
    print("=" * 50)
    print(f"Папка: {os.getcwd()}")
    
    manager = BotManager()
    
    try:
        signal.signal(signal.SIGINT, manager.signal_handler)
        signal.signal(signal.SIGTERM, manager.signal_handler)
        
        if manager.start_bot():
            manager.monitor()
        else:
            print("Не удалось запустить бота")
            sys.exit(1)
            
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
