from dataclasses import dataclass

@dataclass
class Service:
    id: int
    category: str
    name: str
    duration_min: int
    price: float

@dataclass
class Master:
    id: int
    name: str

@dataclass
class Client:
    id: int
    name: str
    phone: str
    email: str

@dataclass
class Appointment:
    id: int
    client_id: int
    master_id: int
    service_id: int
    start: str
    end: str

@dataclass
class ScheduleItem:
    id: int
    master_id: int
    date: str
    start_time: str
    end_time: str