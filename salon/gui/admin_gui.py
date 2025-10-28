from datetime import datetime, timedelta

from services.salon_data import SalonData

import customtkinter as ctk
from tkinter import messagebox

try:
    from tkcalendar import DateEntry
    TKCAL_AVAILABLE = True
except Exception:
    TKCAL_AVAILABLE = False


class AdminGUI(ctk.CTk):
    def __init__(self, data: SalonData):
        super().__init__()
        self.data = data
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
        self.title('Salon Admin — запись')
        self.geometry('1200x800')

        self.tabview = ctk.CTkTabview(self, width=1150)
        self.tabview.pack(padx=20, pady=20, expand=True, fill='both')
        self.tab_clients = self.tabview.add('Клиенты')
        self.tab_records = self.tabview.add('Записи')

        self._build_clients_tab()
        self._build_records_tab()

    def _build_clients_tab(self):
        f = self.tab_clients
        left = ctk.CTkFrame(f)
        left.grid(row=0, column=0, sticky='ns', padx=10, pady=10)
        right = ctk.CTkFrame(f)
        right.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(left, text='Новый клиент').grid(row=0, column=0, pady=6)
        self.c_name = ctk.CTkEntry(left, placeholder_text='Имя')
        self.c_phone = ctk.CTkEntry(left, placeholder_text='Телефон')
        self.c_email = ctk.CTkEntry(left, placeholder_text='Email')
        self.c_name.grid(row=1, column=0, pady=4)
        self.c_phone.grid(row=2, column=0, pady=4)
        self.c_email.grid(row=3, column=0, pady=4)
        ctk.CTkButton(left, text='Добавить', command=self._on_add_client).grid(row=4, column=0, pady=8)

        ctk.CTkLabel(right, text='Список клиентов').grid(row=0, column=0, pady=6)
        self.clients_text = ctk.CTkTextbox(right, width=780, height=640)
        self.clients_text.grid(row=1, column=0, sticky='nsew')
        right.grid_rowconfigure(1, weight=1)
        self._refresh_clients_text()

        # Добавить кнопку очистки
        ctk.CTkButton(left, text='Очистить все данные', 
                    command=self._clear_all_data, 
                    fg_color='red', hover_color='darkred').grid(row=5, column=0, pady=8)

    def _clear_all_data(self):
        if messagebox.askyesno('Подтверждение', 'Вы уверены что хотите удалить ВСЕ данные?'):
            self.data.clients = []
            self.data.appointments = []
            self.data.schedules = []
            self.data._save()
            self._refresh_clients_text()
            self._refresh_schedule_table()
            messagebox.showinfo('Готово', 'Все данные очищены')

    def _on_add_client(self):
        try:
            client = self.data.add_client(self.c_name.get(), self.c_phone.get(), self.c_email.get())
            messagebox.showinfo('Успех', f'Клиент {client.name} добавлен')
            self._refresh_clients_text()
            # Обновляем комбобокс клиентов в записях
            self.client_cb.configure(values=[c.name for c in self.data.clients])
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def _refresh_clients_text(self):
        self.clients_text.delete('1.0', 'end')
        for c in self.data.clients:
            self.clients_text.insert('end', f"{c.id}. {c.name} — {c.phone} — {c.email}\n")

    def _build_records_tab(self):
        f = self.tab_records
        
        # Левая часть - форма создания записи и графика
        left_frame = ctk.CTkFrame(f)
        left_frame.grid(row=0, column=0, sticky='ns', padx=10, pady=10)
        
        # Правая часть - таблица с расписанием и записями
        right_frame = ctk.CTkFrame(f)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        f.grid_columnconfigure(1, weight=1)
        f.grid_rowconfigure(0, weight=1)

        # === ФОРМА СОЗДАНИЯ ЗАПИСИ ===
        form_frame = ctk.CTkFrame(left_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text='Создать запись', font=('Arial', 14, 'bold')).pack(pady=6)

        # Клиент
        client_frame = ctk.CTkFrame(form_frame)
        client_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(client_frame, text='Клиент:').pack(side='left', padx=5)
        self.client_cb = ctk.CTkComboBox(client_frame, values=[c.name for c in self.data.clients], width=200)
        self.client_cb.pack(side='left', padx=5, pady=4, fill='x', expand=True)

        # Мастер
        master_frame = ctk.CTkFrame(form_frame)
        master_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(master_frame, text='Мастер:').pack(side='left', padx=5)
        self.master_cb = ctk.CTkComboBox(master_frame, values=[m.name for m in self.data.masters], width=200)
        self.master_cb.pack(side='left', padx=5, pady=4, fill='x', expand=True)

        # Услуга с отображением времени
        service_frame = ctk.CTkFrame(form_frame)
        service_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(service_frame, text='Услуга:').pack(side='left', padx=5)
        
        # Создаем список услуг с указанием времени
        service_values = []
        for s in self.data.services:
            hours = s.duration_min // 60
            minutes = s.duration_min % 60
            if hours > 0 and minutes > 0:
                time_str = f"({hours}ч {minutes}мин)"
            elif hours > 0:
                time_str = f"({hours}ч)"
            else:
                time_str = f"({minutes}мин)"
            service_values.append(f"{s.id}. {s.name} {time_str}")
        
        self.service_cb = ctk.CTkComboBox(service_frame, 
                                        values=service_values, 
                                        width=200,
                                        command=self._on_service_selected)
        self.service_cb.pack(side='left', padx=5, pady=4, fill='x', expand=True)

        # Дата
        date_frame = ctk.CTkFrame(form_frame)
        date_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(date_frame, text='Дата:').pack(side='left', padx=5)
        if TKCAL_AVAILABLE:
            self.book_date = DateEntry(
                date_frame, 
                date_pattern='yyyy-mm-dd',
                font=('Arial', 12),
                width=15
            )
            self.book_date.pack(side='left', padx=5, pady=4)
        else:
            self.book_date = ctk.CTkEntry(date_frame, placeholder_text='YYYY-MM-DD', width=150)
            self.book_date.pack(side='left', padx=5, pady=4)

        # Время
        time_frame = ctk.CTkFrame(form_frame)
        time_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(time_frame, text='Время:').pack(side='left', padx=5)
        self.time_entry = ctk.CTkEntry(time_frame, placeholder_text='например 10:30', width=150)
        self.time_entry.pack(side='left', padx=5, pady=4)

        # Информация о времени окончания
        self.time_info_label = ctk.CTkLabel(form_frame, text="", text_color="lightblue")
        self.time_info_label.pack(pady=2)

        # Кнопка создания записи
        ctk.CTkButton(form_frame, text='Создать запись', 
                     command=self._on_create_appointment).pack(pady=8)

        # Разделитель
        sep1 = ctk.CTkFrame(left_frame, height=2, fg_color='gray30')
        sep1.pack(fill='x', padx=5, pady=10)

        # === ФОРМА ДОБАВЛЕНИЯ ГРАФИКА ===
        schedule_frame = ctk.CTkFrame(left_frame)
        schedule_frame.pack(fill='x', padx=5, pady=5)
        
        ctk.CTkLabel(schedule_frame, text='График мастера', font=('Arial', 14, 'bold')).pack(pady=6)

        # Мастер для графика
        sched_master_frame = ctk.CTkFrame(schedule_frame)
        sched_master_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(sched_master_frame, text='Мастер:').pack(side='left', padx=5)
        self.schedule_master_cb = ctk.CTkComboBox(sched_master_frame, 
                                                values=[m.name for m in self.data.masters], 
                                                width=200)
        self.schedule_master_cb.pack(side='left', padx=5, pady=4, fill='x', expand=True)

        # Дата графика
        sched_date_frame = ctk.CTkFrame(schedule_frame)
        sched_date_frame.pack(fill='x', padx=5, pady=2)
        ctk.CTkLabel(sched_date_frame, text='Дата:').pack(side='left', padx=5)
        if TKCAL_AVAILABLE:
            self.schedule_date = DateEntry(
                sched_date_frame, 
                date_pattern='yyyy-mm-dd',
                font=('Arial', 12),
                width=15
            )
            self.schedule_date.pack(side='left', padx=5, pady=4)
        else:
            self.schedule_date = ctk.CTkEntry(sched_date_frame, placeholder_text='YYYY-MM-DD', width=150)
            self.schedule_date.pack(side='left', padx=5, pady=4)

        # Время начала и окончания
        sched_time_frame = ctk.CTkFrame(schedule_frame)
        sched_time_frame.pack(fill='x', padx=5, pady=2)
        
        ctk.CTkLabel(sched_time_frame, text='Начало:').pack(side='left', padx=5)
        self.s_start = ctk.CTkEntry(sched_time_frame, placeholder_text='HH:MM', width=80)
        self.s_start.pack(side='left', padx=5, pady=4)
        
        ctk.CTkLabel(sched_time_frame, text='Конец:').pack(side='left', padx=5)
        self.s_end = ctk.CTkEntry(sched_time_frame, placeholder_text='HH:MM', width=80)
        self.s_end.pack(side='left', padx=5, pady=4)

        # Кнопка добавления графика
        ctk.CTkButton(schedule_frame, text='Добавить график', 
                     command=self._on_add_schedule).pack(pady=8)

        # === ТАБЛИЦА РАСПИСАНИЯ И ЗАПИСЕЙ ===
        ctk.CTkLabel(right_frame, text='Расписание мастеров и записи клиентов', 
                    font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Текстовое поле для отображения данных
        self.schedule_text = ctk.CTkTextbox(right_frame, width=800, height=650)
        self.schedule_text.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Кнопка обновления таблицы
        ctk.CTkButton(right_frame, text='Обновить таблицу', 
                     command=self._refresh_schedule_table).pack(pady=5)
        
        # Первоначальное заполнение таблицы
        self._refresh_schedule_table()

    def _on_service_selected(self, choice):
        """Обновляет информацию о времени при выборе услуги"""
        try:
            if choice:
                service_id = int(choice.split('.')[0])
                duration = self.data.get_service_duration(service_id)
                
                hours = duration // 60
                minutes = duration % 60
                
                if hours > 0 and minutes > 0:
                    duration_str = f"{hours}ч {minutes}мин"
                elif hours > 0:
                    duration_str = f"{hours}ч"
                else:
                    duration_str = f"{minutes}мин"
                
                self.time_info_label.configure(text=f"Продолжительность услуги: {duration_str}")
        except Exception:
            self.time_info_label.configure(text="")

    def _on_create_appointment(self):
        try:
            client_name = self.client_cb.get()
            master_name = self.master_cb.get()
            service_text = self.service_cb.get()
            
            if not client_name or not master_name or not service_text:
                raise ValueError('Заполните все поля')
            
            client = self.data.find_client_by_name(client_name)
            if not client:
                raise ValueError('Клиент не найден')
            
            master = next((m for m in self.data.masters if m.name == master_name), None)
            if not master:
                raise ValueError('Мастер не найден')
            
            service_id = int(service_text.split('.')[0])
            date_str = self.book_date.get()
            time_str = self.time_entry.get()
            
            start_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            
            # Получаем информацию об услуге для отображения
            service = next((s for s in self.data.services if s.id == service_id), None)
            if service:
                end_dt = start_dt + timedelta(minutes=service.duration_min)
                duration_info = f" ({service.duration_min} мин)"
            else:
                end_dt = start_dt
                duration_info = ""
            
            appointment = self.data.add_appointment(client.id, master.id, service_id, start_dt)
            
            # Показываем подробное сообщение о созданной записи
            service_name = self.data.get_service_name(service_id)
            messagebox.showinfo('Успех', 
                              f'Запись создана!\n'
                              f'Время: {time_str} - {end_dt.strftime("%H:%M")}\n'
                              f'Услуга: {service_name}{duration_info}\n'
                              f'Клиент: {client_name}\n'
                              f'Мастер: {master_name}')
            
            self._refresh_schedule_table()
            self.time_info_label.configure(text="")  # Очищаем информацию о времени
            
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def _on_add_schedule(self):
        try:
            master_name = self.schedule_master_cb.get()
            if not master_name:
                raise ValueError('Выберите мастера')
            master = next(m for m in self.data.masters if m.name == master_name)
            date = self.schedule_date.get()
            start = self.s_start.get()
            end = self.s_end.get()
            self.data.add_schedule(master.id, date, start, end)
            messagebox.showinfo('ОК', 'График добавлен')
            self._refresh_schedule_table()
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def _refresh_schedule_table(self):
        """Обновление таблицы с расписанием и записями"""
        self.schedule_text.delete('1.0', 'end')
        
        # Собираем все уникальные даты из расписаний и записей
        all_dates = set()
        for schedule in self.data.schedules:
            all_dates.add(schedule.date)
        for appointment in self.data.appointments:
            appointment_date = appointment.start.split('T')[0]
            all_dates.add(appointment_date)
        
        # Сортируем даты
        sorted_dates = sorted(all_dates, reverse=True)
        
        if not sorted_dates:
            self.schedule_text.insert('end', "Нет данных о расписании и записях\n")
            self.schedule_text.insert('end', "Добавьте график работы мастеров и записи клиентов\n")
            return
        
        for date in sorted_dates:
            # Простое текстовое форматирование без тегов
            self.schedule_text.insert('end', f"\n📅 ДАТА: {date}\n")
            self.schedule_text.insert('end', "=" * 60 + "\n\n")
            
            # Расписание мастеров на эту дату
            daily_schedules = [s for s in self.data.schedules if s.date == date]
            if daily_schedules:
                self.schedule_text.insert('end', "🕐 РАБОЧИЙ ГРАФИК МАСТЕРОВ:\n")
                for schedule in daily_schedules:
                    master_name = self.data.get_master_name(schedule.master_id)
                    self.schedule_text.insert('end', 
                        f"   • {master_name}: {schedule.start_time} - {schedule.end_time}\n")
                self.schedule_text.insert('end', "\n")
            
            # Записи клиентов на эту дату
            daily_appointments = [a for a in self.data.appointments if a.start.startswith(date)]
            if daily_appointments:
                self.schedule_text.insert('end', "📋 ЗАПИСИ КЛИЕНТОВ:\n")
                for appointment in daily_appointments:
                    client_name = self.data.get_client_name(appointment.client_id)
                    master_name = self.data.get_master_name(appointment.master_id)
                    service_name = self.data.get_service_name(appointment.service_id)
                    service_duration = self.data.get_service_duration(appointment.service_id)
                    
                    # Извлекаем время из ISO формата
                    start_time = appointment.start.split('T')[1][:5]
                    end_time = appointment.end.split('T')[1][:5]
                    
                    # Форматируем информацию о продолжительности
                    hours = service_duration // 60
                    minutes = service_duration % 60
                    if hours > 0 and minutes > 0:
                        duration_str = f" ({hours}ч {minutes}мин)"
                    elif hours > 0:
                        duration_str = f" ({hours}ч)"
                    else:
                        duration_str = f" ({minutes}мин)"
                    
                    self.schedule_text.insert('end', 
                        f"   • Время: {start_time}-{end_time}{duration_str}\n")
                    self.schedule_text.insert('end', 
                        f"     Мастер: {master_name}\n")
                    self.schedule_text.insert('end', 
                        f"     Клиент: {client_name}\n")
                    self.schedule_text.insert('end', 
                        f"     Услуга: {service_name}\n\n")
            else:
                self.schedule_text.insert('end', "   На эту дату нет записей клиентов\n\n")
            
            self.schedule_text.insert('end', "\n")