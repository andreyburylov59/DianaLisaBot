"""
Базовые CI/CD тесты - проверка импортов и синтаксиса
Эти тесты не требуют запуска бота или базы данных
"""

import sys
import importlib.util

def test_import_module(module_name, file_path):
    """Проверка, что модуль можно импортировать"""
    print(f"[TEST] Проверка модуля {module_name}...")
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            print(f"[FAIL] Не удалось найти модуль {file_path}")
            return False
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        print(f"[PASS] Модуль {module_name} импортирован успешно")
        return True
    except Exception as e:
        print(f"[FAIL] Ошибка при импорте {module_name}: {e}")
        return False

def test_file_exists(file_path):
    """Проверка существования файла"""
    import os
    exists = os.path.exists(file_path)
    status = "[PASS]" if exists else "[FAIL]"
    print(f"{status} Файл {file_path}: {'существует' if exists else 'не найден'}")
    return exists

def main():
    print("="*50)
    print("CI/CD БАЗОВЫЕ ТЕСТЫ")
    print("="*50)
    
    all_passed = True
    
    # Тест 1: Проверка наличия основных файлов
    print("\n[1] Проверка наличия основных файлов...")
    files_to_check = [
        'main.py',
        'callbacks.py', 
        'database.py',
        'keyboards.py',
        'config.py',
        'requirements.txt'
    ]
    
    for file_path in files_to_check:
        if not test_file_exists(file_path):
            all_passed = False
    
    # Тест 2: Проверка синтаксиса Python файлов
    print("\n[2] Проверка синтаксиса основных модулей...")
    import py_compile
    
    python_files = [
        'main.py',
        'callbacks.py',
        'database.py', 
        'keyboards.py',
        'config.py',
        'registration.py',
        'training.py'
    ]
    
    for file_path in python_files:
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"[PASS] Синтаксис {file_path} корректен")
        except py_compile.PyCompileError as e:
            print(f"[FAIL] Ошибка синтаксиса в {file_path}: {e}")
            all_passed = False
    
    # Тест 3: Проверка requirements.txt
    print("\n[3] Проверка requirements.txt...")
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if len(lines) > 0:
                print(f"[PASS] requirements.txt содержит {len(lines)} зависимостей")
            else:
                print("[FAIL] requirements.txt пуст")
                all_passed = False
    except Exception as e:
        print(f"[FAIL] Ошибка при чтении requirements.txt: {e}")
        all_passed = False
    
    # Итоговый результат
    print("\n" + "="*50)
    if all_passed:
        print("[SUCCESS] ВСЕ БАЗОВЫЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("="*50)
        sys.exit(0)
    else:
        print("[FAILED] НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        print("="*50)
        sys.exit(1)

if __name__ == '__main__':
    main()

