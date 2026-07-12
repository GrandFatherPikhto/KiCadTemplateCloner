# get_nets.py

import kipy

def get_selected_footprints(board):
    """Возвращает список выделенных компонентов (Footprint) по UUID."""
    selection = board.get_selection()
    if not selection:
        return []

    selected_uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                selected_uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            selected_uuids.add(str(item.id.value))

    all_footprints = board.get_footprints()
    return [fp for fp in all_footprints
            if hasattr(fp, 'id') and str(fp.id.value) in selected_uuids]

def get_footprint_nets(fp, board):
    """Возвращает множество имён цепей для падов компонента."""
    nets = set()
    try:
        # Способ 1: через get_pads (если есть)
        if hasattr(fp, 'get_pads'):
            pads = fp.get_pads()
            for pad in pads:
                net_name = _extract_net_name(pad)
                if net_name:
                    nets.add(net_name)
        # Способ 2: через board.get_pads() и сравнение по parent_id
        elif hasattr(board, 'get_pads'):
            fp_id = str(fp.id.value) if hasattr(fp.id, 'value') else str(fp.id)
            all_pads = board.get_pads()
            for pad in all_pads:
                if hasattr(pad, 'parent_id'):
                    pad_parent = str(pad.parent_id.value) if hasattr(pad.parent_id, 'value') else str(pad.parent_id)
                    if pad_parent == fp_id:
                        net_name = _extract_net_name(pad)
                        if net_name:
                            nets.add(net_name)
    except Exception as e:
        print(f"Ошибка при получении цепей: {e}")
    return nets

def _extract_net_name(obj):
    """Извлекает имя цепи из объекта пада."""
    # Пробуем разные варианты
    if hasattr(obj, 'net'):
        if hasattr(obj.net, 'name'):
            return obj.net.name
        return str(obj.net)
    if hasattr(obj, 'proto') and hasattr(obj.proto, 'net_name'):
        return obj.proto.net_name
    if hasattr(obj, 'net_code'):
        return str(obj.net_code)
    return None

def main():
    # Подключаемся к KiCad
    kicad = kipy.KiCad()
    board = kicad.get_board()

    # Получаем выделенные футпринты
    fps = get_selected_footprints(board)
    if not fps:
        print("Не выделено ни одного компонента.")
        return

    # Получаем все пады платы (один раз для всех)
    all_pads = board.get_pads() if hasattr(board, 'get_pads') else []

    print(f"Найдено выделенных компонентов: {len(fps)}\n")
    for fp in fps:
        # Извлекаем референс
        try:
            ref = fp.reference_field.text.value
        except AttributeError:
            ref = "Unknown"

        nets = get_footprint_nets(fp, all_pads)
        if nets:
            print(f"{ref}: {', '.join(sorted(nets))}")
        else:
            print(f"{ref}: (нет подключённых цепей)")

if __name__ == "__main__":
    main()