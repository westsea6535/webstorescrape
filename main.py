import sys
from PyQt5.QtWidgets import QApplication
from qtInterface import guiForm

if __name__ == '__main__':
  app = QApplication(sys.argv)
  form = guiForm()
  form.show()
  sys.exit(app.exec_())