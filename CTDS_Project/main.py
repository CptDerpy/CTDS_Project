from database import * # pylint: disable=W0614
from wordCloud import * # pylint: disable=W0614
import os, sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QMainWindow, QLineEdit, QLabel 
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Paths to test data and wikipedia articles
path = os.path.dirname(os.path.abspath(__file__))
wiki_path = os.path.join(path, 'Wikipages')
test_path = os.path.join(path, 'TestOpgaver')


# Show wordclouds on GUI
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=5, height=4, dpi=100):
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
        self.btm_plt.set_title('Wikipedia article')

    def plot_top(self, file):
        test_file = os.path.join(test_path, file)
        wc = wordCloud(test_file)
        cloud = wc.getCloud()
        self.top_plt.imshow(cloud, interpolation="bilinear")

    def plot_btm(self, file):
        test_file = os.path.join(wiki_path, file)
        wc = wordCloud(test_file)
        cloud = wc.getCloud()
        self.btm_plt.imshow(cloud, interpolation="bilinear")


# Main application window
class App(QWidget):

    def __init__(self):
        super().__init__()
        self.left = 800
        self.top = 500
        self.width = 800
        self.height = 600
        self.title = 'Plagiarism detection'
        self.icon = QIcon(os.path.join(path, 'Wikipedia-icon.png'))
        self.initUI()
        self.show()

    def initUI(self):
        # Window properties
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(self.icon)

        # Box layouts
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        # Text label
        label = QLabel('Input article:')
        self.v_layout.addWidget(label)
        
        # Input box
        self.textbox = QLineEdit(self)
        f = self.textbox.font()
        f.setPointSize(9)
        self.textbox.setFont(f)
        self.v_layout.addWidget(self.textbox)

        # Detect plagiarism button
        button = QPushButton('Run', self)
        button.setToolTip('Detect if the article contains plagiarism')
        button.clicked.connect(self.on_click)
        self.v_layout.addWidget(button)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setVisible(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.clicked.connect(self.table_click)
        self.v_layout.addWidget(self.table)

        # Add vertical layout to horizontal layout
        self.h_layout.addLayout(self.v_layout)

        # Matplotlib canvas
        self.m = PlotCanvas(self)
        self.h_layout.addWidget(self.m)

        self.setLayout(self.h_layout)

    @pyqtSlot()
    def on_click(self):
        # Reset table
        self.table.setRowCount(1)
        self.table.setItem(0, 1, QTableWidgetItem(''))

        # Create fingerprint of input file
        self.file = self.textbox.text() + '.txt'
        test_file = os.path.join(test_path, self.file)
        try:
            test_fp = Fingerprint(test_file)
            test_sig = test_fp.getSignatures()
            test_substring = test_fp.getSubstring()
        except FileNotFoundError:
            self.table.setItem(0, 0, QTableWidgetItem('File not found'))
            return

        # Get article fingerprints from database
        db = Database()
        db_sigs = db.get_all_signatures()
        db.close()

        # Detect potential plagiarism and show percentages on GUI
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
                    self.table.setItem(idx, 1, QTableWidgetItem('{} %'.format(round(real_sim * 100))))
                    self.table.item(idx, 1).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    idx += 1
        if idx == 0:
            self.table.setItem(0, 0, QTableWidgetItem('No matches'))

        # Generate wordcloud from input article
        self.m.setParent(None)
        self.m = PlotCanvas(self)
        self.h_layout.addWidget(self.m)
        self.m.plot_top(self.file)
        self.m.draw()

    @pyqtSlot()
    def table_click(self):
        try:
            file = self.table.currentItem().text().replace(' ', '_') + '.txt'
            # self.m.setParent(None)
            # self.m = PlotCanvas(self, self.file, selected_item)
            # self.h_layout.addWidget(self.m)
            self.m.plot_btm(file)
            self.m.draw()
        except FileNotFoundError:
            pass
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())
