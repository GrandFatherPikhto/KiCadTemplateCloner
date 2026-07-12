# template_cloner/extractor.py

from .adapter import KiCadAdapter
from .template import Template, ComponentItem, ViaItem, TrackItem

def extract_template(output_path: str) -> None:
    adapter = KiCadAdapter()
    
    # Получаем выделенные объекты
    components = adapter.get_selected_components()
    vias = adapter.get_selected_vias()
    tracks = adapter.get_selected_tracks()
    
    # Вычисляем центр масс (пока заглушка)
    origin_x, origin_y = 0.0, 0.0
    if components:
        origin_x = sum(c.x for c in components) / len(components)
        origin_y = sum(c.y for c in components) / len(components)
    
    # Создаём шаблон
    template = Template(
        origin_x=origin_x,
        origin_y=origin_y,
        components=[
            ComponentItem(
                ref=c.ref,
                value=c.value,
                footprint=c.footprint,
                layer=c.layer,
                angle=c.angle,
                rel_x=c.x - origin_x,
                rel_y=c.y - origin_y
            )
            for c in components
        ],
        vias=[
            ViaItem(
                drill=v.drill,
                diameter=v.diameter,
                net=v.net,
                layer=v.layer,
                rel_x=v.x - origin_x,
                rel_y=v.y - origin_y
            )
            for v in vias
        ],
        tracks=[
            TrackItem(
                width=t.width,
                layer=t.layer,
                net=t.net,
                start_rel_x=t.start_x - origin_x,
                start_rel_y=t.start_y - origin_y,
                end_rel_x=t.end_x - origin_x,
                end_rel_y=t.end_y - origin_y
            )
            for t in tracks
        ]
    )
    
    template.save(output_path)