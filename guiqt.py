import sys
import os
import hashlib
import json
import shutil

from datetime        import datetime, timedelta
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QFrame,
    QStackedWidget,
    QAction,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QLabel,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QCalendarWidget,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QTimeEdit,
    QSplitter,
    QToolBar,
    QStatusBar,
    QGroupBox,
    QMenu,
)
from PyQt5.QtCore import Qt, QSize, QTimer, QTime, QDate
from PyQt5.QtGui  import QPalette, QColor
from datamanager  import DataManager


class DarkTheme:

    @staticmethod
    def apply(app):
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)


class CollapsibleSidebar(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setMaximumWidth(300)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        button_style = """
            QPushButton {
            background-color: #404040;
            color: white;
                border: 1px solid #555;
                padding: 1px;
                text-align: left;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """

        self.btn_staff = QPushButton("👥 Работа с персоналом")
        self.btn_docs = QPushButton("📁 Внутренние документы")
        self.btn_todo = QPushButton("✓ TODO лист")
        self.btn_calendar = QPushButton("📅 Календарь")
        self.btn_dashboard = QPushButton("📊 Статистика")

        for btn in [
            self.btn_staff,
            self.btn_docs,
            self.btn_todo,
            self.btn_calendar,
            self.btn_dashboard,
        ]:
            btn.setStyleSheet(button_style)
            btn.setFixedHeight(35)
            self.layout.addWidget(btn)

        self.layout.addStretch()


class StaffPage(QWidget):

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.employees = data_manager.employees
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Добавить")
        self.btn_delete = QPushButton("❌ Удалить")
        self.btn_edit = QPushButton("✏️ Изменить")
        self.btn_change_task = QPushButton("🔄 Сменить задачу")
        self.btn_view_history = QPushButton("📋 История задач")
        self.btn_save = QPushButton("💾 Сохранить")

        for btn in [
            self.btn_add,
            self.btn_delete,
            self.btn_edit,
            self.btn_change_task,
            self.btn_view_history,
            self.btn_save,
        ]:
            btn.setFixedHeight(30)
            btn.setStyleSheet("QPushButton { padding: 1px; }")
            control_layout.addWidget(btn)

        control_layout.addStretch()

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Введите ФИО, должность или задачу...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Личный ID",
                "ФИО",
                "Дата рождения",
                "Должность",
                "Текущая задача",
                "Статус",
                "ID",
            ]
        )
        self.table.hideColumn(6)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.btn_add.clicked.connect(self.add_employee)
        self.btn_delete.clicked.connect(self.delete_employee)
        self.btn_edit.clicked.connect(self.edit_employee)
        self.btn_change_task.clicked.connect(self.change_task)
        self.btn_view_history.clicked.connect(self.view_task_history)
        self.btn_save.clicked.connect(self.save_data)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addLayout(control_layout)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.update_table()

    def generate_id(self, full_name, birth_date, position):
        data = f"{full_name}{birth_date}{position}{datetime.now()}"
        return hashlib.md5(data.encode()).hexdigest()[:8]

    def add_employee(self):
        dialog = EmployeeDialog(self, self.data_manager.employees)
        if dialog.exec_():
            full_name, birth_date, position, current_task = dialog.get_data()
            emp_id = self.generate_id(full_name, birth_date, position)

            employee_data = {
                "id": emp_id,
                "full_name": full_name,
                "birth_date": birth_date,
                "position": position,
                "current_task": current_task,
                "task_history": [],
                "status": "Активен",
            }

            self.employees.append(employee_data)
            self.update_table()

    def delete_employee(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            emp_id = self.table.item(current_row, 6).text()
            employee = self.data_manager.get_employee_by_id(emp_id)

            if employee:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    f'Вы уверены, что хотите удалить сотрудника {employee["full_name"]}?',
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    self.employees.remove(employee)
                    self.update_table()

    def edit_employee(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            emp_id = self.table.item(current_row, 6).text()
            employee = self.data_manager.get_employee_by_id(emp_id)

            if employee:
                dialog = EmployeeDialog(
                    self, self.data_manager.employees, employee)
                if dialog.exec_():
                    full_name, birth_date, position, current_task = dialog.get_data()
                    employee.update(
                        {
                            "full_name": full_name,
                            "birth_date": birth_date,
                            "position": position,
                            "current_task": current_task,
                        }
                    )
                    self.update_table()

    def change_task(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            emp_id = self.table.item(current_row, 6).text()
            employee = self.data_manager.get_employee_by_id(emp_id)

            if employee:
                old_task = employee["current_task"]
                new_task, ok = QInputDialog.getText(
                    self, "Смена задачи", "Введите новую задачу:", text=old_task)
                if ok and new_task:
                    if old_task and old_task != new_task:
                        employee["task_history"].append(
                            {
                                "task": old_task,
                                "start_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "end_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "type": "смена",
                            }
                        )

                    employee["current_task"] = new_task
                    self.update_table()

    def view_task_history(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            emp_id = self.table.item(current_row, 6).text()
            employee = self.data_manager.get_employee_by_id(emp_id)

            if employee:
                dialog = TaskHistoryDialog(self, employee)
                dialog.exec_()

    def filter_table(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in [1, 3, 4]:  # ФИО, Должность, Задача
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def update_table(self):
        self.table.setRowCount(len(self.employees))
        for row, employee in enumerate(self.employees):
            self.table.setItem(row, 0, QTableWidgetItem(employee["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(employee["full_name"]))
            self.table.setItem(
                row, 2, QTableWidgetItem(employee["birth_date"]))
            self.table.setItem(row, 3, QTableWidgetItem(employee["position"]))
            self.table.setItem(row, 4, QTableWidgetItem(
                employee["current_task"]))
            self.table.setItem(
                row, 5, QTableWidgetItem(employee.get("status", "Активен")))
            self.table.setItem(row, 6, QTableWidgetItem(employee["id"]))

    def save_data(self):
        try:
            self.data_manager.save_all_data()
            QMessageBox.information(self, "Успех", "Данные сохранены!")
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def show_context_menu(self, position):
        menu = QMenu()

        edit_action = menu.addAction("✏️ Редактировать")
        delete_action = menu.addAction("❌ Удалить")
        change_task_action = menu.addAction("🔄 Сменить задачу")
        history_action = menu.addAction("📋 История задач")

        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        if action == edit_action:
            self.edit_employee()
        elif action == delete_action:
            self.delete_employee()
        elif action == change_task_action:
            self.change_task()
        elif action == history_action:
            self.view_task_history()


class EmployeeDialog(QDialog):

    def __init__(self, parent=None, employees=None, employee=None):
        super().__init__(parent)
        self.employee = employee
        self.employees = employees or []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить/Изменить сотрудника")
        self.setFixedSize(450, 350)

        layout = QFormLayout()

        self.full_name = QLineEdit()
        self.birth_date = QLineEdit()
        self.birth_date.setPlaceholderText("ГГГГ-ММ-ДД")
        self.position = QLineEdit()
        self.current_task = QLineEdit()

        positions = list(
            set(emp["position"]
                for emp in self.employees if emp.get("position"))
        )
        self.position_completer = QComboBox()
        self.position_completer.setEditable(True)
        self.position_completer.addItems(positions)

        if self.employee:
            self.full_name.setText(self.employee["full_name"])
            self.birth_date.setText(self.employee["birth_date"])
            self.position_completer.setCurrentText(self.employee["position"])
            self.current_task.setText(self.employee["current_task"])

        layout.addRow("ФИО:*", self.full_name)
        layout.addRow("Дата рождения:*", self.birth_date)
        layout.addRow("Должность:*", self.position_completer)
        layout.addRow("Текущая задача:", self.current_task)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.full_name.text().strip():
            QMessageBox.warning(
                self, "Ошибка", "Поле ФИО обязательно для заполнения!")
            return
        if not self.birth_date.text().strip():
            QMessageBox.warning(
                self,
                "Ошибка",
                "Поле Дата рождения обязательно для заполнения!")
            return
        if not self.position_completer.currentText().strip():
            QMessageBox.warning(
                self, "Ошибка", "Поле Должность обязательно для заполнения!"
            )
            return

        self.accept()

    def get_data(self):
        return (
            self.full_name.text().strip(),
            self.birth_date.text().strip(),
            self.position_completer.currentText().strip(),
            self.current_task.text().strip(),
        )


class TaskHistoryDialog(QDialog):

    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.employee = employee
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"История задач - {self.employee['full_name']}")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Задача", "Дата начала", "Дата окончания", "Тип"]
        )

        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        history = self.employee.get("task_history", [])
        self.history_table.setRowCount(len(history))

        for row, task in enumerate(history):
            self.history_table.setItem(
                row, 0, QTableWidgetItem(task.get("task", "")))
            self.history_table.setItem(
                row, 1, QTableWidgetItem(task.get("start_date", ""))
            )
            self.history_table.setItem(
                row, 2, QTableWidgetItem(task.get("end_date", ""))
            )
            self.history_table.setItem(
                row, 3, QTableWidgetItem(task.get("type", "смена"))
            )

        layout.addWidget(
            QLabel(f"История задач сотрудника: {self.employee['full_name']}")
        )
        layout.addWidget(self.history_table)

        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
        self.setLayout(layout)


class DocumentsPage(QWidget):
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.documents = data_manager.documents
        self.documents_folder = "documents"
        os.makedirs(self.documents_folder, exist_ok=True)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.doc_list = QListWidget()
        self.doc_list.currentItemChanged.connect(self.show_document)
        self.doc_list.itemDoubleClicked.connect(self.open_file_external)

        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)

        self.file_info = QLabel("Выберите файл для просмотра")
        self.file_info.setStyleSheet(
            "padding: 1px; background-color: #404040; border-radius: 3px;")

        btn_layout = QVBoxLayout()
        self.btn_add = QPushButton("📎 Добавить файл")
        self.btn_add_folder = QPushButton("📁 Добавить папку")
        self.btn_delete = QPushButton("🗑️ Удалить файл")
        self.btn_open_external = QPushButton("🔍 Открыть внешне")
        self.btn_save = QPushButton("💾 Сохранить изменения")
        self.btn_refresh = QPushButton("🔄 Обновить список")

        for btn in [
            self.btn_add,
            self.btn_add_folder,
            self.btn_delete,
            self.btn_open_external,
            self.btn_save,
            self.btn_refresh,
        ]:
            btn.setFixedHeight(30)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()

        self.btn_add.clicked.connect(self.add_document)
        self.btn_add_folder.clicked.connect(self.add_folder)
        self.btn_delete.clicked.connect(self.delete_document)
        self.btn_open_external.clicked.connect(self.open_file_external)
        self.btn_save.clicked.connect(self.save_document)
        self.btn_refresh.clicked.connect(self.refresh_list)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.doc_list)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.file_info)
        right_layout.addWidget(self.viewer)
        right_layout.addLayout(btn_layout)
        right_widget.setLayout(right_layout)

        splitter.addWidget(right_widget)
        splitter.setSizes([250, 550])

        layout.addWidget(splitter)
        self.setLayout(layout)

        self.refresh_list()

    def refresh_list(self):
        self.doc_list.clear()
        for doc in self.documents:
            item = QListWidgetItem(doc["name"])
            item.setData(Qt.UserRole, doc)
            self.doc_list.addItem(item)

    def add_document(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы",
            "",
            "Файлы (*);;Текстовые ;;Документы ;;Изображения ",
        )
        if file_paths:
            for file_path in file_paths:
                self.import_file(file_path)

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder_path:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.import_file(file_path)

    def import_file(self, file_path):
        try:
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1].lower()

            if any(doc["name"] == filename for doc in self.documents):
                reply = QMessageBox.question(
                    self,
                    "Файл существует",
                    f"Файл {filename} уже существует. Заменить?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

            dest_path = os.path.join(self.documents_folder, filename)
            shutil.copy2(file_path, dest_path)

            doc_data = {
                "name": filename,
                "path": dest_path,
                "size": os.path.getsize(dest_path),
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": file_ext,
            }

            existing_index = next(
                (i for i, doc in enumerate(self.documents)
                 if doc["name"] == filename),
                -1,
            )
            if existing_index >= 0:
                self.documents[existing_index] = doc_data
            else:
                self.documents.append(doc_data)

            self.refresh_list()
            self.data_manager.save_all_data()

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось добавить файл: {str(e)}")

    def delete_document(self):
        current_item = self.doc_list.currentItem()
        if current_item:
            doc_data = current_item.data(Qt.UserRole)
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f'Вы уверены, что хотите удалить файл {doc_data["name"]}?',
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    if os.path.exists(doc_data["path"]):
                        os.remove(doc_data["path"])

                    self.documents = [
                        doc for doc in self.documents if doc["name"] != doc_data["name"]]
                    self.data_manager.documents = self.documents
                    self.data_manager.save_all_data()

                    self.refresh_list()
                    self.viewer.clear()
                    self.file_info.setText("Выберите файл для просмотра")

                except Exception as e:
                    QMessageBox.critical(
                        self, "Ошибка", f"Не удалось удалить файл: {str(e)}"
                    )

    def save_document(self):
        current_item = self.doc_list.currentItem()
        if current_item:
            doc_data = current_item.data(Qt.UserRole)
            try:
                if doc_data["type"] in [".txt", ".log", ".csv"]:
                    with open(doc_data["path"], "w", encoding="utf-8") as f:
                        f.write(self.viewer.toPlainText())

                    doc_data["modified"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M")
                    doc_data["size"] = os.path.getsize(doc_data["path"])

                    self.data_manager.save_all_data()
                    QMessageBox.information(
                        self, "Успех", "Изменения сохранены!")
                else:
                    QMessageBox.warning(
                        self,
                        "Предупреждение",
                        "Редактирование возможно только для текстовых файлов",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось сохранить файл: {str(e)}"
                )

    def show_document(self, current, previous):
        if current:
            doc_data = current.data(Qt.UserRole)
            self.file_info.setText(
                f"Файл: {doc_data['name']} | Размер: {doc_data['size']} байт | Изменен: {doc_data['modified']}")

            try:
                if doc_data["type"] in [
                    ".txt",
                    ".log",
                    ".csv",
                    ".json",
                    ".xml",
                    ".html",
                ]:
                    with open(doc_data["path"], "r", encoding="utf-8") as f:
                        content = f.read()
                    self.viewer.setPlainText(content)
                    self.viewer.setReadOnly(False)
                else:
                    self.viewer.setPlainText(
                        f"Файл {doc_data['name']} не может быть отображен в текстовом редакторе.\n\nИспользуйте кнопку 'Открыть внешне' для просмотра."
                    )
                    self.viewer.setReadOnly(True)
            except Exception as e:
                self.viewer.setPlainText(f"Ошибка чтения файла: {str(e)}")
                self.viewer.setReadOnly(True)

    def open_file_external(self):
        current_item = self.doc_list.currentItem()
        if current_item:
            doc_data = current_item.data(Qt.UserRole)
            try:
                if sys.platform == "win32":
                    os.startfile(doc_data["path"])
                elif sys.platform == "darwin":
                    os.system(f"open '{doc_data['path']}'")
                else:
                    os.system(f"xdg-open '{doc_data['path']}'")
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось открыть файл: {str(e)}"
                )


class TodoPage(QWidget):

    def __init__(self, data_manager):
        
        super().__init__()
        self.data_manager = data_manager
        self.tasks = data_manager.tasks
        self.init_ui()

    def init_ui(self):
        
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите новую задачу...")

        self.assignee_combo = QComboBox()
        self.update_assignee_combo()

        self.progress_combo = QComboBox()
        self.progress_combo.addItems(
            ["К выполнению", "В процессе", "Завершено"])

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(
            ["Низкий", "Средний", "Высокий", "Критичный"])

        self.btn_add_task = QPushButton("➕ Добавить задачу")

        form_layout.addWidget(QLabel("Задача:"))
        form_layout.addWidget(self.task_input)
        form_layout.addWidget(QLabel("Исполнитель:"))
        form_layout.addWidget(self.assignee_combo)
        form_layout.addWidget(QLabel("Статус:"))
        form_layout.addWidget(self.progress_combo)
        form_layout.addWidget(QLabel("Приоритет:"))
        form_layout.addWidget(self.priority_combo)
        form_layout.addWidget(self.btn_add_task)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.filter_status = QComboBox()
        self.filter_status.addItems(
            ["Все статусы", "К выполнению", "В процессе", "Завершено"]
        )
        self.filter_assignee = QComboBox()
        self.filter_assignee.addItems(
            ["Все исполнители"]
            + [emp["full_name"] for emp in self.data_manager.employees]
        )
        self.filter_priority = QComboBox()
        self.filter_priority.addItems(
            ["Все приоритеты", "Низкий", "Средний", "Высокий", "Критичный"]
        )

        self.filter_status.currentTextChanged.connect(self.filter_tasks)
        self.filter_assignee.currentTextChanged.connect(self.filter_tasks)
        self.filter_priority.currentTextChanged.connect(self.filter_tasks)

        filter_layout.addWidget(self.filter_status)
        filter_layout.addWidget(self.filter_assignee)
        filter_layout.addWidget(self.filter_priority)
        filter_layout.addStretch()

        self.todo_list = QListWidget()
        self.todo_list.itemDoubleClicked.connect(self.edit_task)

        self.btn_add_task.clicked.connect(self.add_task)

        layout.addLayout(form_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.todo_list)

        self.setLayout(layout)
        self.update_list()

    def update_assignee_combo(self):
        
        self.assignee_combo.clear()
        self.assignee_combo.addItems(
            [emp["full_name"] for emp in self.data_manager.employees]
        )

    def add_task(self):
        
        task_text = self.task_input.text().strip()
        assignee_name = self.assignee_combo.currentText()
        status = self.progress_combo.currentText()
        priority = self.priority_combo.currentText()

        if task_text and assignee_name:
            assignee = next(
                (
                    emp
                    for emp in self.data_manager.employees
                    if emp["full_name"] == assignee_name
                ),
                None,
            )

            if assignee:
                task = {
                    "id": len(self.tasks) + 1,
                    "text": task_text,
                    "assignee_id": assignee["id"],
                    "assignee_name": assignee_name,
                    "status": status,
                    "priority": priority,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "deadline": None,
                }
                self.tasks.append(task)
                self.update_list()

                assignee["current_task"] = task_text

                self.task_input.clear()
                self.data_manager.save_all_data()

    def edit_task(self, item):
        task_id = item.data(Qt.UserRole)
        task = next((t for t in self.tasks if t["id"] == task_id), None)

        if task:
            dialog = TodoTaskDialog(self, self.data_manager.employees, task)
            if dialog.exec_():
                updated_task = dialog.get_data()
                task.update(updated_task)
                self.update_list()
                self.data_manager.save_all_data()

    def update_list(self):
        self.todo_list.clear()
        for task in self.tasks:
            item_text = f"{task['text']} | 👤{task['assignee_name']} | 📊{task['status']} | ⚡{task['priority']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, task["id"])

            if task["status"] == "Завершено":
                item.setBackground(QColor(50, 150, 50))
            elif task["status"] == "В процессе":
                if task["priority"] == "Критичный":
                    item.setBackground(QColor(200, 50, 50))
                elif task["priority"] == "Высокий":
                    item.setBackground(QColor(220, 120, 50))
                else:
                    item.setBackground(QColor(150, 150, 50))
            else:
                if task["priority"] == "Критичный":
                    item.setBackground(QColor(150, 50, 50))
                elif task["priority"] == "Высокий":
                    item.setBackground(QColor(180, 100, 50))
                else:
                    item.setBackground(QColor(80, 80, 80))

            self.todo_list.addItem(item)

    def filter_tasks(self):
        status_filter = self.filter_status.currentText()
        assignee_filter = self.filter_assignee.currentText()
        priority_filter = self.filter_priority.currentText()

        for i in range(self.todo_list.count()):
            item = self.todo_list.item(i)
            task_id = item.data(Qt.UserRole)
            task = next((t for t in self.tasks if t["id"] == task_id), None)

            if task:
                show = True
                if (status_filter != "Все статусы") and (
                    task["status"] != status_filter
                ):
                    show = False
                if (assignee_filter != "Все исполнители") and (
                    task["assignee_name"] != assignee_filter
                ):
                    show = False
                if (priority_filter != "Все приоритеты") and (
                    task["priority"] != priority_filter
                ):
                    show = False
                item.setHidden(not show)


class TodoTaskDialog(QDialog):

    def __init__(self, parent=None, employees=None, task=None):
        super().__init__(parent)
        self.task = task
        self.employees = employees or []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Редактировать задачу")
        self.setFixedSize(500, 300)

        layout = QFormLayout()

        self.task_edit = QTextEdit()
        self.task_edit.setMaximumHeight(80)

        self.assignee_combo = QComboBox()
        self.assignee_combo.addItems(
            [emp["full_name"] for emp in self.employees])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["К выполнению", "В процессе", "Завершено"])

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(
            ["Низкий", "Средний", "Высокий", "Критичный"])

        self.deadline_edit = QLineEdit()
        self.deadline_edit.setPlaceholderText("ГГГГ-ММ-ДД ЧЧ:ММ")

        if self.task:
            self.task_edit.setText(self.task["text"])
            self.assignee_combo.setCurrentText(self.task["assignee_name"])
            self.status_combo.setCurrentText(self.task["status"])
            self.priority_combo.setCurrentText(self.task["priority"])
            if self.task.get("deadline"):
                self.deadline_edit.setText(self.task["deadline"])

        layout.addRow("Задача:", self.task_edit)
        layout.addRow("Исполнитель:", self.assignee_combo)
        layout.addRow("Статус:", self.status_combo)
        layout.addRow("Приоритет:", self.priority_combo)
        layout.addRow("Дедлайн:", self.deadline_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        self.setLayout(layout)

    def get_data(self):
        assignee = next(
            (
                emp
                for emp in self.employees
                if emp["full_name"] == self.assignee_combo.currentText()
            ),
            None,
        )

        return {
            "text": self.task_edit.toPlainText(),
            "assignee_id": assignee["id"] if assignee else self.task["assignee_id"],
            "assignee_name": self.assignee_combo.currentText(),
            "status": self.status_combo.currentText(),
            "priority": self.priority_combo.currentText(),
            "deadline": self.deadline_edit.text() or None,
        }


class CalendarPage(QWidget):

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.events = data_manager.events
        self.notified_events = set()
        self.init_ui()

        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_notifications)
        self.notification_timer.start(30000)

    def init_ui(self):
        layout = QVBoxLayout()

        calendar_layout = QHBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.show_events)

        side_panel = QVBoxLayout()

        today_btn = QPushButton("📅 Сегодня")
        today_btn.clicked.connect(self.go_to_today)

        self.month_view = QListWidget()
        self.update_month_view()

        side_panel.addWidget(today_btn)
        side_panel.addWidget(QLabel("События месяца:"))
        side_panel.addWidget(self.month_view)

        calendar_layout.addWidget(self.calendar)
        calendar_layout.addLayout(side_panel)

        self.events_list = QListWidget()
        self.events_list.itemDoubleClicked.connect(self.edit_event)

        btn_layout = QHBoxLayout()
        self.btn_add_event = QPushButton("➕ Добавить событие")
        self.btn_delete_event = QPushButton("❌ Удалить событие")
        self.btn_export = QPushButton("📤 Экспорт событий")

        for btn in [
                self.btn_add_event,
                self.btn_delete_event,
                self.btn_export]:
            btn.setFixedHeight(30)
            btn_layout.addWidget(btn)

        self.btn_add_event.clicked.connect(self.add_event)
        self.btn_delete_event.clicked.connect(self.delete_event)
        self.btn_export.clicked.connect(self.export_events)

        layout.addLayout(calendar_layout)
        layout.addWidget(QLabel("События на выбранную дату:"))
        layout.addWidget(self.events_list)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.show_events()

    def go_to_today(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.show_events()

    def update_month_view(self):
        self.month_view.clear()
        current_date = QDate.currentDate()
        current_month = current_date.toString("yyyy-MM")

        month_events = []
        for date_str, events in self.events.items():
            if date_str.startswith(current_month):
                for event in events:
                    month_events.append(f"{date_str}: {event['title']}")

        for event_str in sorted(month_events)[:10]:
            self.month_view.addItem(event_str)

    def add_event(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        dialog = EventDialog(
            self, self.data_manager.employees, self.data_manager.tasks)
        if dialog.exec_():
            event_data = dialog.get_data()

            event = {
                "id": len(self.events.get(selected_date, [])) + 1,
                "title": event_data["title"],
                "description": event_data["description"],
                "task_id": event_data["task_id"],
                "task_name": event_data["task_name"],
                "assignee_id": event_data["assignee_id"],
                "assignee_name": event_data["assignee_name"],
                "time": event_data["time"],
                "datetime": f"{selected_date} {event_data['time']}",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

            if selected_date not in self.events:
                self.events[selected_date] = []

            self.events[selected_date].append(event)
            self.show_events()
            self.update_month_view()
            self.data_manager.save_all_data()

    def delete_event(self):
        current_row = self.events_list.currentRow()
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        if current_row >= 0 and selected_date in self.events:
            if current_row < len(self.events[selected_date]):
                event = self.events[selected_date][current_row]
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    f'Удалить событие "{event["title"]}"?',
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    self.events[selected_date].pop(current_row)
                    self.show_events()
                    self.update_month_view()
                    self.data_manager.save_all_data()

    def edit_event(self, item):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        row = self.events_list.row(item)

        if selected_date in self.events and row < len(
                self.events[selected_date]):
            event = self.events[selected_date][row]
            dialog = EventDialog(
                self,
                self.data_manager.employees,
                self.data_manager.tasks,
                event)

            if dialog.exec_():
                event_data = dialog.get_data()
                event.update(
                    {
                        "title": event_data["title"],
                        "description": event_data["description"],
                        "task_id": event_data["task_id"],
                        "task_name": event_data["task_name"],
                        "assignee_id": event_data["assignee_id"],
                        "assignee_name": event_data["assignee_name"],
                        "time": event_data["time"],
                        "datetime": f"{selected_date} {event_data['time']}",
                    }
                )
                self.show_events()
                self.update_month_view()
                self.data_manager.save_all_data()

    def show_events(self):
        self.events_list.clear()
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        if selected_date in self.events:
            sorted_events = sorted(
                self.events[selected_date], key=lambda x: x["time"])

            for event in sorted_events:
                item_text = f"🕒 {event['time']} | {event['title']} | 👤{event['assignee_name']}"
                if event.get("task_name"):
                    item_text += f" | 📋{event['task_name']}"

                item = QListWidgetItem(item_text)
                item.setToolTip(
                    f"Описание: {event['description']}\nЗадача: {event.get('task_name', 'Не указана')}\nИсполнитель: {event['assignee_name']}"
                )
                self.events_list.addItem(item)

    def check_notifications(self):
        now = datetime.now()

        for date_str, events in self.events.items():
            for event in events:
                event_id = f"{date_str}_{event['time']}_{event['title']}"

                if event_id in self.notified_events:
                    continue

                try:
                    event_datetime = datetime.strptime(
                        event["datetime"], "%Y-%m-%d %H:%M"
                    )
                    time_diff = event_datetime - now

                    if timedelta(0) <= time_diff <= timedelta(minutes=10):
                        self.show_notification(event)
                        self.notified_events.add(event_id)

                except ValueError:
                    continue

    def show_notification(self, event):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("🔔 Напоминание о событии")
        msg.setText(f"Событие: {event['title']}")
        msg.setInformativeText(
            f"Время: {event['time']}\nИсполнитель: {event['assignee_name']}\nОписание: {event['description']}"
        )
        msg.addButton("ОК", QMessageBox.AcceptRole)
        msg.addButton("Отложить (5 мин)", QMessageBox.RejectRole)

        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)

        result = msg.exec_()

        if result == QMessageBox.RejectRole:
            self.notified_events.remove(
                f"{event['datetime'].split(' ')[0]}_{event['time']}_{event['title']}"
            )

    def export_events(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт событий", "events_export.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.events, f, ensure_ascii=False, indent=2)
                QMessageBox.information(
                    self, "Успех", "События экспортированы!")
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось экспортировать события: {str(e)}")


class EventDialog(QDialog):
    
    def __init__(self, parent=None, employees=None, tasks=None, event=None):
        super().__init__(parent)
        self.event = event
        self.employees = employees or []
        self.tasks = tasks or []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить/Изменить событие")
        self.setFixedSize(500, 400)

        layout = QFormLayout()

        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)

        self.task_combo = QComboBox()
        self.task_combo.addItem("Не указана", None)
        for task in self.tasks:
            self.task_combo.addItem(
                f"{task['text']} ({task['assignee_name']})", task["id"]
            )

        self.assignee_combo = QComboBox()
        self.assignee_combo.addItems(
            [emp["full_name"] for emp in self.employees])

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setDisplayFormat("HH:mm")

        if self.event:
            self.title_input.setText(self.event["title"])
            self.description_input.setText(self.event["description"])

            if self.event.get("task_id"):
                index = self.task_combo.findData(self.event["task_id"])
                if index >= 0:
                    self.task_combo.setCurrentIndex(index)

            assignee_index = self.assignee_combo.findText(
                self.event.get("assignee_name", "")
            )
            if assignee_index >= 0:
                self.assignee_combo.setCurrentIndex(assignee_index)

            time = QTime.fromString(self.event["time"], "HH:mm")
            self.time_input.setTime(time)

        layout.addRow("Название:*", self.title_input)
        layout.addRow("Описание:", self.description_input)
        layout.addRow("Связанная задача:", self.task_combo)
        layout.addRow("Исполнитель:*", self.assignee_combo)
        layout.addRow("Время:*", self.time_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self, "Ошибка", "Поле Название обязательно для заполнения!"
            )
            return
        if not self.assignee_combo.currentText():
            QMessageBox.warning(
                self, "Ошибка", "Поле Исполнитель обязательно для заполнения!"
            )
            return

        self.accept()

    def get_data(self):
        assignee = next(
            (
                emp
                for emp in self.employees
                if emp["full_name"] == self.assignee_combo.currentText()
            ),
            None,
        )
        task_id = self.task_combo.currentData()
        task = next((t for t in self.tasks if t["id"] == task_id), None)

        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "task_id": task_id,
            "task_name": task["text"] if task else None,
            "assignee_id": assignee["id"] if assignee else None,
            "assignee_name": self.assignee_combo.currentText(),
            "time": self.time_input.time().toString("HH:mm"),
        }


class DashboardPage(QWidget):
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📊 Статистика и аналитика")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 1px;")
        layout.addWidget(title)

        stats_layout = QHBoxLayout()

        employees_card = self.create_stat_card(
            "👥 Сотрудники",
            f"Всего: {len(self.data_manager.employees)}\n"
            f"Активных: {len([e for e in self.data_manager.employees if e.get('status') == 'Активен'])}",
            "#2a82da",
        )

        tasks_card = self.create_stat_card(
            "✓ Задачи",
            f"Всего: {len(self.data_manager.tasks)}\n"
            f"Завершено: {len([t for t in self.data_manager.tasks if t['status'] == 'Завершено'])}",
            "#27ae60",
        )

        events_card = self.create_stat_card(
            "📅 События",
            f"Запланировано: {sum(len(events) for events in self.data_manager.events.values())}\n"
            f"Сегодня: {len(self.data_manager.events.get(datetime.now().strftime('%Y-%m-%d'), []))}",
            "#e74c3c",
        )

        docs_card = self.create_stat_card(
            "📁 Документы",
            f"Всего: {len(self.data_manager.documents)}\n"
            f"Размер: {sum(doc.get('size', 0) for doc in self.data_manager.documents) // 1024} КБ",
            "#f39c12",
        )

        stats_layout.addWidget(employees_card)
        stats_layout.addWidget(tasks_card)
        stats_layout.addWidget(events_card)
        stats_layout.addWidget(docs_card)

        layout.addLayout(stats_layout)

        detail_layout = QHBoxLayout()

        status_widget = self.create_task_status_chart()
        detail_layout.addWidget(status_widget)

        events_widget = self.create_upcoming_events()
        detail_layout.addWidget(events_widget)

        layout.addLayout(detail_layout)
        self.setLayout(layout)

    def create_stat_card(self, title, text, color):
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 0px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
            }}
        """
        )
        card.setFixedSize(180, 80)

        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px;")
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 12px;")

        layout.addWidget(title_label)
        layout.addWidget(text_label)
        card.setLayout(layout)

        return card

    def create_task_status_chart(self):
        group = QGroupBox("📈 Статусы задач")
        layout = QVBoxLayout()

        statuses = {}
        for task in self.data_manager.tasks:
            status = task["status"]
            statuses[status] = statuses.get(status, 0) + 1

        for status, count in statuses.items():
            percent = (
                (count / len(self.data_manager.tasks)) * 100
                if self.data_manager.tasks
                else 0
            )
            row = QHBoxLayout()
            row.addWidget(QLabel(status))
            row.addWidget(QLabel(f"{count} ({percent:.1f}%)"))
            layout.addLayout(row)

        group.setLayout(layout)
        return group

    def create_upcoming_events(self):
        group = QGroupBox("🕐 Ближайшие события")
        layout = QVBoxLayout()

        today = datetime.now().date()
        upcoming = []

        for date_str, events in self.data_manager.events.items():
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if event_date >= today:
                    for event in events:
                        upcoming.append((date_str, event))
            except ValueError:
                continue

        upcoming.sort(key=lambda x: x[0])

        for date_str, event in upcoming[:5]:
            event_text = f"{date_str} {event['time']}: {event['title']}"
            layout.addWidget(QLabel(event_text))

        if not upcoming:
            layout.addWidget(QLabel("Нет предстоящих событий"))

        group.setLayout(layout)
        return group


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.setWindowTitle("Система управления персоналом v2.0")
        self.resize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = CollapsibleSidebar()
        main_layout.addWidget(self.sidebar)

        self.stacked_work_area = QStackedWidget()
        main_layout.addWidget(self.stacked_work_area)

        self.staff_page = StaffPage(self.data_manager)
        self.docs_page = DocumentsPage(self.data_manager)
        self.todo_page = TodoPage(self.data_manager)
        self.calendar_page = CalendarPage(self.data_manager)
        self.dashboard_page = DashboardPage(self.data_manager)

        self.stacked_work_area.addWidget(self.dashboard_page)
        self.stacked_work_area.addWidget(self.staff_page)
        self.stacked_work_area.addWidget(self.docs_page)
        self.stacked_work_area.addWidget(self.todo_page)
        self.stacked_work_area.addWidget(self.calendar_page)

        self.sidebar.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.sidebar.btn_staff.clicked.connect(lambda: self.switch_page(1))
        self.sidebar.btn_docs.clicked.connect(lambda: self.switch_page(2))
        self.sidebar.btn_todo.clicked.connect(lambda: self.switch_page(3))
        self.sidebar.btn_calendar.clicked.connect(lambda: self.switch_page(4))

        self.create_menu_bar()
        self.create_status_bar()
        self.create_tool_bar()

        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.auto_save)
        self.autosave_timer.start(300000)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Файл")

        exit_action = QAction("🚪 Выход", self)
        exit_action.triggered.connect(self.close)

        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("&Вид")
        toggle_sidebar_action = QAction(
            "📋 Свернуть/развернуть боковую панель", self)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        help_menu = menu_bar.addMenu("&Помощь")
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        toolbar = QToolBar("Основные инструменты")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        toolbar.addAction("💾 Сохранить все", self.data_manager.save_all_data)
        toolbar.addAction("🔄 Обновить", self.refresh_all)
        toolbar.addSeparator()
        toolbar.addAction("👥 Сотрудники", lambda: self.switch_page(1))
        toolbar.addAction("✓ Задачи", lambda: self.switch_page(3))
        toolbar.addAction("📅 Календарь", lambda: self.switch_page(4))

    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.showMessage("Готово к работе")
        self.setStatusBar(status_bar)

        self.save_indicator = QLabel("💾 Автосохранение включено")
        status_bar.addPermanentWidget(self.save_indicator)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def switch_page(self, index):
        self.stacked_work_area.setCurrentIndex(index)

        pages = [
            "Статистика",
            "Управление персоналом",
            "Внутренние документы",
            "TODO лист",
            "Календарь",
        ]
        self.statusBar().showMessage(f"Режим: {pages[index]}")

        if index == 0:
            self.dashboard_page.update()
        elif index == 3:
            self.todo_page.update_assignee_combo()
            self.todo_page.update_list()

    def refresh_all(self):
        self.data_manager.load_all_data()
        self.staff_page.update_table()
        self.todo_page.update_list()
        self.calendar_page.show_events()
        self.docs_page.refresh_list()
        self.statusBar().showMessage("Все данные обновлены")

    def auto_save(self):
        try:
            self.data_manager.save_all_data()
            self.statusBar().showMessage("Данные автоматически сохранены", 2000)
        except Exception as e:
            print(f"Ошибка автосохранения: {e}")

    def show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "Система управления персоналом v2.0\n\n"
            "Полностью интегрированная система для управления:\n"
            "• Сотрудниками и их задачами\n"
            "• Внутренними документами\n"
            "• Календарем событий\n"
            "• TODO листами",
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Сохранить данные перед выходом?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )

        if reply == QMessageBox.Yes:
            self.data_manager.save_all_data()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()