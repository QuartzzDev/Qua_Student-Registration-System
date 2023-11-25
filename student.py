import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QInputDialog
import sqlite3
import statistics

class StudentManagementApp(QMainWindow):
    def __init__(self):
        super(StudentManagementApp, self).__init__()

        self.init_ui()

        # SQLite veritabanına bağlan
        self.conn = sqlite3.connect('students.db')
        self.create_tables()

    def init_ui(self):
        # Ana pencere ayarları
        self.setWindowTitle('Öğrenci Kayıt Sistemi')
        self.setGeometry(100, 100, 800, 600)

        # Ana widget ve layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Widget'lar
        self.label_name = QLabel('Öğrenci Adı:', self)
        self.edit_name = QLineEdit(self)

        self.label_grade = QLabel('Notu:', self)
        self.edit_grade = QLineEdit(self)

        self.label_course = QLabel('Ders:', self)
        self.edit_course = QLineEdit(self)

        self.btn_add = QPushButton('Ekle', self)
        self.btn_show_all = QPushButton('Tüm Öğrencileri Görüntüle', self)
        self.btn_update = QPushButton('Bilgileri Güncelle', self)
        self.btn_delete = QPushButton('Sil', self)
        self.btn_stats = QPushButton('İstatistikler', self)
        self.btn_sort = QPushButton('Sırala', self)
        self.btn_multi_grade = QPushButton('Not Değiştir', self)
        self.btn_add_course = QPushButton('Ders Ekle', self)
        self.btn_remove_course = QPushButton('Ders Çıkar', self)

        self.label_search = QLabel('Öğrenci Ara:', self)
        self.edit_search = QLineEdit(self)
        self.btn_search = QPushButton('Ara', self)

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['ID', 'Adı', 'Notu', 'Dersi', 'Durumu'])

        self.combo_filter = QComboBox(self)
        self.combo_filter.addItem('Tümü')
        self.combo_filter.addItems([str(i / 10) for i in range(101)])

        # Layout'a widget'ları ekleme
        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.edit_name)
        self.layout.addWidget(self.label_grade)
        self.layout.addWidget(self.edit_grade)
        self.layout.addWidget(self.label_course)
        self.layout.addWidget(self.edit_course)
        self.layout.addWidget(self.btn_add)
        self.layout.addWidget(self.btn_show_all)

        # Arama bölümü
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.label_search)
        search_layout.addWidget(self.edit_search)
        search_layout.addWidget(self.btn_search)
        self.layout.addLayout(search_layout)

        # Filtreleme bölümü
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.combo_filter)
        self.layout.addLayout(filter_layout)

        # İstatistik ve Sırala butonlarını eklemek
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_stats)
        buttons_layout.addWidget(self.btn_sort)
        buttons_layout.addWidget(self.btn_multi_grade)
        buttons_layout.addWidget(self.btn_update)
        buttons_layout.addWidget(self.btn_delete)
        self.layout.addLayout(buttons_layout)

        # Ders ekleme ve çıkartma butonlarını eklemek
        course_layout = QHBoxLayout()
        course_layout.addWidget(self.btn_add_course)
        course_layout.addWidget(self.btn_remove_course)
        self.layout.addLayout(course_layout)

        # Tabloyu eklemek
        self.layout.addWidget(self.table_widget)

        # Butonlara fonksiyonlar ekleme
        self.btn_add.clicked.connect(self.add_student)
        self.btn_show_all.clicked.connect(self.show_all_students)
        self.btn_search.clicked.connect(self.search_students)
        self.btn_update.clicked.connect(self.update_student)
        self.btn_delete.clicked.connect(self.delete_student)
        self.btn_stats.clicked.connect(self.show_statistics)
        self.btn_sort.clicked.connect(self.sort_students)
        self.btn_multi_grade.clicked.connect(self.add_multi_grade)
        self.btn_add_course.clicked.connect(self.add_course)
        self.btn_remove_course.clicked.connect(self.remove_course)

        # Layout'u ana widget'a ekleme
        self.central_widget.setLayout(self.layout)

    def create_tables(self):
        # Veritabanında "students" ve "courses" tablolarını oluştur
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                grade REAL,
                course_id INTEGER,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        self.conn.commit()

    def add_student(self):
        # Öğrenci eklemek için
        name = self.edit_name.text()
        grade = self.edit_grade.text()
        course_name = self.edit_course.text()

        if name and grade and course_name:
            # Ders var mı kontrol et, yoksa ekleyerek ID'yi al
            course_id = self.get_or_add_course(course_name)

            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO students (name, grade, course_id) VALUES (?, ?, ?)', (name, grade, course_id))
            self.conn.commit()
            self.show_all_students()
            self.edit_name.clear()
            self.edit_grade.clear()
            self.edit_course.clear()
        else:
            QMessageBox.warning(self, 'Hata', 'Lütfen öğrenci adı, notu ve ders adını girin.')

    def get_or_add_course(self, course_name):
        # Ders var mı kontrol et, yoksa ekleyerek ID'yi al
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM courses WHERE name = ?', (course_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            cursor.execute('INSERT INTO courses (name) VALUES (?)', (course_name,))
            self.conn.commit()
            return cursor.lastrowid

    def show_all_students(self):
        # Tüm öğrencileri tabloya ekleme
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT students.id, students.name, students.grade, courses.name AS course_name
            FROM students
            JOIN courses ON students.course_id = courses.id
        ''')
        students = cursor.fetchall()

        self.table_widget.setRowCount(0)

        for row_number, student in enumerate(students):
            self.table_widget.insertRow(row_number)
            for column_number, data in enumerate(student):
                self.table_widget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def search_students(self):
        # Öğrenci aramak için
        keyword = self.edit_search.text()
        filter_grade = self.combo_filter.currentText()

        if filter_grade == 'Tümü':
            query = '''
                SELECT students.id, students.name, students.grade, courses.name AS course_name
                FROM students
                JOIN courses ON students.course_id = courses.id
                WHERE students.name LIKE ?
            '''
            params = ('%' + keyword + '%',)
        else:
            query = '''
                SELECT students.id, students.name, students.grade, courses.name AS course_name
                FROM students
                JOIN courses ON students.course_id = courses.id
                WHERE students.name LIKE ? AND students.grade = ?
            '''
            params = ('%' + keyword + '%', filter_grade)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        students = cursor.fetchall()

        self.table_widget.setRowCount(0)

        for row_number, student in enumerate(students):
            self.table_widget.insertRow(row_number)
            for column_number, data in enumerate(student):
                self.table_widget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def update_student(self):
        # Seçili öğrenciyi güncellemek için
        selected_row = self.table_widget.currentRow()

        if selected_row != -1:
            student_id = self.table_widget.item(selected_row, 0).text()
            new_name, ok = QInputDialog.getText(self, 'Öğrenci Bilgilerini Güncelle', 'Yeni Ad:')
            
            if ok:
                cursor = self.conn.cursor()
                cursor.execute('UPDATE students SET name = ? WHERE id = ?', (new_name, student_id))
                self.conn.commit()
                self.show_all_students()
        else:
            QMessageBox.warning(self, 'Hata', 'Lütfen bir öğrenci seçin.')

    def delete_student(self):
        # Seçili öğrenciyi silmek için
        selected_row = self.table_widget.currentRow()

        if selected_row != -1:
            student_id = self.table_widget.item(selected_row, 0).text()
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
            self.conn.commit()
            self.show_all_students()
        else:
            QMessageBox.warning(self, 'Hata', 'Lütfen bir öğrenci seçin.')

    def show_statistics(self):
        # İstatistikleri göstermek için
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(id), AVG(grade), MIN(grade), MAX(grade) FROM students')
        statistics = cursor.fetchone()

        message = f"Toplam Öğrenci: {statistics[0]}\n"
        message += f"Not Ortalaması: {statistics[1]:.2f}\n"
        message += f"En Düşük Not: {statistics[2]}\n"
        message += f"En Yüksek Not: {statistics[3]}"

        QMessageBox.information(self, 'İstatistikler', message)

    def sort_students(self):
        # Öğrencileri sıralamak için
        sort_type, ok = QInputDialog.getItem(self, 'Sıralama', 'Sıralama Türünü Seç:',
                                            ['Artan', 'Azalan'], 0, False)
        if ok:
            cursor = self.conn.cursor()
            if sort_type == 'Artan':
                cursor.execute('''
                    SELECT students.id, students.name, students.grade, courses.name AS course_name
                    FROM students
                    JOIN courses ON students.course_id = courses.id
                    ORDER BY students.grade ASC
                ''')
            else:
                cursor.execute('''
                    SELECT students.id, students.name, students.grade, courses.name AS course_name
                    FROM students
                    JOIN courses ON students.course_id = courses.id
                    ORDER BY students.grade DESC
                ''')
            
            students = cursor.fetchall()

            self.table_widget.setRowCount(0)

            for row_number, student in enumerate(students):
                self.table_widget.insertRow(row_number)
                for column_number, data in enumerate(student):
                    self.table_widget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def add_multi_grade(self):
        # Çoklu not ekleme işlevselliği
        selected_rows = set([item.row() for item in self.table_widget.selectedItems()])

        if not selected_rows:
            QMessageBox.warning(self, 'Hata', 'Lütfen not eklemek istediğiniz öğrencileri seçin.')
            return

        new_grade, ok = QInputDialog.getText(self, 'Çoklu Not Ekle', 'Yeni Not:')

        if ok:
            for row in selected_rows:
                student_id = self.table_widget.item(row, 0).text()
                cursor = self.conn.cursor()
                cursor.execute('UPDATE students SET grade = ? WHERE id = ?', (new_grade, student_id))
                self.conn.commit()

            self.show_all_students()

    def add_course(self):
        # Ders eklemek için
        course_name, ok = QInputDialog.getText(self, 'Ders Ekle', 'Yeni Ders Adı:')

        if ok:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO courses (name) VALUES (?)', (course_name,))
            self.conn.commit()

    def remove_course(self):
        # Ders çıkartmak için
        course_name, ok = QInputDialog.getText(self, 'Ders Çıkar', 'Çıkarılacak Ders Adı:')

        if ok:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM courses WHERE name = ?', (course_name,))
            self.conn.commit()
            self.show_all_students()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StudentManagementApp()
    ex.show()
    sys.exit(app.exec_())