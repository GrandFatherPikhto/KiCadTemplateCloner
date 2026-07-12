import sys
import kipy

def get_selected_footprints_full():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("В KiCad ничего не выделено!")
        return []
        
    # 1. Извлекаем UUID выделения (наш проверенный метод)
    selected_uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                selected_uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            selected_uuids.add(str(item.id.value))
            
    # 2. Строим словарь { UUID_Footprint : set(Имена_цепей) } один раз!
    print("Индексация цепей на плате...")
    nets_map = {}
    if hasattr(board, 'get_pads'):
        for pad in board.get_pads():
            parent_id = ""
            if hasattr(pad, 'parent_id'):
                parent_id = str(pad.parent_id.value) if hasattr(pad.parent_id, 'value') else str(pad.parent_id)
            
            if parent_id:
                if parent_id not in nets_map:
                    nets_map[parent_id] = set()
                
                # Достаем имя цепи (в kipy оно обычно в .net.name)
                try:
                    if hasattr(pad, 'net') and pad.net and hasattr(pad.net, 'name'):
                        nets_map[parent_id].add(pad.net.name)
                except Exception:
                    pass

    # 3. Получаем полные данные футпринтов (наш проверенный метод)
    all_footprints = board.get_footprints()
    selected_fps = [fp for fp in all_footprints 
                    if hasattr(fp, 'id') and str(fp.id.value) in selected_uuids]
    
    return selected_fps, nets_map

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    fps, nets_map = get_selected_footprints_full()
    print(f"\nНайдено выделенных компонентов: {len(fps)}")
    print("=" * 90)
    
    for idx, fp in enumerate(fps, start=1):
        # --- Текстовые данные (проверенный метод) ---
        try:
            ref = fp.reference_field.text.value
            val = fp.value_field.text.value
            fp_name = str(fp.definition.id)
        except Exception:
            ref, val, fp_name = "Err", "Err", "Err"
            
        # --- Координаты (нанометры -> миллиметры) ---
        x = fp.position.x / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        y = fp.position.y / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        
        # --- Цепи (из предварительно построенного словаря) ---
        fp_id_str = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
        nets = nets_map.get(fp_id_str, set())

        # --- Вывод ---
        print(f"[{idx}] {ref:<6} | {val:<15} | X:{x:>7.3f}мм  Y:{y:>7.3f}мм")
        # Выводим имя footprint на отдельной строке, чтобы не растягивать таблицу
        print(f"     FP: {fp_name}")
        
        if nets:
            # Сортируем цепи для красивого вывода
            nets_str = ", ".join(sorted(list(nets)))
            print(f"     └── Nets: {nets_str}")
        else:
            print(f"     └── Nets: (Нет подключенных цепей / N/C)")
        print()