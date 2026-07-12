import kipy

def find_footprint_name():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    # Берем первый попавшийся компонент на плате
    footprints = board.get_footprints()
    if not footprints:
        print("На плате нет компонентов!")
        return
        
    fp = footprints[0]
    print(f"Анализируем компонент (Ref: {fp.reference_field.text.value})\n")
    
    print("--- Ищем строку с двоеточием ':' (стандартный формат FPID) ---")
    for attr in dir(fp):
        if attr.startswith('_'): continue
        try:
            val = getattr(fp, attr)
            val_str = str(val)
            
            # Если в строковом представлении атрибута есть двоеточие - скорее всего это наш футпринт!
            if ':' in val_str and not val_str.startswith('<'):
                print(f"НАЙДЕНО В: {attr:<25} | Значение: {val_str[:150]}")
        except Exception:
            pass

    print("\n--- Также выводим ВСЕ не-методы на случай, если формат без двоеточия ---")
    for attr in dir(fp):
        if attr.startswith('_'): continue
        try:
            val = getattr(fp, attr)
            if not callable(val):
                val_str = str(val)
                # Отсекаем пустые и служебные
                if val_str and not val_str.startswith('<') and len(val_str) > 3:
                    print(f"{attr:<25} = {val_str[:120]}")
        except Exception:
            pass

if __name__ == "__main__":
    find_footprint_name()
