# template_cloner/extractor.py

import kipy
from .template import Template, ComponentItem, ViaItem, TrackItem

def _get_selected_uuids(board):
    """Извлекает UUID всех выделенных объектов (включая группы)."""
    selection = board.get_selection()
    if not selection:
        return set()
    uuids = set()
    for item in selection:
        if type(item).__name__ == "Group" and hasattr(item, 'proto'):
            for proto_item in item.proto.items:
                uuids.add(str(proto_item.value))
        elif hasattr(item, 'id') and hasattr(item.id, 'value'):
            uuids.add(str(item.id.value))
    return uuids

def _get_selected_footprints(board, uuids):
    """Возвращает компоненты, чьи UUID есть в наборе."""
    all_footprints = board.get_footprints()
    return [fp for fp in all_footprints
            if hasattr(fp, 'id') and str(fp.id.value) in uuids]

def _get_selected_vias(board, uuids):
    """Возвращает via, чьи UUID есть в наборе."""
    all_vias = board.get_vias() if hasattr(board, 'get_vias') else []
    return [via for via in all_vias
            if hasattr(via, 'id') and str(via.id.value) in uuids]

def _get_selected_tracks(board, uuids):
    """Возвращает дорожки, чьи UUID есть в наборе."""
    all_tracks = board.get_tracks() if hasattr(board, 'get_tracks') else []
    return [tr for tr in all_tracks
            if hasattr(tr, 'id') and str(tr.id.value) in uuids]

def _extract_net_name(obj):
    """Извлекает имя сети из объекта via или track."""
    if hasattr(obj, 'net'):
        if hasattr(obj.net, 'name'):
            return obj.net.name
        return str(obj.net)
    if hasattr(obj, 'proto') and hasattr(obj.proto, 'net'):
        if hasattr(obj.proto.net, 'name'):
            return obj.proto.net.name
        return str(obj.proto.net)
    return ""

def extract_template(output_path: str):
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    uuids = _get_selected_uuids(board)
    if not uuids:
        raise RuntimeError("Не выделено ни одного объекта на плате")

    # --- Компоненты ---
    fps = _get_selected_footprints(board, uuids)
    if not fps:
        raise RuntimeError("Не выделено ни одного компонента")

    # --- Via ---
    vias = _get_selected_vias(board, uuids)
    # --- Дорожки ---
    tracks = _get_selected_tracks(board, uuids)

    # Центр масс по компонентам (как ранее)
    cx = sum(fp.position.x for fp in fps) / len(fps) / 1_000_000.0
    cy = sum(fp.position.y for fp in fps) / len(fps) / 1_000_000.0

    # --- Сбор компонентов ---
    comp_items = []
    for fp in fps:
        ref = fp.reference_field.text.value if hasattr(fp, 'reference_field') else "Unknown"
        val = fp.value_field.text.value if hasattr(fp, 'value_field') else "Unknown"
        fp_name = str(fp.definition.id) if hasattr(fp, 'definition') else "Unknown"
        layer_obj = fp.get_layer() if hasattr(fp, 'get_layer') else None
        layer = layer_obj.name if layer_obj and hasattr(layer_obj, 'name') else "F.Cu"
        angle = fp.orientation.as_degrees() if hasattr(fp, 'orientation') and hasattr(fp.orientation, 'as_degrees') else 0.0
        px = fp.position.x / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        py = fp.position.y / 1_000_000.0 if hasattr(fp, 'position') else 0.0
        comp_items.append(
            ComponentItem(
                ref=ref,
                value=val,
                footprint=fp_name,
                layer=layer,
                angle=angle,
                rel_x=px - cx,
                rel_y=py - cy
            )
        )

    # --- Сбор via ---
    via_items = []
    for via in vias:
        net = _extract_net_name(via)
        drill = via.drill.diameter if hasattr(via, 'drill') and hasattr(via.drill, 'diameter') else 0.3
        diameter = via.diameter if hasattr(via, 'diameter') else 0.6
        layer = "F.Cu"  # via обычно проходные, но можно попробовать получить слой
        if hasattr(via, 'layer'):
            layer = str(via.layer)
        px = via.position.x / 1_000_000.0 if hasattr(via, 'position') else 0.0
        py = via.position.y / 1_000_000.0 if hasattr(via, 'position') else 0.0
        via_items.append(
            ViaItem(
                drill=drill,
                diameter=diameter,
                net=net,
                layer=layer,
                rel_x=px - cx,
                rel_y=py - cy
            )
        )

    # --- Сбор дорожек ---
    track_items = []
    for tr in tracks:
        net = _extract_net_name(tr)
        width = tr.width if hasattr(tr, 'width') else 0.2
        layer = "F.Cu"
        if hasattr(tr, 'layer'):
            layer = str(tr.layer)
        start = tr.start if hasattr(tr, 'start') else None
        end = tr.end if hasattr(tr, 'end') else None
        if start and end:
            sx = start.x / 1_000_000.0 if hasattr(start, 'x') else 0.0
            sy = start.y / 1_000_000.0 if hasattr(start, 'y') else 0.0
            ex = end.x / 1_000_000.0 if hasattr(end, 'x') else 0.0
            ey = end.y / 1_000_000.0 if hasattr(end, 'y') else 0.0
            track_items.append(
                TrackItem(
                    width=width,
                    layer=layer,
                    net=net,
                    start_rel_x=sx - cx,
                    start_rel_y=sy - cy,
                    end_rel_x=ex - cx,
                    end_rel_y=ey - cy
                )
            )

    template = Template(
        origin_x=cx,
        origin_y=cy,
        components=comp_items,
        vias=via_items,
        tracks=track_items
    )
    template.save(output_path)