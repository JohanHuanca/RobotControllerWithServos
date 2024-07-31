from dataclasses import dataclass, asdict

@dataclass
class Button:
    id: int
    state: bool

@dataclass
class Servo:
    id: int
    angle: int

@dataclass
class Movement:
    id: int
    name: str

@dataclass
class Position:
    id: int
    order:int
    time: int
    angles: list
    movement_id: int