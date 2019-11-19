import os
import sys
import subprocess
import threading

import psutil
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QTreeWidgetItem, QFileDialog
from PyQt5.uic import loadUi


class tests_gui(QDialog):

    def __init__(self):
        super(tests_gui, self).__init__()
        loadUi('Tests_GUI.ui', self)
        self.setWindowTitle('Tests GUI')

        self.tree_tests.setHeaderHidden(True)

        self.select_folder.clicked.connect(self.on_build_tree)
        self.run_tests.clicked.connect(self.on_run_tests)

        self.stop_test.setEnabled(False)
        self.stop_test.clicked.connect(self.on_stop_tests)

        self.log_results.clicked.connect(self.on_log_results)
        self.clear_log.clicked.connect(self.on_clear_results)

        self.check_all.clicked.connect(self.check_box)

    # Add items (js files) in tree widget after the user chooser folder
    def on_build_tree(self):
        try:
            self.tree_tests.clear()
            self.file = str(QFileDialog.getExistingDirectory(self, "Select Directory", "../../week6-7/LHWeb/tests/"))
            tests_js_files = os.listdir(self.file)
            for test in tests_js_files:
                if test.endswith(".js"):
                    QTreeWidgetItem(self.tree_tests, [test]).setCheckState(0, QtCore.Qt.Unchecked)
        except:
            self.logger.setText("Choose folder")

    # Run all items that checked in tree widget with thread
    def on_run_tests(self):
        try:
            # Clear results.log file from folder path
            with open(f'{self.file}/log/results.log', 'w') as log_results:
                log_results.write('')

            # Take items from tree_tests. If item is Checked, it added to self.active
            root = self.tree_tests.invisibleRootItem()
            child_count = root.childCount()
            self.active = ""
            for i in range(child_count):
                item = root.child(i)
                if item.checkState(0) == QtCore.Qt.Checked:
                    if "node" in self.active:
                        self.active += " && "
                    self.active += f"node {item.text(0)}"
            # if active is empty -> the user need to pick files. else -> run files.
            if self.active == "":
                self.logger.setText("Choose files to run")
            else:
                self.logger.setText("")
                # Invoke process in thread
                proc = threading.Thread(target=self.run_it, args=(self.active,))
                proc.start()
                self.run_tests.setEnabled(False)
                self.stop_test.setEnabled(True)
                self.active = ""
        except:
            self.logger.setText("Choose files to run")

    # Run process in another thread
    def run_it(self, active):
        self.process = subprocess.Popen(active, shell=True, cwd=self.file)
        self.process.communicate()
        self.stop_test.setEnabled(False)
        self.run_tests.setEnabled(True)

    def on_stop_tests(self):
        try:
            process = psutil.Process(self.process.pid)
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
            self.stop_test.setEnabled(False)
            self.run_tests.setEnabled(True)
            self.logger.setText("Stop testing!")
        except Exception as e:
            self.logger.setText(f'Got exception in running_thread {e}')

    def on_log_results(self):
        try:
            results_log = (open(f'{self.file}/log/results.log', 'r').read()).split("\n")
            results = ""
            for word in results_log:
                if "info" in word:
                    results += f"<div style=\"color: #053b5f;\" > {word} </div>"
                elif "error" in word:
                    results += f"<div style=\"color: red;\" > {word} </div>"
            self.logger.setText(results)
        except:
            self.logger.setText("NO RESULTS")

    def on_clear_results(self):
        self.logger.clear()

    def check_box(self):
        root = self.tree_tests.invisibleRootItem()
        child_count = root.childCount()
        if self.check_all.text() == "Uncheck All":
            self.uncheck_box()
        else:
            for i in range(child_count):
                root.child(i).setCheckState(0, QtCore.Qt.Checked)
                self.check_all.setText("Uncheck All")

    def uncheck_box(self):
        root = self.tree_tests.invisibleRootItem()
        child_count = root.childCount()
        if self.check_all.text() == "Check All":
            self.check_box()
        else:
            for i in range(child_count):
                root.child(i).setCheckState(0, QtCore.Qt.Unchecked)
                self.check_all.setText("Check All")


app = QApplication(sys.argv)
widget = tests_gui()
widget.show()
sys.exit(app.exec())
