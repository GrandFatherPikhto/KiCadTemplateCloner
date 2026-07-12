import sys
import kipy

def get_fp_info_kicad10(fp):
    """Извлекает Reference и Value из texts_and_fields в KiCad 10."""
    ref, val = "Unknown", "Unknown"
    if hasattr(fp, 'texts_and_fields') and fp.texts_and_fields:
        try:
            for tf in fp.texts_and_fields:
                if hasattr(tf, 'proto') and hasattr(tf.proto, 'type'):
                    # 1 - Reference, 2 - Value
                    if tf.proto.type == 1:
                        ref = str(tf.proto.text.value)
                    elif tf.proto.type == 2:
                        val = str(tf.proto.text.value)
        except Exception:
            pass
    return ref, val

def analyze_selection():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("В KiCad ничего не выделено!")
        return
        
    print(f"Всего объектов в выделении: {len(selection)}")
    
    # 1. Отбираем компоненты прямо из плоского списка выделения
    footprints = []
    for item in selection:
        if type(item).__name__ in ['Footprint', 'FootprintInstance']:
            footprints.append(item)
            
    print(f"Из них является компонентами (Footprints): {len(footprints)}\n")
    
    if not footprints:
        print("Среди выделенных объектов не обнаружено футпринтов.")
        return

    # 2. Подтягиваем пады платы, чтобы сопоставить их с цепями
    all_pads = board.get_pads() if hasattr(board, 'get_pads') else []
    
    # 3. Выводим информацию по каждому компоненту
    for idx, fp in enumerate(footprints, start=1):
        ref, val = get_fp_info_kicad10(fp)
        
        # Переводим нанометры в миллиметры
        x = fp.position.x / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        y = fp.position.y / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        
        # Собираем цепи этого компонента по его ID
        fp_id_str = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
        nets = set()
        
        for pad in all_pads:
            if hasattr(pad, 'parent_id'):
                p_parent_str = str(pad.parent_id.value) if hasattr(pad.parent_id, 'value') else str(pad.parent_id)
                if p_parent_str == fp_id_str:
                    # Из разведки: у пада есть свойство .net с полем .name внутри, либо в .proto
                    if hasattr(pad, 'net') and pad.net and hasattr(pad.net, 'name') and pad.net.name:
                        nets.add(pad.net.name)
                    elif hasattr(pad, 'proto') and hasattr(pad.proto, 'net_name') and pad.proto.net_name:
                        nets.add(pad.proto.net_name)

        print(f"  [{idx}] Ref: {ref:<6} | Value: {val:<15} | Позиция: X={x:.3f}мм, Y={y:.3f}мм")
        if nets:
            print(f"        └── Цепи: {', '.join(sorted(list(nets)))}")
        else:
            print(f"        └── Нет подключенных цепей")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    analyze_selection()
