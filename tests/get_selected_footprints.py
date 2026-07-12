import sys
import kipy

def get_selected_footprints():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("В KiCad ничего не выделено!")
        return [], board
        
    selected_uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                selected_uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            selected_uuids.add(str(item.id.value))
                
    print(f"Извлечено ID объектов из выделения: {len(selected_uuids)}")
    
    all_footprints = board.get_footprints()
    fps = [fp for fp in all_footprints if hasattr(fp, 'id') and str(fp.id.value) in selected_uuids]
    return fps, board

def get_fp_info_kicad10(fp):
    """
    Извлекает Reference и Value из свойства texts_and_fields в KiCad 10.
    """
    ref, val = "Unknown", "Unknown"
    
    # В kipy тексты компонента лежат в свойстве texts_and_fields
    if hasattr(fp, 'texts_and_fields') and fp.texts_and_fields:
        try:
            for tf in fp.texts_and_fields:
                # Проверяем тип текстового поля через его gRPC proto структуру
                if hasattr(tf, 'proto') and hasattr(tf.proto, 'type'):
                    # 1 — это обычно Reference, 2 — Value (стандартные типы полей KiCad)
                    if tf.proto.type == 1 or getattr(tf.proto, 'name', '').lower() == 'reference':
                        ref = str(tf.proto.text.value)
                    elif tf.proto.type == 2 or getattr(tf.proto, 'name', '').lower() == 'value':
                        val = str(tf.proto.text.value)
        except Exception:
            pass
            
    # Запасной хак: если texts_and_fields пуст, ищем в сыром definition
    if ref == "Unknown" and hasattr(fp, 'definition') and fp.definition:
        try:
            val = str(fp.definition.id.footprint_name)
        except Exception:
            pass
            
    return ref, val

def get_fp_detailed_info(fp, board):
    """
    Извлекает координаты (в мм) и список уникальных цепей, подключенных к выводам.
    """
    x_mm = fp.position.x / 1_000_000.0 if hasattr(fp, 'position') else 0.0
    y_mm = fp.position.y / 1_000_000.0 if hasattr(fp, 'position') else 0.0
    
    nets_connected = set()
    
    if hasattr(board, 'get_pads'):
        all_pads = board.get_pads()
        fp_id_str = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
        
        for p in all_pads:
            if hasattr(p, 'parent_id'):
                p_parent_str = str(p.parent_id.value) if hasattr(p.parent_id, 'value') else str(p.parent_id)
                if p_parent_str == fp_id_str:
                    # Извлекаем имя цепи из gRPC структуры площадки
                    if hasattr(p, 'proto') and hasattr(p.proto, 'net_name') and p.proto.net_name:
                        nets_connected.add(p.proto.net_name)
                        
    return x_mm, y_mm, sorted(list(nets_connected))

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    fps, board = get_selected_footprints()
    print(f"Найдено компонентов (Footprints): {len(fps)}\n")
    
    for idx, fp in enumerate(fps, start=1):
        ref, val = get_fp_info_kicad10(fp)
        x, y, nets = get_fp_detailed_info(fp, board)
        
        print(f"  [{idx}] Ref: {ref:<6} | Value: {val:<15} | Позиция: X={x:.3f}мм, Y={y:.3f}мм")
        if nets:
            print(f"        └── Подключенные цепи: {', '.join(nets)}")
        else:
            print(f"        └── Нет подключенных цепей")
