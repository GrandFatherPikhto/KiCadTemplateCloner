# template_cloner/adapter.py

from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Component:
    ref: str
    value: str
    footprint: str
    layer: str
    x: float
    y: float
    angle: float

@dataclass
class Via:
    x: float
    y: float
    drill: float
    diameter: float
    net: str
    layer: str

@dataclass
class Track:
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    width: float
    layer: str
    net: str

class KiCadAdapter:
    """Адаптер для работы с KiCad через pcbnew или kipy"""
    
    def __init__(self):
        # Позже — инициализация соединения с открытой платой
        pass
    
    def get_selected_components(self) -> List[Component]:
        """Возвращает список выделенных компонентов"""
        raise NotImplementedError
    
    def get_selected_vias(self) -> List[Via]:
        """Возвращает список выделенных переходных отверстий"""
        raise NotImplementedError
    
    def get_selected_tracks(self) -> List[Track]:
        """Возвращает список выделенных дорожек"""
        raise NotImplementedError
    
    def place_component(self, comp: Component) -> None:
        """Перемещает или создаёт компонент"""
        raise NotImplementedError
    
    def place_via(self, via: Via) -> None:
        """Создаёт переходное отверстие"""
        raise NotImplementedError
    
    def place_track(self, track: Track) -> None:
        """Создаёт дорожку"""
        raise NotImplementedError
    
    def commit(self) -> None:
        """Фиксирует изменения в плате"""
        raise NotImplementedError
    
    def rollback(self) -> None:
        """Откатывает изменения"""
        raise NotImplementedError