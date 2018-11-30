from database import * # pylint: disable=W0614
from wordCloud import * # pylint: disable=W0614
import os, sys
from PyQt5.QtGui import QIcon # pylint: disable=E0611
from PyQt5.QtCore import pyqtSlot # pylint: disable=E0611
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout # pylint: disable=E0611
from PyQt5.QtWidgets import QPushButton, QMainWindow, QLineEdit, QLabel # pylint: disable=E0611
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView # pylint: disable=E0611
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

path = os.path.dirname(os.path.abspath(__file__))
wiki_path = os.path.join(path, 'Wikipages')
test_path = os.path.join(path, 'TestOpgaver')


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.left = 800
        self.top = 500
        self.width = 400
        self.height = 600
        self.title = 'Plagiarism detection'
        self.icon = QIcon(os.path.join(path, 'A.png'))
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(self.icon)

        self.layout = QVBoxLayout()

        label = QLabel('Input article:')
        self.layout.addWidget(label)
        
        self.textbox = QLineEdit(self)
        f = self.textbox.font()
        f.setPointSize(10)
        self.textbox.setFont(f)
        self.layout.addWidget(self.textbox)

        button = QPushButton('Run', self)
        button.setToolTip('Detect if the article contains plagiarism')
        button.clicked.connect(self.on_click)
        self.layout.addWidget(button)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        # self.table.setRowCount(2)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setVisible(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        db = Database()

        file = self.textbox.text() + '.txt'
        test_file = os.path.join(test_path, file)
        test_fp = Fingerprint(test_file)
        test_sig = test_fp.getSignatures()
        test_substring = test_fp.getSubstring()
        db_sigs = db.get_all_signatures()

        idx = 0
        self.table.setColumnCount(2)
        for name, sig in db_sigs.items():
            sim = jaccard(test_sig, sig)
            if sim >= 0.001:
                substring = Fingerprint(os.path.join(wiki_path, name)).getSubstring()
                real_sim = substring_match(test_substring, substring)
                if real_sim > 0.01:
                    self.table.setRowCount(idx + 1)
                    self.table.setItem(idx, 0, QTableWidgetItem(name.replace('_', ' ').replace('.txt', '')))
                    self.table.setItem(idx, 1, QTableWidgetItem('{}%'.format(round(real_sim * 100))))
                    idx += 1
        if idx == 0:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem('No matches'))

        db.close()

    @pyqtSlot()
    def generate_word_cloud(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())
