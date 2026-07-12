# template_cloner/applier.py

import math
import kipy
from .template import Template

def create_via(board, x_mm, y_mm, drill_mm, diameter_mm, net_name, layer="F.Cu"):
    """Создаёт via в указанной позиции."""
    # Конвертация в нанометры
    x_nm = int(x_mm * 1_000_000)
    y_nm = int(y_mm * 1_000_000)
    drill_nm = int(drill_mm * 1_000_000)
    diam_nm = int(diameter_mm * 1_000_000)
    
    try:
        from kipy import Via
        via = Via()
        via.position.x = x_nm
        via.position.y = y_nm
        via.drill.diameter = drill_nm
        via.diameter = diam_nm
        if net_name:
            via.net.name = net_name
        # layer можно попробовать задать через via.layer, если есть
        if hasattr(via, 'layer'):
            via.layer = layer
        # Создаём via через board.create_items
        board.create_items([via])
    except Exception as e:
        print(f"Ошибка создания via: {e}")

def create_track(board, start_x_mm, start_y_mm, end_x_mm, end_y_mm, width_mm, net_name, layer="F.Cu"):
    """Создаёт дорожку между двумя точками."""
    sx = int(start_x_mm * 1_000_000)
    sy = int(start_y_mm * 1_000_000)
    ex = int(end_x_mm * 1_000_000)
    ey = int(end_y_mm * 1_000_000)
    w = int(width_mm * 1_000_000)
    
    try:
        from kipy import Track
        tr = Track()
        tr.start.x = sx
        tr.start.y = sy
        tr.end.x = ex
        tr.end.y = ey
        tr.width = w
        if net_name:
            tr.net.name = net_name
        if hasattr(tr, 'layer'):
            tr.layer = layer
        board.create_items([tr])
    except Exception as e:
        print(f"Ошибка создания дорожки: {e}")

def apply_template(input_path: str, new_origin_x: float, new_origin_y: float):
    template = Template.load(input_path)
    kicad = kipy.KiCad()
    board = kicad.get_board()

    # --- 1. Перемещаем компоненты ---
    all_footprints = board.get_footprints()
    ref_to_fp = {}
    for fp in all_footprints:
        try:
            ref = fp.reference_field.text.value
            ref_to_fp[ref] = fp
        except AttributeError:
            continue

    for comp in template.components:
        ref = comp.ref
        if ref not in ref_to_fp:
            print(f"Предупреждение: компонент {ref} не найден, пропускаем")
            continue
        fp = ref_to_fp[ref]
        new_x = new_origin_x + comp.rel_x
        new_y = new_origin_y + comp.rel_y
        fp.position.x = int(new_x * 1_000_000)
        fp.position.y = int(new_y * 1_000_000)
        if hasattr(fp, 'orientation'):
            fp.orientation = math.radians(comp.angle)

    # --- 2. Создаём via ---
    for via_item in template.vias:
        new_x = new_origin_x + via_item.rel_x
        new_y = new_origin_y + via_item.rel_y
        create_via(board, new_x, new_y, via_item.drill, via_item.diameter, via_item.net, via_item.layer)

    # --- 3. Создаём дорожки ---
    for tr_item in template.tracks:
        new_sx = new_origin_x + tr_item.start_rel_x
        new_sy = new_origin_y + tr_item.start_rel_y
        new_ex = new_origin_x + tr_item.end_rel_x
        new_ey = new_origin_y + tr_item.end_rel_y
        create_track(board, new_sx, new_sy, new_ex, new_ey, tr_item.width, tr_item.net, tr_item.layer)

    # --- 4. Фиксируем изменения ---
    board.push_commit()
    print(f"Шаблон применён в ({new_origin_x}, {new_origin_y})")