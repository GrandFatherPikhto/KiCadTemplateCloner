import sys
import kipy

def get_selected_footprints_full():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("В KiCad ничего не выделено!")
        return []
        
    # 1. Извлекаем UUID выделения (проверенный метод)
    selected_uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                selected_uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            selected_uuids.add(str(item.id.value))
            
    # 2. Получаем полные данные только выделенных футпринтов
    all_footprints = board.get_footprints()
    selected_fps = [fp for fp in all_footprints 
                    if hasattr(fp, 'id') and str(fp.id.value) in selected_uuids]
    
    return selected_fps

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    fps = get_selected_footprints_full()
    print(f"Найдено выделенных компонентов: {len(fps)}")
    print("=" * 90)
    
    for idx, fp in enumerate(fps, start=1):
        # --- Текстовые данные ---
        try:
            ref = fp.reference_field.text.value
            val = fp.value_field.text.value
            fp_name = str(fp.definition.id)
        except Exception:
            ref, val, fp_name = "Err", "Err", "Err"
            
        # --- Координаты (нанометры -> миллиметры) ---
        x = fp.position.x / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        y = fp.position.y / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        
        # --- ЦЕПИ (Новый подход: берем пады прямо из футпринта!) ---
        nets = set()
        
        # Ищем пады внутри самого footprint'а
        fp_pads = []
        if hasattr(fp, 'pads') and isinstance(fp.pads, (list, tuple)):
            fp_pads = fp.pads
        elif hasattr(fp, 'get_pads') and callable(fp.get_pads):
            fp_pads = fp.get_pads()
            
        # Извлекаем имена цепей из пинов
        for pad in fp_pads:
            try:
                if hasattr(pad, 'net') and hasattr(pad.net, 'name') and pad.net.name:
                    nets.add(pad.net.name)
            except Exception:
                pass

        # --- Вывод ---
        print(f"[{idx}] {ref:<6} | {val:<15} | X:{x:>7.3f}мм  Y:{y:>7.3f}мм")
        print(f"     FP: {fp_name}")
        
        if nets:
            nets_str = ", ".join(sorted(list(nets)))
            print(f"     └── Nets: {nets_str}")
        else:
            print(f"     └── Nets: (Нет подключенных цепей / N/C)")
        print()