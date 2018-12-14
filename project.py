import csv
import math
import random
from PyQt5 import QtCore, QtGui, QtWidgets


def DataImputFromCsv(FileName, time, tupe):
    time = int(time)
    if time < 0 or time > 23:
        raise NameError("Bad time!")
    else:
        if tupe is True:
            if ((time >= 0) and (time <= 9)):
                time = str(time)
                time = "0" + str(time)
        time = str(time)
        time += ":00"
        Position = [[], []]
        try:
            with open(FileName, 'r') as f:
                reader = csv.DictReader(f, delimiter=';')
                i = 0
                for row in reader:
                    i += 1
                    Position[1].append(float(row[time].replace(',', '.')))
                    Position[0].append(float(row[''].replace(',', '.')))
                f.close()
            return Position
        except:
            raise NameError("Error in reading")


def func_weath(x1, x2, x3, x4):
    while True:
        vysota = random.random()
        if vysota <= 0.1875:
            chis = random.uniform(x1, x2)
            return chis
        elif vysota <= 0.8125:
            chis = random.uniform(x2, x3)
            return chis
        elif vysota <= 1:
            chis = random.uniform(x3, x4)
            return chis


def sun_24():
    B = []
    file = "Sollar.csv"
    tupl = False
    for time in range(0, 24):
        A = DataImputFromCsv(file, time, tupl)
        x = func_weath(A[1][0], A[1][1], A[1][3], A[1][4])
        B.append(x)
    return B


def wind_24():
    c = []
    file = "Wind.csv"
    tupl = False
    for time in range(0, 24):
        A = DataImputFromCsv(file, time, tupl)
        x = func_weath(A[1][0], A[1][1], A[1][3], A[1][4])
        c.append(x)
    return c


def windGeneration(P):
    const = 5
    c = wind_24()
    for elem in c:
        elem = (elem / const) ** 3 * P
    return c


def sunGeneration(P):
    B = sun_24()
    c = []
    for i in B:
        c.append(i * P)
    return c


def fullGeneration(Psun, Pwind, Pdiesel):
    full = [0] * 24
    C = sunGeneration(Psun)
    B = windGeneration(Pwind)
    for elem in range(0, 24):
        full[elem] = C[elem] + B[elem] + Pdiesel
    return (full)


def mkConsumption():
    file = "Data.csv"
    A = []
    tupl = True
    for time in range(0, 24):
        hist = DataImputFromCsv(file, time, tupl)
        vysota = random.random()
        histzero = hist[0][0]
        shir = hist[0][1] - hist[0][0]
        x = len(hist[0])
        summa = hist[1][0]
        for i in range(0, x):
            if vysota <= summa:
                chis = random.uniform(histzero, histzero + shir * x)
                A.append(chis)
                break
            else:
                i += 1
                summa += hist[1][i]
    return A


def countStats(Psun, Pwind, Pdiesel):
    amountppl = 1
    numb = 0
    discon = 0
    fullGen = fullGeneration(Psun, Pwind, Pdiesel)
    fullCons = mkConsumption()
    if fullGen[1] < fullCons[1]:
        numb = 1
    for i in range(0, 24):
        if fullGen[i] < fullCons[i] and fullGen[i - 1] >= fullCons[i - 1]:
            numb += 1
    for i in range(0, 24):
        if fullGen[i] < fullCons[i]:
            discon += 1
    SAIFI = numb / amountppl
    if numb != 0:
        CAIDI = discon / numb
    else:
        CAIDI = 0
    A = [SAIFI, CAIDI]
    return A


class Output:
    powerS = None
    powerW = None
    powerD = None
    CAIDI = None
    SAIDI = None
    price = None
    good = None


def makeStats(Psun, Pwind, Pdiesel):
    S24 = [0] * 25
    C24 = [0] * 25
    for i in range(10):
        A = countStats(Psun, Pwind, Pdiesel)
        for j in range(0, 25):
            if A[0] == j:
                S24[j] += 1
            if (j + 1 > A[1] >= j):
                C24[j] += 1
    Mass = [S24, C24]
    return Mass


