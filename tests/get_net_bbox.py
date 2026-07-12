import kipy

def get_selected_footprints(board):
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

def extract_net_name(pad):
    if hasattr(pad, 'net'):
        if hasattr(pad.net, 'name'):
            return pad.net.name
        return str(pad.net)
    if hasattr(pad, 'proto') and hasattr(pad.proto, 'net'):
        if hasattr(pad.proto.net, 'name'):
            return pad.proto.net.name
        return str(pad.proto.net)
    return None

def get_footprint_nets(fp, board):
    nets = set()
    try:
        bbox = fp.get_item_bounding_box()
        all_pads = board.get_pads()
        for pad in all_pads:
            pos = pad.position
            if (bbox.x_min <= pos.x <= bbox.x_max and
                bbox.y_min <= pos.y <= bbox.y_max):
                net = extract_net_name(pad)
                if net:
                    nets.add(net)
    except Exception as e:
        print(f"Ошибка: {e}")
    return nets

def main():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    fps = get_selected_footprints(board)
    if not fps:
        print("Нет выделенных компонентов")
        return
    for fp in fps:
        ref = fp.reference_field.text.value if hasattr(fp, 'reference_field') else "Unknown"
        nets = get_footprint_nets(fp, board)
        print(f"{ref}: {', '.join(nets) if nets else '(нет цепей)'}")

if __name__ == "__main__":
    main()