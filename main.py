import sys
import os
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from json_viewer import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('이미지 보기')
        self.initValues()
        
        self.screenRect = QApplication.desktop().screenGeometry()
        self.setGeometry(10, 30, 1200, 840)  # x, y, w, h
        self.setWindowTitle('LabelPro Viewer')
        self.setWindowIcon(QIcon('lbp-icon-512.png'))

        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(QRect(0, 0, 980, 820))
        self.backgroundLabel.setFixedWidth(980)
        self.backgroundLabel.setFixedHeight(820)
        self.backgroundLabel.setStyleSheet("border: 1px solid black;") 

        self.maskLabel = QLabel(self)
        self.maskLabel.setGeometry(QRect(0, 0, 980, 820))
        self.maskLabel.setFixedWidth(980)
        self.maskLabel.setFixedHeight(820)
        self.maskLabel.setStyleSheet("border: 1px solid black;") 
        imageLayout= QGridLayout()
        # imageLayout.
        imageLayout.addWidget(self.backgroundLabel, 0, 0, 3, 3)
        imageLayout.addWidget(self.maskLabel, 0, 0, 3, 3)

        # QButton 위젯 생성 - FileDialog 을 띄위기 위한 버튼
        openBackgroundButton = QPushButton('원천데이터 경로 선택', self)
        openBackgroundButton.clicked.connect(self.selectSourceImagePath)
        openBackgroundButton.setGeometry(1000, 10, 180, 25)
        self.lblSrcDir = QLabel(self)
        self.lblSrcDir.setGeometry(QRect(1000, 50, 180, 25))
        self.lblSrcDir.setText('원천데이터 경로를 선택하세요')

        openMaskButton = QPushButton('라벨링데이터 경로 선택', self)
        openMaskButton.clicked.connect(self.selectMaskImagePath)
        openMaskButton.setGeometry(1000, 130, 180, 25)
        self.lblLblDir = QLabel(self)
        self.lblLblDir.setGeometry(QRect(1000, 170, 180, 25))
        self.lblLblDir.setText('라벨링데이터 경로를 선택하세요')

        self.listView = QListView(self)
        self.fileListModel = QStandardItemModel()
        self.listView.setModel(self.fileListModel)
        self.listView.selectionModel().selectionChanged.connect(self.listItemSelected)

        btShowJSON = QPushButton('JSON', self)
        btShowJSON.clicked.connect(self.showJSON)
        btShowJSON.setGeometry(1000, 130, 180, 25)
        

        slider = QSlider(Qt.Horizontal, self)
        slider.setGeometry(1000, 200, 180, 30)
        slider.setRange(0, 100)
        slider.setSliderPosition(100)

        slider.valueChanged.connect(self.valueChanged)
        ctrlLayout = QVBoxLayout()
        ctrlLayout.addWidget(openBackgroundButton)
        ctrlLayout.addWidget(self.lblSrcDir)
        ctrlLayout.addWidget(openMaskButton)
        ctrlLayout.addWidget(self.lblLblDir)
        ctrlLayout.addWidget(slider)
        ctrlLayout.addWidget(btShowJSON)
        ctrlLayout.addWidget(self.listView)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(imageLayout)
        mainLayout.addLayout(ctrlLayout)
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)
        mainWidget.setLayout(mainLayout)

        self.opacityEffect = QGraphicsOpacityEffect()
        self.opacityEffect.setOpacity(1)
        self.maskLabel.setGraphicsEffect(self.opacityEffect)

        self.jsonViewer = JsonViewer(self)
        self.lastSelectedFileName = ''


    def initValues(self):
        self.srcImagePath = ''
        self.maskImagePath = ''

    def selectSourceImagePath(self):
        strDir = QFileDialog.getExistingDirectory(None, "원천데이터 경로를 선택하세요.")
        if strDir != "":
            self.srcImagePath = strDir
            strPath, strDirName = os.path.split(strDir)
            self.lblSrcDir.setText(strDirName)
            self.scanImages()
            
    def selectMaskImagePath(self):
        strDir = QFileDialog.getExistingDirectory(None, "라벨링데이터 경로를 선택하세요.")
        if strDir != "":
            self.maskImagePath = strDir
            strPath, strDirName = os.path.split(strDir)
            self.lblLblDir.setText(strDirName)
            self.scanImages()

    def scanImages(self):
        self.fileListModel.clear()
        if os.path.isdir(self.srcImagePath) and os.path.isdir(self.maskImagePath):
            arSrcNames = listdir(self.srcImagePath)
            for srcName in arSrcNames:
                if srcName.endswith('.jpg'):
                    strSrcImgName = srcName
                    strMaskImgName = srcName.replace('.jpg', '.png')
                    if os.path.isfile(os.path.join(self.maskImagePath, strMaskImgName)):
                        self.fileListModel.appendRow(QStandardItem(strSrcImgName))
                
            
    def listItemSelected(self, cur, prev):
        arIndexes = cur.indexes()
        if len(arIndexes) > 0:
            strSelectedFileName = self.fileListModel.item(arIndexes[0].row()).text()
            print(strSelectedFileName)
            self.setWindowTitle('LabelPro Viewer')
            bOpened = False
            if self.openBackgroundFile(strSelectedFileName):
                if self.openMaskFile(strSelectedFileName):
                    self.setWindowTitle('LabelPro Viewer - ' + strSelectedFileName)
                    self.lastSelectedFileName = strSelectedFileName
                    bOpened = True

            if bOpened == False:
                QMessageBox.about(self, '오류', '이미지를 불러올 수 없습니다.')

    def openBackgroundFile(self, fileName):
        strJPGPath = os.path.join(self.srcImagePath, fileName)
        if not os.path.isfile(strJPGPath):
            return False
        self.screenRect
        image = QPixmap(strJPGPath).scaled(980, 820, Qt.KeepAspectRatio)
        self.backgroundLabel.setPixmap(image)
        return True

    def openMaskFile(self, fileName):
        strPNGPath = os.path.join(self.maskImagePath, fileName.replace('.jpg', '.png'))
        if not os.path.isfile(strPNGPath):
            return False
        print(f'maskPath: {strPNGPath}')
        image = QPixmap(strPNGPath).scaled(980, 820, Qt.KeepAspectRatio)
        self.maskLabel.setPixmap(image)
        return True

    def showJSON(self):
        strJSONPath = os.path.join(self.maskImagePath, self.lastSelectedFileName.replace('.jpg', '.json'))
        if not os.path.isfile(strJSONPath):
            QMessageBox.about(self, '오류', 'JSON 파일을 찾을 수 없습니다.')
            return False
        # strJsonPath = os.path.join(self.maskImagePath, strMaskImgName)
        self.jsonViewer.showJson(strJSONPath)
        self.jsonViewer.show()

    
    def valueChanged(self, value):
        self.opacityEffect.setOpacity(value / 100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    