def GenConfig(w1, w3, s1, s3, d1, d3):
    Mass = []
    SC = []
    A = [w1, (w1 + w3) / 2, w3]
    B = [s1, (s1 + s3) / 2, s3]
    C = [d1, (d1 + d3) / 2, d3]
    for i in A:
        for j in B:
            for g in C:
                x = Output()
                x.powerS = j
                x.powerW = i
                x.powerD = g
                Mass.append(x)
    for i in range(0, 27):
        SaiCai = makeStats(Mass[i].powerW, Mass[i].powerS, Mass[i].powerD)
        Mass[i].SAIFI = SaiCai[0]
        Mass[i].CAIDI = SaiCai[1]
    return Mass


class Input:
    priceW = None
    priceS = None
    priceD = None
    thrSAIFI = None
    thrCAIDI = None
    probCAIDI = None
    probSAIFI = None
    windLow = None
    windHigh = None
    sunLow = None
    sunHigh = None
    dieLow = None
    dieHigh = None


def GoodGist(porogSA, verSA, porogCA, verCA, Mass):
    sumver = 0
    fullsum = 0
    for g in range(0, 24):
        fullsum += Mass.SAIFI[g]
    for j in range(int(porogSA), 24):
        sumver += Mass.SAIFI[j]
    ourver = sumver / fullsum
    if ourver > verSA:
        return False
    sumver1 = 0
    fullsum1 = 0
    for g in range(0, 24):
        fullsum1 += Mass.CAIDI[g]
    for j in range(int(porogCA), 24):
        sumver1 += Mass.CAIDI[j]
    ourver1 = sumver1 / max(fullsum1, 1)
    if ourver1 > verCA:
        return False
    return True


def TargetFunc(x, Data):
    k = GoodGist(x.thrSAIFI, x.probSAIFI, x.thrCAIDI, x.probCAIDI, Data)
    wind = Data.powerW * x.priceW
    solar = Data.powerS * x.priceS
    diesel = Data.powerD * x.priceD
    if k == True:
        fullprice = wind + solar + diesel
    else:
        fullprice = wind + solar + diesel + math.inf
    return fullprice


def BubbleSort(A):
    for j in range(len(A) - 1):
        for i in range(len(A) - 1 - j):
            if A[i] > A[i + 1]:
                A[i], A[i + 1] = A[i + 1], A[i]


defaultInput = Input()


def bubble_sort(x):
    Mass = GenConfig(x.windLow, x.windHigh, x.sunLow, x.sunHigh, x.dieLow, x.dieHigh)
    EndMass = []
    for i in range(0, len(Mass)):
        for j in range(0, len(Mass) - 1):
            if TargetFunc(x, Mass[j]) > TargetFunc(x, Mass[j + 1]):
                Mass[j], Mass[j + 1] = Mass[j + 1], Mass[j]
    for i in range(0, 3):
        Mass[i].price = TargetFunc(x, Mass[i])
        Mass[i].good = GoodGist(x.thrSAIFI, x.probSAIFI, x.thrCAIDI, x.probCAIDI, Mass[i])
        EndMass.append(Mass[i])
    return EndMass


def mainAlgorithm(inputData):
    return bubble_sort(inputData)


Inp = Input()


