from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
# from kivy.metrics import dp
from kivymd.uix.label import MDLabel


class AllEmployeesView(MDScreen):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        self.__error_label = MDLabel()
        self.add_widget(self.__error_label)

        self.__data_table = MDDataTable()
        self.add_widget(self.__data_table)

    def set_labels(self, labels):
        column_data = [
            (labels.get('id', {}).get('value', ''), dp(30)),
            (labels.get('first_name', {}).get('value', ''), dp(30)),
            (labels.get('middle_name', {}).get('value', ''), dp(30)),
            (labels.get('last_name', {}).get('value', ''), dp(30))
        ]
        self.__data_table.column_data = column_data

    def update_table(self, data):
        row_data = []
        for item in data.keys():
            row_data.append((item['id'], item['first_name'], item['middle_name'], item['last_name']))
        self.__data_table.row_data = row_data

    def display_error(self, message):
        self.__error_label.text = message
