import sys
import kipy

def deep_inspect(obj, label="Объект"):
    print(f"\n==========================================")
    print(f"📊 ИНСПЕКЦИЯ: {label}")
    print(f"==========================================")
    print(f"Имя класса: {type(obj).__name__}")
    print(f"Полный тип: {type(obj)}")
    
    # 1. Получаем все публичные атрибуты
    attrs = [a for a in dir(obj) if not a.startswith('_')]
    print(f"\n🔹 Доступные поля и методы ({len(attrs)} шт.):")
    print(f"   {attrs}")
    
    # 2. Сканируем значения свойств
    print(f"\n🔹 Анализ значений полей:")
    for attr_name in attrs:
        try:
            val = getattr(obj, attr_name)
            val_type = type(val).__name__
            
            # Если это метод
            if callable(val):
                print(f"  [Method]   .{attr_name}()")
                # Пробуем вызвать базовые «безопасные» геттеры без аргументов
                if attr_name in ['get', 'all', 'as_list', 'to_list']:
                    try:
                        res = val()
                        print(f"             └── Результат вызова: {type(res).__name__} (len: {len(res) if hasattr(res, '__len__') else 'N/A'})")
                    except Exception as e:
                        print(f"             └── Ошибка вызова: {e}")
            else:
                # Если это свойство
                print(f"  [Property] .{attr_name} : {val_type}")
                # Если это подозрительное свойство вроде 'items' или 'proto', смотрим вглубь
                if attr_name == 'items':
                    print(f"             └── Содержимое .items: {val}")
                    # Проверяем, является ли свойство встроенной gRPC-коллекцией
                    sub_attrs = [sa for sa in dir(val) if not sa.startswith('_')]
                    print(f"             └── Поля внутри .items: {sub_attrs}")
                    
        except Exception as e:
            print(f"  [Error]    Не удалось прочитать .{attr_name}: {e}")

def run_inspection():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    # Сначала заглянем в саму плату, чтобы понять, какие у нее есть коллекции
    print("📋 Базовая инспекция объекта Board...")
    board_attrs = [a for a in dir(board) if not a.startswith('_') and 'get_' in a]
    print(f"Доступные геттеры у Board: {board_attrs}")

    selected = board.get_selection()
    if not selected:
        print("\n❌ Ошибка: В KiCad ничего не выделено! Выделите компонент на плате перед запуском.")
        return
        
    print(f"\nНайдено элементов в корне выборки: {len(selected)}")
    
    # Инспектируем первый элемент (наш загадочный Group)
    group_item = selected[0]
    deep_inspect(group_item, label="Элемент из get_selection()")
    
    # Если у группы есть свойство items, инспектируем его отдельно
    if hasattr(group_item, 'items'):
        deep_inspect(group_item.items, label="Внутреннее свойство Group.items")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    run_inspection()
