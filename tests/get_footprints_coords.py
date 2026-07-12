import sys
import kipy

def get_selected_footprints_and_all_data():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    selection = board.get_selection()
    if not selection:
        print("В KiCad ничего не выделено!")
        return [], [], board
        
    # Собираем ID именно из выделения
    selected_uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                selected_uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            selected_uuids.add(str(item.id.value))
            
    # Запрашиваем ВСЕ объекты по этим ID одним gRPC-запросом, 
    # чтобы сервер KiCad вернул их полные структуры
    print(f"Запрашиваем данные для {len(selected_uuids)} объектов с сервера...")
    
    # Конвертируем строковые UUID обратно в формат, который ждет get_items_by_id
    # (kipy обычно принимает список строк или объектов ID)
    try:
        raw_ids = [item.id for item in selection if hasattr(item, 'id')]
        if not raw_ids and type(selection[0]).__name__ == "Group":
            # Если выделена группа, вытаскиваем её gRPC-объекты ID
            raw_ids = list(selection[0].proto.items)
        full_items = board.get_items_by_id(raw_ids)
    except Exception as e:
        print(f"Ошибка gRPC запроса get_items_by_id: {e}")
        full_items = []

    # Отфильтровываем только футпринты из всей кучи (дорожки игнорируем)
    footprints = []
    for item in full_items:
        if "Footprint" in type(item).__name__:
            footprints.append(item)
            
    # Дополнительно подтягиваем все пады платы, чтобы узнать их цепи
    all_pads = board.get_pads() if hasattr(board, 'get_pads') else []
            
    return footprints, all_pads, board

def extract_names_kicad10(fp):
    """Вытаскивает Reference и Value из texts_and_fields полного объекта"""
    ref, val = "Unknown", "Unknown"
    if hasattr(fp, 'texts_and_fields') and fp.texts_and_fields:
        for tf in fp.texts_and_fields:
            if hasattr(tf, 'proto') and hasattr(tf.proto, 'type'):
                # type == 1: Reference, type == 2: Value
                if tf.proto.type == 1:
                    ref = str(tf.proto.text.value)
                elif tf.proto.type == 2:
                    val = str(tf.proto.text.value)
    return ref, val

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    fps, all_pads, board = get_selected_footprints_and_all_data()
    print(f"Среди выделенного обнаружено футпринтов: {len(fps)}\n")
    
    for idx, fp in enumerate(fps, start=1):
        ref, val = extract_names_kicad10(fp)
        
        # Считаем координаты из Vector2 (переводим нанометры в мм)
        x = fp.position.x / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        y = fp.position.y / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        
        # Ищем цепи, подключенные к падам ЭТОГО футпринта
        nets = set()
        fp_id_str = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
        
        for pad in all_pads:
            if hasattr(pad, 'parent_id'):
                pad_parent_str = str(pad.parent_id.value) if hasattr(pad.parent_id, 'value') else str(pad.parent_id)
                if pad_parent_str == fp_id_str:
                    # Из разведки мы увидели у Pad свойство .net
                    if hasattr(pad, 'net') and pad.net and hasattr(pad.net, 'name'):
                        nets.add(pad.net.name)
                    elif hasattr(pad, 'proto') and hasattr(pad.proto, 'net_name'):
                        nets.add(pad.proto.net_name)

        print(f"  [{idx}] Ref: {ref:<6} | Value: {val:<15} | Позиция: X={x:.3f}мм, Y={y:.3f}мм")
        if nets:
            print(f"        └── Цепи: {', '.join(sorted(list(nets)))}")
        else:
            print(f"        └── Нет подключенных цепей")
