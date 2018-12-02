import os, sys

from database import *
from wordCloud import *

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QPushButton, QMainWindow, QLineEdit, QLabel 
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Paths to test data and wikipedia articles
path = os.path.dirname(os.path.abspath(__file__))
wiki_path = os.path.join(path, 'Wikipages')
test_path = os.path.join(path, 'TestOpgaver')


# Show wordclouds on GUI
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=4, height=1, dpi=100):
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

    def plot_top(self, file):
        test_file = os.path.join(test_path, file)
        wc = WordCloud(test_file)
        cloud = wc.getCloud()
        self.top_plt.imshow(cloud, interpolation="bilinear")
        self.draw()

    def plot_btm(self, file):
        test_file = os.path.join(wiki_path, file.replace(' ', '_') + '.txt')
        wc = WordCloud(test_file)
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
        self.show()

    def initUI(self, left=800, top=500, width=600, height=400):
        # Window properties
        self.setGeometry(left, top, width, height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(self.icon)

        # Box layouts
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        # Text label
        label = QLabel('Input document:')
        self.v_layout.addWidget(label)
        
        # Input box
        self.textbox = QLineEdit(self)
        f = self.textbox.font()
        f.setPointSize(9)
        self.textbox.setFont(f)
        self.v_layout.addWidget(self.textbox)

        # Detect plagiarism button
        button = QPushButton('Detect plagiarism', self)
        button.setToolTip('Detect if the article contains plagiarism from Wikipedia')
        button.clicked.connect(self.on_click)
        self.v_layout.addWidget(button)

        # Table
        self.table = QTableWidget(self)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnCount(1)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
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
        # Reset table and wordclouds
        self.reset_view()

        # Detect potential plagiarised articles
        try:
            file = self.textbox.text() + '.txt'
            test_file = os.path.join(test_path, file)
            self.detect_plagiarism(test_file)
        except FileNotFoundError:
            self.table.setItem(0, 0, QTableWidgetItem('File not found'))
            return
        
        # Show detected articles on GUI
        self.update_table()

        # Generate wordcloud from input article
        self.m.plot_top(file)

    @pyqtSlot()
    def table_click(self):
        try:
            file = self.table.currentItem().text()
            self.m.plot_btm(file)
        except FileNotFoundError:
            pass

    def reset_view(self):
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.m.setParent(None)
        self.m = PlotCanvas(self)
        self.h_layout.addWidget(self.m)

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
