# Importing dependancies
import cv2
import qrcode
import datetime
import pandas as pd
from records import records
from pyzbar.pyzbar import ZBarSymbol
from pyzbar.pyzbar import decode

class QR_GEN():
    def __init__(self, names_csv):
        self.record = []
        self.qr_list = []
        self.names_csv = names_csv
        self.df = pd.read_csv(self.names_csv)

    def createQrCode(self, save=False):
        df = pd.read_csv(self.names_csv)

        for index, values in df.iterrows():
            name = values["Name"]
            roll = values["Roll"]

            data = f"{name} {roll}"
            self.record.append(data)

            image = qrcode.make(data)

            self.qr_list.append(f"{roll}_{name}.jpg")

            # Saving the codes to <QRs> directory
            if save:
                image.save(f"QRs/{roll}_{name}.jpg")
        return self.record

    def name_col_check(self):
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")

        self.df = pd.read_csv(self.names_csv)
        if date not in self.df.columns:
            self.df.insert(2, column=date, value="A")
            self.df.to_csv('output.csv', index=False)

        return date

    def qr_check(self, img):
        # date = self.name_col_check()
        # ------------
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")
        if date not in self.df.columns:
            self.df.insert(2, column=date, value="A")
            self.df.to_csv('output.csv', index=False)
        # ------------
        if decode(img, symbols=[ZBarSymbol.QRCODE]):
            for qr in decode(img, symbols=[ZBarSymbol.QRCODE]):
                myData = qr.data.decode('utf-8')

                scanedname, scanedroll = myData.split(" ")

                if myData in records:  # Check if the student is actually listed in records
                    print(f"Good morning, Your attendance has been marked {scanedname}")
                    # df = pd.read_csv('output.csv')

                    self.df = pd.read_csv('output.csv')

                    pos = self.df[self.df['Name'] == scanedname].index.values
                    self.df.loc[pos[0], date] = "P"
                    # print(self.df.loc[pos[0], date])

                    self.df.to_csv('output.csv', index=False)

def main():
    gen = QR_GEN("names.csv")
    url = "http://192.168.0.110:8080/video"
    cap = cv2.VideoCapture(url)
    while True:
        res, img = cap.read()
        img = cv2.resize(img, (640, 480))
        gen.qr_check(img)

        cv2.imshow("Webcam", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

if __name__ == "__main__":
    main()
