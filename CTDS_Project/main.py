import os, sys

from database import *
from wordCloud import *

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QMainWindow, QLineEdit, QLabel, QSpinBox
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Paths to test data and wikipedia articles
path = os.path.dirname(os.path.abspath(__file__))
wiki_path = os.path.join(path, 'Wikipages')
test_path = os.path.join(path, 'TestOpgaver')


# Show wordclouds on GUI
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=5, height=1, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.top_plt = self.figure.add_subplot(211)
        self.top_plt.axis("off")
        self.top_plt.set_title('Input document')
        self.btm_plt = self.figure.add_subplot(212)
        self.btm_plt.axis("off")

    def plot_top(self, file, words=10):
        test_file = os.path.join(test_path, file)
        wc = WordCloud(test_file, words)
        cloud = wc.getCloud()
        self.top_plt.imshow(cloud, interpolation="bilinear")
        self.draw()

    def plot_btm(self, file, words=10):
        test_file = os.path.join(wiki_path, file.replace(' ', '_') + '.txt')
        wc = WordCloud(test_file, words)
        cloud = wc.getCloud()
        self.btm_plt.set_title(file)
        self.btm_plt.imshow(cloud, interpolation="bilinear")
        self.draw()

# TODO: Select number of words in wordcloud and show a list of available input documents
# Main application window
class App(QWidget):

    def __init__(self):
        super().__init__()

        # Get article fingerprints from database
        db = Database()
        self.db_sigs = db.get_all_signatures()
        db.close()

        # Initialize window
        self.title = 'Plagiarism detection'
        self.icon = QIcon(os.path.join(path, 'Wikipedia-icon.png'))
        self.initUI()
        self.find_documents()
        self.show()

    def initUI(self, left=800, top=500, width=1200, height=600):
        # Window properties
        self.setGeometry(left, top, width, height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(self.icon)

        # Box layouts
        self.h_layout = QHBoxLayout()
        self.v_layout_left = QVBoxLayout()
        self.v_layout_mid = QVBoxLayout()
        self.v_layout_right = QVBoxLayout()

        sel_label = QLabel('Select input document:')
        self.v_layout_left.addWidget(sel_label)

        # Table
        self.doc_table = QTableWidget(self)
        self.doc_table.verticalHeader().setVisible(False)
        self.doc_table.horizontalHeader().setVisible(False)
        self.doc_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.doc_table.setColumnCount(1)
        self.doc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.doc_table.clicked.connect(self.select_doc)
        self.v_layout_left.addWidget(self.doc_table)

        # Detect plagiarism button
        button = QPushButton('Detect plagiarism', self)
        button.setToolTip('Detect if the article contains plagiarism from Wikipedia')
        button.clicked.connect(self.on_click)
        self.v_layout_left.addWidget(button)

        self.h_layout.addLayout(self.v_layout_left)

        # Text label
        label = QLabel('Detected documents:')
        self.v_layout_mid.addWidget(label)
        
        # Input box
        # self.textbox = QLineEdit(self)
        # f = self.textbox.font()
        # f.setPointSize(9)
        # self.textbox.setFont(f)
        # self.v_layout_mid.addWidget(self.textbox)

        # Table
        self.table = QTableWidget(self)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnCount(1)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.clicked.connect(self.table_click)
        self.v_layout_mid.addWidget(self.table)

        # Add vertical layout to horizontal layout
        self.h_layout.addLayout(self.v_layout_mid)

        # Text label
        label2 = QLabel('Number of words in cloud:')
        self.v_layout_right.addWidget(label2)

        # Number selection
        self.int_sel = QSpinBox(self)
        self.int_sel.setValue(10)
        self.int_sel.setRange(1, 20)
        self.int_sel.valueChanged.connect(self.update_wordclouds)
        self.int_sel.lineEdit().setReadOnly(True)
        sel_text = self.int_sel.lineEdit()
        sel_text.selectionChanged.connect(lambda : self.int_sel.lineEdit().deselect())
        self.v_layout_right.addWidget(self.int_sel)

        # Matplotlib canvas
        self.m = PlotCanvas(self)
        self.v_layout_right.addWidget(self.m)
        self.h_layout.addLayout(self.v_layout_right)

        self.setLayout(self.h_layout)

    @pyqtSlot()
    def on_click(self):
        # Reset table and wordclouds
        self.reset_view()

        # Detect potential plagiarised articles
        try:
            test_file = os.path.join(test_path, self.file1)
            self.detect_plagiarism(test_file)
        except FileNotFoundError and AttributeError:
            self.table.setItem(0, 0, QTableWidgetItem('File not found'))
            return
        
        # Show detected articles on GUI
        self.update_table()

        # Generate wordcloud from input article
        self.m.plot_top(self.file1, self.int_sel.value())

    @pyqtSlot()
    def table_click(self):
        try:
            self.file2 = self.table.currentItem().text()
            self.m.plot_btm(self.file2, self.int_sel.value())
        except FileNotFoundError:
            pass

    def reset_view(self):
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.m.setParent(None)
        self.m = PlotCanvas(self)
        self.v_layout_right.addWidget(self.m)

    def update_table(self):
        if self.detected != []:
            self.table.setColumnCount(2)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            for idx, (name, sim) in enumerate(self.detected):
                self.table.setRowCount(idx + 1)
                self.table.setItem(idx, 0, QTableWidgetItem(name.replace('_', ' ').replace('.txt', '')))
                self.table.setItem(idx, 1, QTableWidgetItem('{} %'.format(round(sim * 100))))
                self.table.item(idx, 1).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
        else:
            self.table.setItem(0, 0, QTableWidgetItem('No matches'))

    def update_wordclouds(self):
        print('It works')

    def find_documents(self):
        files = [f for f in os.listdir(test_path) if '.txt' in f]
        for idx, file in enumerate(files):
            self.doc_table.setRowCount(idx + 1)
            self.doc_table.setItem(idx, 0, QTableWidgetItem(file))

    def select_doc(self):
        self.file1 = self.doc_table.currentItem().text()

    def detect_plagiarism(self, file):
        # Create fingerprint of input file
        test_fp = Fingerprint(file)
        test_sig = test_fp.getSignatures()
        test_substring = test_fp.getSubstring()

        # Detect potential plagiarised articles
        self.detected = []
        for name, sig in self.db_sigs.items():
            # Calculate jaccard similarity
            sim = jaccard(test_sig, sig)
            if sim >= 0.001:
                # Calculate substring similarity
                substring = Fingerprint(os.path.join(wiki_path, name)).getSubstring()
                real_sim = substring_match(test_substring, substring)
                if real_sim > 0.01:
                    self.detected.append((name, real_sim))
        self.detected.sort(key=lambda x: x[1], reverse=True)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())