class OutPutInterface(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(630, 865)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 10, 251, 51))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 191, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 110, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 150, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(250, 20, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.Price1 = QtWidgets.QLabel(Dialog)
        self.Price1.setGeometry(QtCore.QRect(410, 20, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(22)
        self.Price1.setFont(font)
        self.Price1.setText("")
        self.Price1.setObjectName("Price1")
        self.powerWind1 = QtWidgets.QLabel(Dialog)
        self.powerWind1.setGeometry(QtCore.QRect(190, 70, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerWind1.setFont(font)
        self.powerWind1.setText("")
        self.powerWind1.setObjectName("powerWind1")
        self.powerSolar1 = QtWidgets.QLabel(Dialog)
        self.powerSolar1.setGeometry(QtCore.QRect(190, 110, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerSolar1.setFont(font)
        self.powerSolar1.setText("")
        self.powerSolar1.setObjectName("powerSolar1")
        self.powerWind2 = QtWidgets.QLabel(Dialog)
        self.powerWind2.setGeometry(QtCore.QRect(200, 340, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerWind2.setFont(font)
        self.powerWind2.setText("")
        self.powerWind2.setObjectName("powerWind2")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(20, 340, 191, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.powerDisel2 = QtWidgets.QLabel(Dialog)
        self.powerDisel2.setGeometry(QtCore.QRect(200, 420, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerDisel2.setFont(font)
        self.powerDisel2.setText("")
        self.powerDisel2.setObjectName("powerDisel2")
        self.powerSolar2 = QtWidgets.QLabel(Dialog)
        self.powerSolar2.setGeometry(QtCore.QRect(200, 380, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerSolar2.setFont(font)
        self.powerSolar2.setText("")
        self.powerSolar2.setObjectName("powerSolar2")
        self.obg1 = QtWidgets.QLabel(Dialog)
        self.obg1.setGeometry(QtCore.QRect(260, 290, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.obg1.setFont(font)
        self.obg1.setObjectName("obg1")
        self.label_14 = QtWidgets.QLabel(Dialog)
        self.label_14.setGeometry(QtCore.QRect(10, 280, 251, 51))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(Dialog)
        self.label_15.setGeometry(QtCore.QRect(20, 420, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.Price2 = QtWidgets.QLabel(Dialog)
        self.Price2.setGeometry(QtCore.QRect(420, 290, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(22)
        self.Price2.setFont(font)
        self.Price2.setText("")
        self.Price2.setObjectName("Price2")
        self.label_16 = QtWidgets.QLabel(Dialog)
        self.label_16.setGeometry(QtCore.QRect(20, 380, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.powerWind3 = QtWidgets.QLabel(Dialog)
        self.powerWind3.setGeometry(QtCore.QRect(200, 640, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerWind3.setFont(font)
        self.powerWind3.setText("")
        self.powerWind3.setObjectName("powerWind3")
        self.label_18 = QtWidgets.QLabel(Dialog)
        self.label_18.setGeometry(QtCore.QRect(20, 640, 191, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.powerDisel3 = QtWidgets.QLabel(Dialog)
        self.powerDisel3.setGeometry(QtCore.QRect(200, 720, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerDisel3.setFont(font)
        self.powerDisel3.setText("")
        self.powerDisel3.setObjectName("powerDisel3")
        self.powerSolar3 = QtWidgets.QLabel(Dialog)
        self.powerSolar3.setGeometry(QtCore.QRect(200, 680, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerSolar3.setFont(font)
        self.powerSolar3.setText("")
        self.powerSolar3.setObjectName("powerSolar3")
        self.ogb5 = QtWidgets.QLabel(Dialog)
        self.ogb5.setGeometry(QtCore.QRect(260, 590, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.ogb5.setFont(font)
        self.ogb5.setObjectName("ogb5")
        self.label_22 = QtWidgets.QLabel(Dialog)
        self.label_22.setGeometry(QtCore.QRect(10, 580, 251, 51))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(Dialog)
        self.label_23.setGeometry(QtCore.QRect(20, 720, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.Price3 = QtWidgets.QLabel(Dialog)
        self.Price3.setGeometry(QtCore.QRect(420, 590, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(22)
        self.Price3.setFont(font)
        self.Price3.setText("")
        self.Price3.setObjectName("Price3")
        self.label_24 = QtWidgets.QLabel(Dialog)
        self.label_24.setGeometry(QtCore.QRect(20, 680, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_24.setFont(font)
        self.label_24.setObjectName("label_24")
        self.powerDisel1 = QtWidgets.QLabel(Dialog)
        self.powerDisel1.setGeometry(QtCore.QRect(190, 150, 411, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.powerDisel1.setFont(font)
        self.powerDisel1.setText("")
        self.powerDisel1.setObjectName("powerDisel1")
        self.Show1 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setFamily("BankGothic Lt BT")
        font.setPointSize(36)
        self.Show1.setObjectName("Show1")
        self.Show2 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setFamily("BankGothic Lt BT")
        font.setPointSize(36)
        self.Show2.setObjectName("Show2")
        self.Show3 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setFamily("BankGothic Lt BT")
        font.setPointSize(36)
        self.Show3.setObjectName("Show3")
        self.retranslateUi(Dialog)
        self.Show1.clicked.connect(self.Show11)
        self.Show2.clicked.connect(self.Show22)
        self.Show3.clicked.connect(self.Show33)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def DataSEET(self,datta):
        self.AllData = datta

    def Show11(self):
        histDat = []
        high = self.AllData[0].CAIDI
        for i in range(25):
            highh = high[i]
            for j in range(0, 10, 3):
                histDat.append(random.randint(0, j))
        Histogramm11 = plt.figure()
        plt.hist(histDat, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color='r')
        plt.xlabel("Time Hour")
        plt.ylabel("Probability %")
        plt.title("CAIDI Option 1")
        plt.grid(True)
        histDat = []
        high = self.AllData[0].SAIFI
        for i in range(25):
            highh = high[i]
            for j in range(0, 10, 3):
                histDat.append(random.randint(0, j))
        Histogramm12 = plt.figure()
        plt.hist(histDat, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color='b')
        plt.xlabel("Time Hour")
        plt.ylabel("Probability %")
        plt.title("SAIFI Option 1")
        plt.grid(True)
        plt.show()

    def Show22(self):
        histDat = []
        high = self.AllData[1].CAIDI
        for i in range(25):
            highh = high[i]
            for j in range(0, 10, 3):
                histDat.append(random.randint(0, j))
        Histogramm21 = plt.figure()
        plt.hist(histDat, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color='r')
        plt.xlabel("Time Hour")
        plt.ylabel("Probability %")
        plt.title("CAIDI Option 2")
        plt.grid(True)
        histDat = []
        high = self.AllData[1].SAIFI
        for i in range(25):
            highh = high[i]
            for j in range(0, 10, 3):
                histDat.append(random.randint(0, j))
        Histogramm22 = plt.figure()
        plt.hist(histDat, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color='b')
        plt.xlabel("Time Hour")
        plt.ylabel("Probability %")
        plt.title("SAIFI Option 2")
        plt.grid(True)
        plt.show()

    def Show33(self):
        histDat = []
        high = self.AllData[2].CAIDI
        for i in range(25):
            highh = high[i]
            for j in range(0, 10, 3):
                histDat.append(random.randint(0, j))
        Histogramm31 = plt.figure()
        plt.hist(histDat, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color='r')
        plt.xlabel("Time Hour")
        plt.ylabel("Probability %")
        plt.title("CAIDI Option 3")
        plt.grid(True)
        histDat = []
        high = self.AllData[2].SAIFI
        for i in range(25):
            highh = high[i]
            for j in range(0, 10, 3):
                histDat.append(random.randint(0, j))
        Histogramm32 = plt.figure()
        plt.hist(histDat, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], color='b')
        plt.xlabel("Time Hour")
        plt.ylabel("Probability %")
        plt.title("SAIFI Option 3")
        plt.grid(True)
        plt.show()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Option 1 /"))
        self.label_2.setText(_translate("Dialog", "Wind Power = "))
        self.label_3.setText(_translate("Dialog", "Solar Power = "))
        self.label_4.setText(_translate("Dialog", "Disel Power = "))
        self.label_5.setText(_translate("Dialog", " Price = "))
        self.label_10.setText(_translate("Dialog", "Wind Power = "))
        self.obg1.setText(_translate("Dialog", " Price = "))
        self.label_14.setText(_translate("Dialog", "Option 2 /"))
        self.label_15.setText(_translate("Dialog", "Disel Power = "))
        self.label_16.setText(_translate("Dialog", "Solar Power = "))
        self.label_18.setText(_translate("Dialog", "Wind Power = "))
        self.ogb5.setText(_translate("Dialog", " Price = "))
        self.label_22.setText(_translate("Dialog", "Option 3 /"))
        self.label_23.setText(_translate("Dialog", "Disel Power = "))
        self.label_24.setText(_translate("Dialog", "Solar Power = "))

    def ParamsSet(self,par):
        self.powerDisel1.setText(str(par[0].powerD))
        self.powerDisel2.setText(str(par[1].powerD))
        self.powerDisel3.setText(str(par[2].powerD))
        self.powerSolar1.setText(str(par[0].powerS))
        self.powerSolar2.setText(str(par[1].powerS))
        self.powerSolar3.setText(str(par[2].powerS))
        self.powerWind1.setText(str(par[0].powerW))
        self.powerWind2.setText(str(par[1].powerW))
        self.powerWind3.setText(str(par[2].powerW))
        self.Price1.setText(str(par[0].price))
        self.Price2.setText(str(par[1].price))
        self.Price3.setText(str(par[2].price))

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(531, 579)
        Dialog.setAutoFillBackground(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(310, 530, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.Run = QtWidgets.QPushButton(Dialog)
        self.Run.setGeometry(QtCore.QRect(20, 430, 281, 131))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(48)
        self.Run.setFont(font)
        self.Run.setIconSize(QtCore.QSize(100, 100))
        self.Run.setObjectName("Run")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 10, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(210, 10, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(380, 10, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(340, 40, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(340, 80, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(170, 80, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(10, 80, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(Dialog)
        self.label_12.setGeometry(QtCore.QRect(10, 40, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(Dialog)
        self.label_13.setGeometry(QtCore.QRect(170, 40, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(50, 180, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(310, 180, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(50, 270, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.probability_SAIFI = QtWidgets.QSpinBox(Dialog)
        self.probability_SAIFI.setGeometry(QtCore.QRect(310, 320, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.probability_SAIFI.setFont(font)
        self.probability_SAIFI.setObjectName("probability_SAIFI")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(310, 270, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.probability_CAIDI = QtWidgets.QSpinBox(Dialog)
        self.probability_CAIDI.setGeometry(QtCore.QRect(50, 320, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.probability_CAIDI.setFont(font)
        self.probability_CAIDI.setObjectName("probability_CAIDI")
        self.CAIDI = QtWidgets.QLineEdit(Dialog)
        self.CAIDI.setGeometry(QtCore.QRect(50, 220, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.CAIDI.setFont(font)
        self.CAIDI.setText("")
        self.CAIDI.setObjectName("CAIDI")
        self.SAIFI = QtWidgets.QLineEdit(Dialog)
        self.SAIFI.setGeometry(QtCore.QRect(310, 220, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.SAIFI.setFont(font)
        self.SAIFI.setObjectName("SAIFI")
        self.diselMin = QtWidgets.QLineEdit(Dialog)
        self.diselMin.setGeometry(QtCore.QRect(50, 40, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.diselMin.setFont(font)
        self.diselMin.setObjectName("diselMin")
        self.diselMax = QtWidgets.QLineEdit(Dialog)
        self.diselMax.setGeometry(QtCore.QRect(50, 80, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.diselMax.setFont(font)
        self.diselMax.setObjectName("diselMax")
        self.solarMax = QtWidgets.QLineEdit(Dialog)
        self.solarMax.setGeometry(QtCore.QRect(210, 80, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.solarMax.setFont(font)
        self.solarMax.setObjectName("solarMax")
        self.solarMin = QtWidgets.QLineEdit(Dialog)
        self.solarMin.setGeometry(QtCore.QRect(210, 40, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.solarMin.setFont(font)
        self.solarMin.setObjectName("solarMin")
        self.windMin = QtWidgets.QLineEdit(Dialog)
        self.windMin.setGeometry(QtCore.QRect(380, 40, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.windMin.setFont(font)
        self.windMin.setObjectName("windMin")
        self.windMax = QtWidgets.QLineEdit(Dialog)
        self.windMax.setGeometry(QtCore.QRect(380, 80, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.windMax.setFont(font)
        self.windMax.setObjectName("windMax")
        self.label_14 = QtWidgets.QLabel(Dialog)
        self.label_14.setGeometry(QtCore.QRect(10, 120, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(Dialog)
        self.label_15.setGeometry(QtCore.QRect(170, 120, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(Dialog)
        self.label_16.setGeometry(QtCore.QRect(340, 120, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.diselPrice = QtWidgets.QLineEdit(Dialog)
        self.diselPrice.setGeometry(QtCore.QRect(50, 120, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.diselPrice.setFont(font)
        self.diselPrice.setObjectName("diselPrice")
        self.solarPrice = QtWidgets.QLineEdit(Dialog)
        self.solarPrice.setGeometry(QtCore.QRect(210, 120, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.solarPrice.setFont(font)
        self.solarPrice.setObjectName("solarPrice")
        self.windPrice = QtWidgets.QLineEdit(Dialog)
        self.windPrice.setGeometry(QtCore.QRect(380, 120, 113, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.windPrice.setFont(font)
        self.windPrice.setObjectName("windPrice")
        self.stop = QtWidgets.QPushButton(Dialog)
        self.stop.setGeometry(QtCore.QRect(320, 430, 191, 91))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(28)
        self.stop.setFont(font)
        self.stop.setObjectName("stop")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(20, 400, 491, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.Run.clicked.connect(self.Runfunc)
        self.Proc = 0

    def Runfunc(self):
        mass  = {}
        mass["diselMin"] = float(self.diselMin.text())
        mass["diselMax"] = float(self.diselMax.text())
        mass["diselPrice"] = float(self.diselPrice.text())
        mass["solarMin"] = float(self.solarMin.text())
        mass["solarMax"] = float(self.solarMax.text())
        mass["solarPrice"] = float(self.solarPrice.text())
        mass["windMin"] = float(self.windMin.text())
        mass["windMax"] = float(self.windMax.text())
        mass["windPrice"] = float(self.windPrice.text())
        mass["CAIDI"] = float(self.CAIDI.text())
        mass["SAIFI"] = float(self.SAIFI.text())
        mass["probalility_CAIDI"] = float(self.probability_CAIDI.text())
        mass["probability_SAIFI"] = float(self.probability_SAIFI.text())
        print(mass)
        Data = mass
        Inp.priceW = Data["windPrice"]
        Inp.priceS = Data["solarPrice"]
        Inp.priceD = Data["diselPrice"]
        Inp.thrSAIFI = Data["SAIFI"]
        Inp.thrCAIDI = Data['CAIDI']
        Inp.probCAIDI = Data["probalility_CAIDI"] / 100
        Inp.probSAIFI = Data["probability_SAIFI"] / 100
        Inp.windLow = Data["windMin"]
        Inp.windHigh = Data["windMax"]
        Inp.sunLow = Data["solarMin"]
        Inp.sunHigh = Data["solarMax"]
        Inp.dieLow = Data["diselMin"]
        Inp.dieHigh = Data["diselMax"]
        x = bubble_sort(Inp)
        ui1.DataSEET(x)
        ui1.setupUi(Dialog1)
        ui1.ParamsSet(x)
        self.progressBar.setProperty("value", 100)
        Dialog1.show()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Run.setText(_translate("Dialog", "Run"))
        self.label.setText(_translate("Dialog", "Disel Power"))
        self.label_2.setText(_translate("Dialog", "Solar Power"))
        self.label_3.setText(_translate("Dialog", "Wind Power"))
        self.label_8.setText(_translate("Dialog", "Min"))
        self.label_9.setText(_translate("Dialog", "Max"))
        self.label_10.setText(_translate("Dialog", "Max"))
        self.label_11.setText(_translate("Dialog", "Max"))
        self.label_12.setText(_translate("Dialog", "Min"))
        self.label_13.setText(_translate("Dialog", "Min"))
        self.label_4.setText(_translate("Dialog", "CAIDI"))
        self.label_5.setText(_translate("Dialog", "SAIFI"))
        self.label_6.setText(_translate("Dialog", "Probability"))
        self.label_7.setText(_translate("Dialog", "Probability"))
        self.label_14.setText(_translate("Dialog", "Price"))
        self.label_15.setText(_translate("Dialog", "Price"))
        self.label_16.setText(_translate("Dialog", "Price"))
        self.stop.setText(_translate("Dialog", "Stop"))

    def SetText(self,Texxt):
        self.diselMin.setText(str(Texxt["diselMin"]))
        self.diselMax.setText(str(Texxt["diselMax"]))
        self.diselPrice.setText(str(Texxt["diselPrice"]))
        self.solarMin.setText(str(Texxt["solarMin"]))
        self.solarMax.setText(str(Texxt["solarMax"]))
        self.solarPrice.setText(str(Texxt["solarPrice"]))
        self.windMin.setText(str(Texxt["windMin"]))
        self.windMax.setText(str(Texxt["windMax"]))
        self.windPrice.setText(str(Texxt["windPrice"]))
        self.CAIDI.setText(str(Texxt["CAIDI"]))
        self.SAIFI.setText(str(Texxt["SAIFI"]))
        self.probability_CAIDI.setValue(Texxt["probability_CAIDI"])
        self.probability_SAIFI.setValue(Texxt["probability_SAIFI"])


def TexxtGet():
    file = {
        "diselMin": 500,
        "diselMax": 2500,
        "diselPrice": 50,
        "solarMin": 500,
        "solarMax": 2500,
        "solarPrice": 20,
        "windMin": 500,
        "windMax": 2500,
        "windPrice": 10,
        "CAIDI": 6,
        "SAIFI": 8,
        "probability_CAIDI": 5,
        "probability_SAIFI": 5
    }
    return(file)


if __name__ == "__main__":
    import sys
    AllDataGet = None
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    app1 = QtWidgets.QApplication(sys.argv)
    Dialog1 = QtWidgets.QDialog()
    ui1 = OutPutInterface()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    ui.SetText(TexxtGet())
    Dialog.show()
    sys.exit(app.exec_())
