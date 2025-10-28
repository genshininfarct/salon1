import json
import os
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import List, Optional

from models.entities import Service, Master, Client, Appointment, ScheduleItem


class SalonData:
    DATA_FILE = 'salon_data.json'

    def __init__(self):
        self.services: List[Service] = self._build_services()
        self.masters: List[Master] = [Master(1,'Анна'), Master(2,'Ольга'), Master(3,'Мария'), Master(4,'Дмитрий'), Master(5,'Сергей')]
        self.clients: List[Client] = []
        self.appointments: List[Appointment] = []
        self.schedules: List[ScheduleItem] = []
        self._load()

    def _build_services(self) -> List[Service]:
        items = [
            Service(1, 'Стрижки', 'Женская стрижка (с мытьем и укладкой)', 60, 1500),
            Service(2, 'Стрижки', 'Мужская стрижка (с мытьем и укладкой)', 45, 1000),
            Service(3, 'Стрижки', 'Детская стрижка (до 10 лет)', 30, 700),
            Service(4, 'Стрижки', 'Стрижка челки', 15, 300),
            Service(5, 'Стрижки', 'Креативная/модельная стрижка', 75, 1800),
            Service(6, 'Стрижки', 'Стрижка машинкой', 20, 500),
            Service(7, 'Стрижки', 'Подравнивание кончиков', 20, 600),
            Service(8, 'Окрашивание', 'Окрашивание в один тон', 90, 2500),
            Service(9, 'Окрашивание', 'Тонирование', 60, 1500),
            Service(10, 'Окрашивание', 'Мелирование (классическое, шатуш, балаяж, омбре)', 150, 4000),
            Service(11, 'Окрашивание', 'Колорирование', 120, 3500),
            Service(12, 'Окрашивание', 'Предпигментация / восстановление цвета', 90, 2200),
            Service(13, 'Окрашивание', 'Смывка цвета', 60, 1500),
            Service(14, 'Окрашивание', 'Окрашивание корней', 75, 1800),
            Service(15, 'Окрашивание', 'AIRTOUCH', 180, 5000),
            Service(16, 'Укладки', 'Укладка феном / брашинг', 40, 900),
            Service(17, 'Укладки', 'Укладка на бигуди', 45, 1000),
            Service(18, 'Укладки', 'Вечерняя / Свадебная прическа', 120, 4000),
            Service(19, 'Укладки', 'Гламурные локоны / Голливудские волны', 60, 2000),
            Service(20, 'Укладки', 'Плетение кос (различные техники)', 45, 1200),
            Service(21, 'Укладки', 'Укладка с выпрямлением', 45, 1000),
        ]
        return items

    def _load(self):
        if not os.path.exists(self.DATA_FILE):
            return
        with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        apps = data.get('appointments', [])
        migrated = []
        for a in apps:
            if 'service_name' in a and 'service_id' not in a:
                name = a.get('service_name')
                match = next((s.id for s in self.services if s.name == name), None)
                if match:
                    a['service_id'] = match
                a.pop('service_name', None)
            migrated.append(a)
        self.clients = [Client(**c) for c in data.get('clients', [])]
        loaded_appts = []
        for a in migrated:
            try:
                ap = Appointment(id=a['id'], client_id=a['client_id'], master_id=a['master_id'], service_id=a['service_id'], start=a['start'], end=a['end'])
                loaded_appts.append(ap)
            except Exception:
                continue
        self.appointments = loaded_appts
        self.schedules = [ScheduleItem(**s) for s in data.get('schedules', [])]
        self._save()

    def _save(self):
        data = {
            'clients': [asdict(c) for c in self.clients],
            'appointments': [asdict(a) for a in self.appointments],
            'schedules': [asdict(s) for s in self.schedules]
        }
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_client(self, name: str, phone: str, email: str) -> Client:
        if not name.strip() or not phone.strip() or not email.strip():
            raise ValueError('Все поля клиента обязательны')
        new_id = max([c.id for c in self.clients], default=0) + 1
        client = Client(new_id, name.strip(), phone.strip(), email.strip())
        self.clients.append(client)
        self._save()
        return client

    def find_client_by_name(self, name: str) -> Optional[Client]:
        return next((c for c in self.clients if c.name == name), None)

    def add_schedule(self, master_id: int, date: str, start_time: str, end_time: str) -> ScheduleItem:
        st = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
        en = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')
        if en <= st:
            raise ValueError('Время окончания должно быть позже времени начала')
        new_id = max([s.id for s in self.schedules], default=0) + 1
        sched = ScheduleItem(new_id, master_id, date, start_time, end_time)
        self.schedules.append(sched)
        self._save()
        return sched

    def get_schedules_for(self, master_id: int, date: str) -> List[ScheduleItem]:
        return [s for s in self.schedules if s.master_id == master_id and s.date == date]

    def add_appointment(self, client_id: int, master_id: int, service_id: int, start_dt: datetime) -> Appointment:
        service = next((s for s in self.services if s.id == service_id), None)
        if not service:
            raise ValueError('Услуга не найдена')
        end_dt = start_dt + timedelta(minutes=service.duration_min)
        date = start_dt.strftime('%Y-%m-%d')
        schedules = self.get_schedules_for(master_id, date)
        if not schedules:
            raise ValueError('Мастер не принимает в этот день')
        fits = False
        for s in schedules:
            s_start = datetime.strptime(f"{s.date} {s.start_time}", '%Y-%m-%d %H:%M')
            s_end = datetime.strptime(f"{s.date} {s.end_time}", '%Y-%m-%d %H:%M')
            if start_dt >= s_start and end_dt <= s_end:
                fits = True
                break
        if not fits:
            raise ValueError('Запись не помещается в рабочий график мастера')
        for a in self.appointments:
            if a.master_id != master_id:
                continue
            a_start = datetime.fromisoformat(a.start)
            a_end = datetime.fromisoformat(a.end)
            if not (end_dt <= a_start or start_dt >= a_end):
                raise ValueError('Время уже занято')
        new_id = max([a.id for a in self.appointments], default=0) + 1
        appt = Appointment(new_id, client_id, master_id, service_id, start_dt.isoformat(), end_dt.isoformat())
        self.appointments.append(appt)
        self._save()
        return appt

    def get_client_name(self, client_id: int) -> str:
        client = next((c for c in self.clients if c.id == client_id), None)
        return client.name if client else "Неизвестный клиент"

    def get_master_name(self, master_id: int) -> str:
        master = next((m for m in self.masters if m.id == master_id), None)
        return master.name if master else "Неизвестный мастер"

    def get_service_name(self, service_id: int) -> str:
        service = next((s for s in self.services if s.id == service_id), None)
        return service.name if service else "Неизвестная услуга"
    
    def get_service_duration(self, service_id: int) -> int:
        service = next((s for s in self.services if s.id == service_id), None)
        return service.duration_min if service else 0