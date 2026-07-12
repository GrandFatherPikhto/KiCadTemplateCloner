import sys
import math
import kipy

def get_selected_footprints_with_nets():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("В KiCad ничего не выделено!")
        return []
        
    # 1. Извлекаем UUID выделения
    selected_uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                selected_uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            selected_uuids.add(str(item.id.value))
            
    # 2. Строим карту позиций ВСЕХ компонентов на плате
    # Формат: { "uuid": (X_nm, Y_nm) }
    all_footprints = board.get_footprints()
    fp_positions = {}
    for fp in all_footprints:
        fp_id = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
        if hasattr(fp, 'position'):
            fp_positions[fp_id] = (fp.position.x, fp.position.y)

    # 3. Геометрический маппинг: связываем пады с компонентами по ближайшим координатам
    # Формат: { "fp_uuid": set("Net1", "Net2") }
    nets_map = {fp_id: set() for fp_id in fp_positions.keys()}
    
    if hasattr(board, 'get_pads'):
        for pad in board.get_pads():
            if not (hasattr(pad, 'position') and hasattr(pad, 'net') and hasattr(pad.net, 'name')):
                continue
                
            net_name = pad.net.name
            if not net_name: continue
                
            px, py = pad.position.x, pad.position.y
            
            # Ищем ближайший футпринт к этому пину
            min_dist = float('inf')
            closest_fp_id = None
            
            for fp_id, (fx, fy) in fp_positions.items():
                # Быстрое вычисление расстояния без извлечения корня (для оптимизации)
                dist_sq = (px - fx)**2 + (py - fy)**2
                if dist_sq < min_dist:
                    min_dist = dist_sq
                    closest_fp_id = fp_id
                    
            # Привязываем цепь к найденному компоненту
            if closest_fp_id:
                nets_map[closest_fp_id].add(net_name)

    # 4. Фильтруем только выделенные компоненты
    selected_fps = [fp for fp in all_footprints 
                    if (str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)) in selected_uuids]
                    
    return selected_fps, nets_map

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    fps, nets_map = get_selected_footprints_with_nets()
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
        
        # --- Цепи (из нашей геометрической карты) ---
        fp_id = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
        nets = nets_map.get(fp_id, set())

        # --- Вывод ---
        print(f"[{idx}] {ref:<6} | {val:<15} | X:{x:>7.3f}мм  Y:{y:>7.3f}мм")
        print(f"     FP: {fp_name}")
        
        if nets:
            nets_str = ", ".join(sorted(list(nets)))
            print(f"     └── Nets: {nets_str}")
        else:
            print(f"     └── Nets: (Нет подключенных цепей / N/C)")
        print()