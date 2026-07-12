import sys
import kipy

def deep_inspect_single_footprint():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("❌ Ошибка: В KiCad ничего не выделено!")
        print("Пожалуйста, разгруппируйте элементы, выделите ОДИН конденсатор и запустите скрипт заново.")
        return
        
    print(f"Количество объектов в выборке: {len(selection)}")
    
    # Берем самый первый объект из выделения
    item = selection[0]
    item_type = type(item).__name__
    
    print(f"\n==========================================")
    print(f"📊 ИНСПЕКЦИЯ ВЫДЕЛЕННОГО ОБЪЕКТА")
    print(f"==========================================")
    print(f"Имя класса: {item_type}")
    print(f"Полный тип: {type(item)}")
    
    # 1. Выводим список всех публичных полей
    attrs = [a for a in dir(item) if not a.startswith('_')]
    print(f"\n🔹 Доступные поля и методы ({len(attrs)} шт.):")
    print(f"   {attrs}")
    
    # 2. Сканируем значения свойств одиночного объекта
    print(f"\n🔹 Анализ значений полей:")
    for attr_name in attrs:
        try:
            val = getattr(item, attr_name)
            val_type = type(val).__name__
            
            if callable(val):
                print(f"  [Method]   .{attr_name}()")
            else:
                # Если это строка, число или булево — выводим значение
                if isinstance(val, (str, int, float, bool)):
                    print(f"  [Property] .{attr_name} : {val_type} = {val}")
                else:
                    print(f"  [Property] .{attr_name} : {val_type}")
                    
                # Если нашли свойство proto, заглянем в его строковое представление
                if attr_name == 'proto':
                    print(f"             └── Содержимое .proto (первые 150 символов):")
                    print(f"                 {str(val).replace('\n', ' ')[:150]}...")
        except Exception as e:
            print(f"  [Error]    Не удалось прочитать .{attr_name}: {e}")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    deep_inspect_single_footprint()
