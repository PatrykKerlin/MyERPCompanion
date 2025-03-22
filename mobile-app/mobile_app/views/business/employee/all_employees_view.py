from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivy.clock import mainthread


class AllEmployeesView(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'all_employees'
        self.__data_table = None

        self.__error_label = MDLabel(theme_text_color='Error', halign='center')
        self.add_widget(self.__error_label)

    @mainthread
    def set_data_table(self, labels):
        column_data = [
            (labels.get('id', {}).get('value', ''), dp(30)),
            (labels.get('first_name', {}).get('value', ''), dp(30)),
            (labels.get('middle_name', {}).get('value', ''), dp(30)),
            (labels.get('last_name', {}).get('value', ''), dp(30))
        ]
        if not self.__data_table:
            self.__data_table = MDDataTable(column_data=column_data)
            self.add_widget(self.__data_table)

    @mainthread
    def update_table(self, data):
        row_data = []
        for item in data:
            row_data.append((
                self.sanitize_value(item.get('id')),
                self.sanitize_value(item.get('first_name')),
                self.sanitize_value(item.get('middle_name')),
                self.sanitize_value(item.get('last_name'))
            ))
        self.__data_table.row_data = row_data

    @mainthread
    def display_error(self, message):
        self.__error_label.text = message

    @staticmethod
    def sanitize_value(value):
        return value if value is not None else ''
