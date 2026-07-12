# template_cloner/template.py

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import yaml

@dataclass
class ComponentItem:
    ref: str
    value: str
    footprint: str
    layer: str
    angle: float
    rel_x: float
    rel_y: float

@dataclass
class ViaItem:
    drill: float
    diameter: float
    net: str
    layer: str
    rel_x: float
    rel_y: float

@dataclass
class TrackItem:
    width: float
    layer: str
    net: str
    start_rel_x: float
    start_rel_y: float
    end_rel_x: float
    end_rel_y: float

@dataclass
class Template:
    origin_x: float
    origin_y: float
    components: List[ComponentItem] = field(default_factory=list)
    vias: List[ViaItem] = field(default_factory=list)
    tracks: List[TrackItem] = field(default_factory=list)
    
    def save(self, path: str) -> None:
        data = {
            'origin': [self.origin_x, self.origin_y],
            'components': [
                {
                    'ref': c.ref,
                    'value': c.value,
                    'footprint': c.footprint,
                    'layer': c.layer,
                    'angle': c.angle,
                    'rel_x': c.rel_x,
                    'rel_y': c.rel_y
                }
                for c in self.components
            ],
            'vias': [
                {
                    'drill': v.drill,
                    'diameter': v.diameter,
                    'net': v.net,
                    'layer': v.layer,
                    'rel_x': v.rel_x,
                    'rel_y': v.rel_y
                }
                for v in self.vias
            ],
            'tracks': [
                {
                    'width': t.width,
                    'layer': t.layer,
                    'net': t.net,
                    'start_rel_x': t.start_rel_x,
                    'start_rel_y': t.start_rel_y,
                    'end_rel_x': t.end_rel_x,
                    'end_rel_y': t.end_rel_y
                }
                for t in self.tracks
            ]
        }
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    @classmethod
    def load(cls, path: str) -> 'Template':
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        origin = data['origin']
        return cls(
            origin_x=origin[0],
            origin_y=origin[1],
            components=[
                ComponentItem(**c) for c in data.get('components', [])
            ],
            vias=[
                ViaItem(**v) for v in data.get('vias', [])
            ],
            tracks=[
                TrackItem(**t) for t in data.get('tracks', [])
            ]
        )