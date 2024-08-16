import cv2
import numpy as np
from math import sqrt, atan2, pi

class DegreeHistgram:
    def __init__(self):
        self.dlbl = None
        self.Rpt = None
        self.Lpt = None
        self.Rmax = 0
        self.Lmax = 0
        self.lv = None
        self.tv = None
        self.maxValueP = None

    def getDistance(self, x, y, x2, y2):
        distance = sqrt((x2 - x) * (x2 - x) + (y2 - y) * (y2 - y))
        return distance

    def histgramMethodUzGray(self, lbl, c, s, e, l, res):
        cols = lbl.shape[1]
        rows = lbl.shape[0]

        if c[0] >= cols:
            print("正しく円が検出できていない(大きい）")
            return 0

        if c[1] >= rows:
            print("正しく円が検出できていない(大きい)")
            return 0

        self.dlbl = lbl.copy()
        Llabel = lbl[0:c[1], 0:c[0]]
        Rlabel = lbl[0:c[1], c[0]:cols]

        for row in range(Rlabel.shape[0]):
            for col in range(Rlabel.shape[1]):
                if Rlabel[row, col] == 255:
                    if row > self.Rmax:
                        self.Rmax = row
                        self.Rpt = (col, row)

        self.Rpt = (self.Rpt[0] + c[0], self.Rpt[1] + c[1])

        for row in range(Llabel.shape[0]):
            for col in range(Llabel.shape[1]):
                if Llabel[row, col] == 255:
                    if row > self.Lmax:
                        self.Lmax = row
                        self.Lpt = (col, row)

        self.Lpt = (self.Lpt[0], self.Lpt[1] + c[1])

        calc_hist = np.zeros((360, 360), dtype=np.uint8)
        draw_hist = np.zeros((360, 360), dtype=np.uint8)
        buf = np.zeros(360, dtype=np.int32)

        self.lv = np.array([-c[0], -c[1]])
        for row in range(rows):
            for col in range(cols):
                if lbl[row, col] == 255:
                    self.tv = np.array([col - c[0], row - c[1]])
                    inner = np.dot(self.lv, self.tv)
                    cross = np.cross(self.lv, self.tv)
                    sita = atan2(cross, inner)
                    radian = (sita * 180.0 / pi) if sita >= 0 else (sita + (2 * pi)) * 180.0 / pi
                    buf[int(radian)] += 3

        maxrad = 0
        tmpbuf = 0
        for i in range(360):
            if buf[i] >= calc_hist.shape[0]:
                buf[i] = calc_hist.shape[0] - 1
            if buf[i] > tmpbuf:
                tmpbuf = buf[i]
                maxrad = i
            calc_hist[buf[i], i] = 255
            if buf[i] > 0:
                cv2.line(draw_hist, (i, buf[i]), (i, 0), (255, 255, 255), 1, cv2.LINE_4)

        maxp = 0
        sminrad = 1000
        eminrad = 1000
        maxminrad = 1000
        for row in range(rows):
            for col in range(cols):
                if lbl[row, col] == 255:
                    self.tv = np.array([col - c[0], row - c[1]])
                    inner = np.dot(self.lv, self.tv)
                    cross = np.cross(self.lv, self.tv)
                    sita = atan2(cross, inner)
                    radian = (sita * 180.0 / pi) if sita >= 0 else (sita + (2 * pi)) * 180.0 / pi
                    if abs(radian - maxrad) < maxminrad:
                        maxminrad = abs(radian - maxrad)
                        self.maxValueP = (col, row)

        if self.Rpt[0] < self.Lpt[0]:
            self.Rpt = (self.Rpt[0] + 1, self.Rpt[1])
            self.Lpt = (self.Lpt[0] - 1, self.Lpt[1])
            s[0], s[1] = self.Rpt #FIXME?
            e[0], e[1] = self.Lpt
        else:
            self.Rpt = (self.Rpt[0] + 1, self.Rpt[1])
            self.Lpt = (self.Lpt[0] - 1, self.Lpt[1])
            #e[0], e[1] = self.Rpt "append"って一回でいいの？
            e.append(self.Rpt)
            
            #s[0], s[1] = self.Lpt
            s.append(self.Rpt)
                       

        dline = self.dlbl
        #l[0], l[1] = self.maxValueP
        l.append(self.maxValueP)
        res = draw_hist

        cv2.line(lbl, c, (l[0]), 200, thickness=2)

        return 0