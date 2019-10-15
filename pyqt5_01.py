import sys, os, enum

# QT5 Python Binding
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout, QHBoxLayout, \
    QAbstractScrollArea,QListView
from PyQt5.QtWidgets import QAction, QMainWindow, QFileDialog, QGridLayout, QGroupBox, QTextEdit, QDesktopWidget, \
    QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QFontDatabase, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, pyqtSlot, QObject, pyqtSignal


class Mode(enum.Enum):
    READ = 0  # Purely read the hex.
    ADDITION = 1  # Add to the hex.
    OVERRIDE = 2  # Override the current text.


class FileSelector(QFileDialog):  # FILE 입출력부
    def __init__(self):
        super().__init__()

        self.selectFile()  # FILE 선택창 열어줌
        self.show()  # 위젯에 띄워줌

    def selectFile(self):  # FILE 선택창 설정
        options = QFileDialog.Options()  # 이 속성은 대화 상자의 모양과 느낌에 영향을 미치는 다양한 옵션을 보유함
        options != QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Contact Icon", "", "Image Files (*.jpg *.png)",
                                                  options=options)
        # 사용자가 선택한 기존 파일을 반환하는 편의 정적 기능이다. 사용자가 취소를 누르면 null 문자열이 반환된다.
        # 윈도우즈 및 macOS에서 이 정적 기능은 QFileDialog가 아닌 기본 파일 대화 상자를 사용한다.
        # 1. 어느 위젯에 띄울지결정 하는포인터인것 같고, 다이어로그창 이름, 작업하려는 dir 시작점, 필터 (ex / All dir 로 걸면 dir 만 보임), option 인데
        # 필터 여러개중 고를 수 있네
        # Dir 인자는 제대로 돌아가는지 모르겠네

        self.fileName = fileName


class InputDialogue(QInputDialog):  # 대화상자에 input값 과 get 설정
    def __init__(self, title, text):
        super().__init__()

        # Dialogue options.
        self.dialogueTitle = title
        self.dialogueText = text

        self.initUI()

    # initUI ... Initialize the main view of the dialogue.
    def initUI(self):
        dialogueResponse, dialogueComplete = QInputDialog.getText(self, self.dialogueTitle, self.dialogueText,
                                                                  QLineEdit.Normal, '')
        # 1. 부모위젯 포인터 , 2, 타이틀, 3,그 머고 XXX : ___ 에 XX 담당 인듯,4. 그리고 mode ( echo mode ) 같은것, 4.  받아오는 스트링

        if dialogueComplete and dialogueResponse:
            self.dialogueReponse = dialogueResponse

        else:
            self.dialogueReponse = ''





