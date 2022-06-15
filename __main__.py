from pathlib import Path
from re import T

from PySide6.QtWidgets import (
    QApplication,
    QInputDialog,
    QMessageBox,
    QHeaderView,
    QMainWindow,
    QFileDialog,
    QTableView, 
    QTabWidget,
    QToolBar,
    QMenuBar
)

from PySide6.QtGui import (
    QAction,
    QIcon,
    QFont
)
from PySide6.QtCore import (
    QSettings,
    QRect,
    Slot,
    Qt
)

from PySide6.QtSql import (
    QSqlTableModel,
    QSqlDatabase,
    QSql
)

from tabbar import VTabBar


with open("style.qss") as style:
    stylesheet = style.read()


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings()

        self.setWindowIcon(QIcon("icons/stack.svg"))
        self.setWindowTitle("SQL Viewer - example_dbs\chinook.db")
        self.setStyleSheet(stylesheet)
        self.setGeometry(self.settings.value("geometry", QRect(200, 200, 800, 600)))

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabBar(VTabBar())
        self.tabWidget.setTabPosition(QTabWidget.West)

        self.db = QSqlDatabase.addDatabase("QSQLITE")

        self.setDB("example_dbs\chinook.db")

        # --- Tool bar ---
        self.fileToolbar = QToolBar(self.tr("File"), self)
        self.addToolBar(self.fileToolbar)

        # actions
        openFile = QAction(
            QIcon("icons/folder-open.svg"), 
            self.tr("Open..."), self.fileToolbar,
            triggered=self.open
        )

        saveAll = QAction(
            QIcon("icons/document-edit.svg"),
            self.tr("Save Changes"), self.fileToolbar,
            triggered=self.tabWidget.currentWidget().model().submitAll
        )

        undoAll = QAction(
            QIcon("icons/backspace.svg"),
            self.tr("Undo All"), self.fileToolbar,
            triggered=self.tabWidget.currentWidget().model().revertAll
        )

        terminal = QAction(
            QIcon("icons/code.svg"),
            self.tr("Open Terminal"), self.fileToolbar,
            triggered=self.inputCommand
        )

        self.fileToolbar.addActions((openFile,))
        self.fileToolbar.addSeparator()
        self.fileToolbar.addActions((saveAll, undoAll))
        self.fileToolbar.addSeparator()
        self.fileToolbar.addActions((terminal,))

        self.setCentralWidget(self.tabWidget)
        self.show()

    def closeEvent(self, event) -> None:
        self.settings.setValue("geometry", self.rect())
        event.accept()

    def inputCommand(self):
        commands = QInputDialog.getMultiLineText(
            self, self.tr("Input SQL Command"),
            self.tr("Input command(s) here (seperature commands by newline):"),
            inputMethodHints=Qt.ImhMultiLine | Qt.ImhNoAutoUppercase | Qt.ImhPreferLatin
        )

        for command in commands.split('\n'):
            self.db.exec(command)

            if self.db.lastError():
                QMessageBox.critical(self, "Error", self.db.lastError().text())


    def open(self):
        file = QFileDialog.getOpenFileName(
            self, 
            self.tr("Open SQL file..."),
            "",
            self.tr("SQL files (*.db *.sqlite);;All files (*)")
        )

        if file[0]:
            self.setDB(file[0])

    def setDB(self, file: str):
        self.db.setDatabaseName(file)

        # DB error checking
        if not self.db.open():
            print("Error when opening database:", self.db.lastError())

        self.setWindowTitle("SQL Viewer - " + str(Path(file).resolve()))

        self.tabWidget.clear()

        for tableName in self.db.tables(QSql.AllTables):
            model = QSqlTableModel(self, self.db)
            model.setTable(tableName)
            model.select()
            model.setEditStrategy(QSqlTableModel.OnManualSubmit)

            table = QTableView(self)
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeToContents
            )
            table.setModel(model) 

            self.tabWidget.addTab(table, tableName)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)   
    app.setApplicationName("SQL Viewer")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Unknown")

    window = Window()

    sys.exit(app.exec())
