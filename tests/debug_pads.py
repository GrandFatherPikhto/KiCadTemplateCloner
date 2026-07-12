import kipy

def debug_component_pads():
    kicad = kipy.KiCad()
    board = kicad.get_board()
    
    # Найдём компонент C403
    # Можно получить все футпринты и найти по reference
    all_footprints = board.get_footprints()
    target_fp = None
    for fp in all_footprints:
        try:
            ref = fp.reference_field.text.value
            if ref == "C403":
                target_fp = fp
                break
        except:
            pass
    
    if not target_fp:
        print("Компонент C403 не найден на плате.")
        return
    
    print("=== Компонент C403 ===")
    print(f"Тип: {type(target_fp)}")
    print(f"ID: {target_fp.id} (value: {target_fp.id.value if hasattr(target_fp.id, 'value') else '?'})")
    
    # Выведем все атрибуты и методы компонента
    attrs = [a for a in dir(target_fp) if not a.startswith('_')]
    print(f"Атрибуты/методы: {attrs}")
    
    # Проверим наличие get_pads, pads, etc.
    for name in ['get_pads', 'pads', 'pad', 'pads_and_vias']:
        if hasattr(target_fp, name):
            val = getattr(target_fp, name)
            print(f"  {name}: {val} (тип: {type(val)})")
            if callable(val):
                try:
                    result = val()
                    print(f"    результат: {result}")
                except Exception as e:
                    print(f"    ошибка: {e}")
    
    # Теперь получим все пады платы и посмотрим на их структуру
    print("\n=== Пады платы ===")
    if hasattr(board, 'get_pads'):
        all_pads = board.get_pads()
        print(f"Всего падов на плате: {len(all_pads)}")
        # Посмотрим первые несколько падов
        for i, pad in enumerate(all_pads[:5]):
            print(f"  Пад {i}: тип {type(pad)}")
            # Выведем атрибуты пада
            pad_attrs = [a for a in dir(pad) if not a.startswith('_')]
            print(f"    Атрибуты: {pad_attrs}")
            # Проверим parent_id
            if hasattr(pad, 'parent_id'):
                print(f"    parent_id: {pad.parent_id} (value: {pad.parent_id.value if hasattr(pad.parent_id, 'value') else '?'})")
            if hasattr(pad, 'net'):
                print(f"    net: {pad.net} (name: {pad.net.name if hasattr(pad.net, 'name') else '?'})")
            # Проверим proto
            if hasattr(pad, 'proto'):
                print(f"    proto: {pad.proto}")
                # Выведем поля proto
                if hasattr(pad.proto, 'DESCRIPTOR'):
                    for field in pad.proto.DESCRIPTOR.fields:
                        print(f"      proto.{field.name} = {getattr(pad.proto, field.name, None)}")
    else:
        print("board.get_pads() отсутствует")
        
    # Попробуем найти пады, принадлежащие C403, через сравнение ID
    target_id = str(target_fp.id.value) if hasattr(target_fp.id, 'value') else str(target_fp.id)
    print(f"\nИщем пады с parent_id == {target_id}")
    found_pads = []
    for pad in all_pads:
        if hasattr(pad, 'parent_id'):
            pad_parent = str(pad.parent_id.value) if hasattr(pad.parent_id, 'value') else str(pad.parent_id)
            if pad_parent == target_id:
                found_pads.append(pad)
    print(f"Найдено падов: {len(found_pads)}")
    for pad in found_pads:
        print(f"  Пад: {pad}")

if __name__ == "__main__":
    debug_component_pads()