class App(QMainWindow,QWidget):  # 창의 대부분의 기능
    def __init__(self):  # 창 기본 세팅 설정
        super().__init__()

        # Window options!
        self.title = 'HexQT'
        self.left = 0
        self.top = 0
        self.width = 1280
        self.height = 840

        self.rowSpacing = 4  # How many bytes before a double space.
        self.rowLength = 16  # 헥사 창에 얼마나 많은 byte 가 들어갈 것인지
        self.byteWidth = 4  # How many bits to include in a byte.
        self.mode = Mode.READ

        self.initUI()

    # readFile ... Reads file data from a file in the form of bytes and generates the text for the hex-editor.
    def readFile(self, fileName):
        fileData = ''

        if fileName:
            with open(fileName, 'rb') as fileObj:
                fileData = fileObj.read()

        self.generateView(fileData)

    # generateView ... Generates text view for hexdump likedness.
    def generateView(self, text):
        space = ' '
        bigSpace = ' ' * 4

        rowSpacing = self.rowSpacing
        rowLength = self.rowLength

        offset = 0

        offsetText = ''
        mainText = ''
        asciiText = ''

        for chars in range(1, len(text) + 1):
            byte = text[chars - 1]
            char = chr(text[chars - 1])

            # Asciitext 는 오른쪽 출력부
            if char is ' ':
                asciiText += '.'

            elif char is '\n':
                asciiText += '!'

            else:
                asciiText += char
            # main text 가 중앙에 있는것
            mainText += format(byte, '0' + str(self.byteWidth) + 'x')

            if chars % rowLength is 0:
                offsetText += format(offset, '08x') + '\n'
                mainText += '\n'
                asciiText += '\n'

            elif chars % rowSpacing is 0:
                mainText += space * 2

            else:
                mainText += space

            offset += len(char)



        self.offsetTextArea.setText(offsetText)
        self.mainTextArea.setText(mainText)
        self.asciiTextArea.setText(asciiText)

    # openFile ... Opens a file directory and returns the filename.
    def openFile(self):
        fileSelect = FileSelector()
        fileName = fileSelect.fileName

        self.readFile(fileName)

    # saveFile ... Method for saving the edited hex file.
    def saveFile(self):
        print('Saved!')

    # highlightMain ... Bi-directional highlighting from main.
    def highlightMain(self):
        # Create and get cursors for getting and setting selections.
        highlightCursor = QTextCursor(self.asciiTextArea.document())
        # asciitextArea의 처음을 가르치는 커서를 구성
        cursor = self.mainTextArea.textCursor()
        # 커서의 위치의 사본을 따서 복사 함
        # Clear any current selections and reset text color.
        highlightCursor.select(QTextCursor.Document)
        highlightCursor.setCharFormat(QTextCharFormat())
        highlightCursor.clearSelection()

        # Information about where selections and rows start.
        selectedText = cursor.selectedText()  # The actual text selected.
        selectionStart = cursor.selectionStart()
        selectionEnd = cursor.selectionEnd()

        mainText = self.mainTextArea.toPlainText().replace('\n', 'A')

        totalBytes = 0

        for char in mainText[selectionStart:selectionEnd]:
            if char is not ' ':
                totalBytes += len(char)

        asciiStart = 0

        for char in mainText[:selectionStart]:
            if char is not ' ':
                asciiStart += len(char)

        totalBytes = round(totalBytes / self.byteWidth)
        asciiStart = round(asciiStart / self.byteWidth)
        asciiEnd = asciiStart + totalBytes

        asciiText = self.asciiTextArea.toPlainText()

        # Select text and highlight it.
        highlightCursor.setPosition(asciiStart, QTextCursor.MoveAnchor)
        highlightCursor.setPosition(asciiEnd, QTextCursor.KeepAnchor)

        highlight = QTextCharFormat()
        highlight.setBackground(Qt.red)
        highlightCursor.setCharFormat(highlight)
        highlightCursor.clearSelection()

    # highlightAscii ... Bi-directional highlighting from ascii.
    def highlightAscii(self):
        selectedText = self.asciiTextArea.textCursor().selectedText()

    # offsetJump ... Creates a dialogue and gets the offset to jump to and then jumps to that offset.

    def offsetJump(self):  # input dialog 를 활용 하여 jump to ofsset 을 만듭니다.
        jumpText = InputDialogue('Jump to Offset', 'Offset').dialogueReponse
        jumpOffset = 0xF

        mainText = self.mainTextArea.toPlainText()
        mainText = mainText.strip().replace('  ', ' ')

        textCursor = self.mainTextArea.textCursor()

    # createMainView ... Creates the primary view and look of the application (3-text areas.)

    def createMainView(self):
        qhBox = QHBoxLayout()
        qhBox2 = QHBoxLayout()
        qvBox =QVBoxLayout()

        self.treeModel = QFileSystemModel()
        self.treeModel.setRootPath('')
        self.listModel = QFileSystemModel()
        self.listModel.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.treeModel)
        self.listview = QListView()
        self.listview.setModel(self.listModel);

        self.mainTextArea = QTextEdit()
        self.offsetTextArea = QTextEdit()
        self.asciiTextArea = QTextEdit()

        # Initialize them all to read only.
        self.mainTextArea.setReadOnly(True)
        self.asciiTextArea.setReadOnly(True)
        self.offsetTextArea.setReadOnly(True)

        # Create the fonts and styles to be used and then apply them.
        font = QFont("DejaVu Sans Mono", 12, QFont.Normal, True)

        self.mainTextArea.setFont(font)
        self.asciiTextArea.setFont(font)
        self.offsetTextArea.setFont(font)

        self.offsetTextArea.setTextColor(Qt.red)

        # Syncing scrolls.
        syncScrolls(self.mainTextArea, self.asciiTextArea, self.offsetTextArea)

        # Highlight linking. BUG-GY
        # self.mainTextArea.selectionChanged.connect(self.highlightMain)
        # self.asciiTextArea.selectionChanged.connect(self.highlightAscii)

        qhBox.addWidget(self.offsetTextArea, 1)
        qhBox.addWidget(self.mainTextArea, 6)
        qhBox.addWidget(self.asciiTextArea, 2)
        qhBox2.addWidget(self.tree)
        qhBox2.addWidget(self.listview)
        self.tree.clicked.connect(self.on_clicked)

        qvBox.addLayout(qhBox2)
        qvBox.addLayout(qhBox)
        return qvBox

    def on_clicked(self, index):
        path = self.treeModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.listModel.setRootPath(path))

    # initUI ... Initializes the min look of the application.
    def initUI(self):
        # Initialize basic window options.
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Center the window.
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # Creates a menu bar, (file, edit, options, etc...)
        mainMenu = self.menuBar()

        # Menus for window.
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        helpMenu = mainMenu.addMenu('Help')

        # FILE MENU ---------------------------------------

        # Open button.
        openButton = QAction(QIcon(), 'Open', self)
        openButton.setShortcut('Ctrl+O')
        openButton.setStatusTip('Open file')
        openButton.triggered.connect(self.openFile)

        # Save button.
        saveButton = QAction(QIcon(), 'Save', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setStatusTip('Open file')
        saveButton.triggered.connect(self.saveFile)

        # Optional exit stuff.
        exitButton = QAction(QIcon(), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)

        fileMenu.addAction(openButton)
        fileMenu.addAction(saveButton)
        fileMenu.addAction(exitButton)

        # EDIT MENU ---------------------------------------

        # Jump to Offset
        offsetButton = QAction(QIcon(), 'Jump to Offset', self)
        offsetButton.setShortcut('Ctrl+J')
        offsetButton.setStatusTip('Jump to Offset')
        offsetButton.triggered.connect(self.offsetJump)

        editMenu.addAction(offsetButton)

        # Creating a widget for the central widget thingy.
        centralWidget = QWidget()
        centralWidget.setLayout(self.createMainView())

        self.setCentralWidget(centralWidget)

        # Show our masterpiece.
        self.show()


# syncScrolls ... Syncs the horizontal scrollbars of multiple qTextEdit objects. Rather clunky but it works.
def syncScrolls(qTextObj0, qTextObj1, qTextObj2):
    scroll0 = qTextObj0.verticalScrollBar()
    scroll1 = qTextObj1.verticalScrollBar()
    scroll2 = qTextObj2.verticalScrollBar()

    # There seems to be no better way of doing this at present so...

    scroll0.valueChanged.connect(
        scroll1.setValue
    )

    scroll0.valueChanged.connect(
        scroll2.setValue
    )

    scroll1.valueChanged.connect(
        scroll0.setValue
    )

    scroll1.valueChanged.connect(
        scroll2.setValue
    )

    scroll2.valueChanged.connect(
        scroll1.setValue
    )

    scroll2.valueChanged.connect(
        scroll0.setValue
    )


# setStyle ... Sets the style of the QT Application. Right now using edgy black.
def setStyle(qApp):
    qApp.setStyle("Fusion")

    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.white)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    qApp.setPalette(dark_palette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def main():
    app = QApplication(sys.argv)
    setStyle(app)

    hexqt = App()
    sys.exit(app.exec_())


# Initialize the brogram.
if __name__ == '__main__':
    main()