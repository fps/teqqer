from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import carla_backend

carla_host = carla_backend.Host("/usr/local/lib/carla/libcarla_standalone.so")
print (carla_host.get_engine_driver_count())

class song:
	def __init__(self):
		self.tempo = 250
		self.loop_range = (0, 1)
		

class main_window(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		settings = QSettings()
		
		self.resize(settings.value("size", QSize(400, 400)).toSize())
		self.move(settings.value("pos", QPoint(200, 200)).toPoint())
		
		menu_bar = QMenuBar()
		file_menu = QMenu()
		
	def closeEvent(self, e):
		settings = QSettings()
		settings.setValue("size", self.size())
		settings.setValue("pos", self.pos())

app = QApplication(sys.argv)

app.setOrganizationName("fps.io")
app.setOrganizationDomain("fps.io")
app.setApplicationName("teqqer")

the_main_window = main_window()
the_main_window.show()

table_view = QTableView()
the_main_window.setCentralWidget(table_view)

app.exec_()
