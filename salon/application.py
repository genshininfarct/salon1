from services.salon_data import SalonData
from gui.admin_gui import AdminGUI


def main():
    data = SalonData()
    app = AdminGUI(data)
    app.mainloop()

if __name__ == '__main__':
    main()