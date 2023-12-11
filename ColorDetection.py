import cv2
import numpy as np
import glob

def nothing(x):
    pass

def initializeTrackbars():
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Pict", "Trackbars", 0,7, nothing)
    cv2.createTrackbar("Threshold1", "Trackbars", 182,255, nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("iterationsDil", "Trackbars", 1, 10, nothing)
    cv2.createTrackbar("iterationsEr", "Trackbars", 1, 10, nothing)

# Create Trackbar to control treshhold and images
def valTrackbars():
    n = cv2.getTrackbarPos("Pict", "Trackbars")
    Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    it1 = cv2.getTrackbarPos("iterationsDil", "Trackbars")
    it2 = cv2.getTrackbarPos("iterationsEr", "Trackbars")
    src = Threshold1,Threshold2,it1,it2,n
    return src

# To reorder detected corner point coordinate
def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] =myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    return myPointsNew

# Finding the color tags based on the area
def FindTag(contours):
    Points = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if int(area) in range(170,180) or int(area) in range(500,510)\
            or int(area) in range(5300,5400) or int(area) in range(1400,1500)\
            or int(area) in range(3000,3300) or int(area) in range(1500,1600)\
            or int(area) in range(3000,3300) or int(area) in range(1600,1700):
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.03 * peri,True)
            for i in approx:
                x, y = i.ravel()
                Points.append(np.array([x,y]))
    return Points

initializeTrackbars()
Tupian = glob.glob('ObjectWithTag2/*.jpg')
print(Tupian)

while True:
    num = valTrackbars()
    n = num[4]
    img = cv2.imread(Tupian[n])
    img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)

    width = img.shape[1]
    height = img.shape[0]

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(7,7),1)

    thres=valTrackbars()
    canny = cv2.Canny(blur,thres[0],thres[1])

    kernel = np.ones((5,5))
    Dilation = cv2.dilate(canny,kernel,iterations = thres[2])
    canny = cv2.erode(Dilation,kernel,iterations= thres[3])
    
    imgContours = img.copy()
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 2)
    point = FindTag(contours)
    
    grays = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
    cannys = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)
    row1 = np.concatenate((img,grays),axis = 1)
    row2 = np.concatenate((cannys,imgContours),axis = 1)
    images = np.concatenate((row1, row2))

    cv2.imshow("Finding Tag",images)

    # Mengetahui bentuk yang ditemukan berupa kotak dengan melihat besar array point
    if np.size(point) == 8 :
        # Melakukan penataan ulang dari titik sudut yang didapat
        pointo = reorder(np.array(point))

        # Melakukan Penggambaran titik sudut yang sudah di tata ulang
        imgTag = img.copy()
        cv2.drawContours(imgTag, pointo, -1, (0, 255, 0), 3)
        
        # Menggambarkan Garis Tepi Hanya pada Color Tag
        imgLine = img.copy()
        cv2.line(imgLine, (pointo[0][0][0], pointo[0][0][1]), (pointo[1][0][0], pointo[1][0][1]), (0, 69, 255), 2)
        cv2.line(imgLine, (pointo[1][0][0], pointo[1][0][1]), (pointo[3][0][0], pointo[3][0][1]), (0, 69, 255), 2)
        cv2.line(imgLine, (pointo[3][0][0], pointo[3][0][1]), (pointo[2][0][0], pointo[2][0][1]), (0, 69, 255), 2)
        cv2.line(imgLine, (pointo[2][0][0], pointo[2][0][1]), (pointo[0][0][0], pointo[0][0][1]), (0, 69, 255), 2)

        # Mempersiapkan Matriks Transform
        # Nilai sudut yang didapatkan sebelumnya
        pts1 = np.float32(pointo)                                       
        # Titik - titik baru dengan ukuran sesuai gambar terbaca
        pts2 = np.float32([[0,0],[width,0],[0, height],[width,height]]) 
        # Mendapatkan transformasi matrix
        matrix = cv2.getPerspectiveTransform(pts1, pts2)                 

        # Melakukan transformasi perspektif gambar dari titik awal ke titik baru
        imgWarpColored = cv2.warpPerspective(imgTag, matrix, (width,height))

        # Melakukan perubahan warna dari BGR menjadi HSV untuk melakukan masking warna
        hsv1 = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2HSV)
        
        # Melakukan Masking warna hijau pada domain HSV
        lowerGreen = np.array([30, 52, 72])     # Range bawah warna hijau domain HSV
        upperGreen = np.array([90, 255, 255])   # Range atas warna hijau domain HSV
        
        # Melakukan masking/segmentasi warna pada range atas bawah hijau
        Green_mask = cv2.inRange(hsv1, lowerGreen, upperGreen) 

        # Menghitung banyak hijau pada sisi kiri gambar color Tag
        LeftGreen = Green_mask[: , 0:int(width/2)]      

        # Menghitung banyak hijau pada sisi kanan gambar color Tag
        RightGreen = Green_mask[: , int(width/2):width]

        # Membandingkan selisih warna hijau pada sisi kiri dan kanan
        if abs(int(RightGreen.sum())-int(LeftGreen.sum())) > 450000:
            # Melakukan pemutaran ke kiri 90° pada gambar 
            imgWarpColored = cv2.rotate(imgWarpColored,cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Mengatur ulang lebar dan tinggi agar sesuai dengan gambar asli
            imgWarpColored = cv2.resize(imgWarpColored, (width,height))

            # Melakukan perubahan domain warna dari BGR menjadi HSV
            hsv1 = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2HSV)
            
            #Melakukan masking warna hijau pada domain HSV
            lowerGreen = np.array([30, 52, 72])
            upperGreen = np.array([90, 255, 255])
            Green_mask = cv2.inRange(hsv1, lowerGreen, upperGreen)

            # Menghitung warna hijau di sisi atas gambar
            UpGreen = Green_mask[0:int(height/2) , :]

            # Menghitung warna hijau di sisi bawah gambar
            LowGreen = Green_mask[int(height/2):height , :]

            # Memeriksa apakah sisi bawah memiliki kadar hijau lebih banyak daripada sisi atas
            if LowGreen.sum() > UpGreen.sum():

                # Melakukan pembalikkan gambar (Atas menjadi bawah dan sebaliknya)
                imgWarpColored = cv2.flip(imgWarpColored,0)

            else: pass # Bila tidak maka dilewati
        else: pass # Bila tidak maka dilewati

        # Melakukan perubahan domain warna dari BGR menjadi HSV
        hsv2 = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2HSV)
        
        lowerRed1 = np.array([0, 100, 20]) # Menentukan rentang bawah dari warna merah domain HSV 
        upperRed1 = np.array([10, 255, 255]) # Menentukan rentang atas dari warna merah domain HSV

        # Melakukan segmentasi warna merah bawah (0° - 10°)
        low_red_mask = cv2.inRange(hsv2, lowerRed1, upperRed1)

        # Menentukan rentang bawah dan atas dari warna merah dengan nilai H berbeda
        lowerRed2 = np.array([160,100,20])
        upperRed2 = np.array([179,255,255])

        # Melakukan segmentasi warna merah atas (160° - 180°)
        upper_red_mask = cv2.inRange(hsv2, lowerRed2, upperRed2)

        # Menggabungkan segmentasi merah 0° - 10° dan 160° - 180°
        full_mask_red = upper_red_mask + low_red_mask

        # Melakukan Pencarian dan Menggambar contour lingkaran merah
        imgtest = imgWarpColored.copy() 
        contours, hierarchy = cv2.findContours(full_mask_red,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) 
        cv2.drawContours(imgtest, contours, -1, (0, 255, 0), 5)

        center = []
	  # Mencari titik tengah (Centroid) lingkaran merah 
        for cnt in contours:
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                pass
            else:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.circle(imgtest, (cx, cy), 2, (255, 255, 255), -1)
                center.append(np.array([cx,cy]))
        
  # Menata ulang titik centroid lingkaran agar index 0 terisi centroid lingkaran kiri
        if np.size(center) == 4:
            if center[1][0] < center[0][0]:
                cent_temp = center[1]
                center[1] = center[0]
                center[0] = cent_temp

        imgClass = imgLine.copy()

        # Menginisalisasi letak text
        pos = pointo[0].ravel() - 10
        pos[0] = pos[0] - 15

        # Klasifikasi lingkaran merah kiri dan kanan bila sejajar atau memiliki nilai y yang mirip
        if abs(center[0][1] - center[1][1]) < 10:

            # Bila letak lingkaran merah berada di bagian atas
            if center[0][1] in range(int(height/8),int(height/3)):
                imgClass = cv2.putText(imgClass, 'PC', pos, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)

            # Bila letak lingkaran merah berada di bagian tengah
            elif center[0][1] in range(int(height/3),int(4*height/6)):
                imgClass = cv2.putText(imgClass, 'Meja', pos, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)
            
            # Bila letak lingkaran merah berada di bagian bawah
            else:
                imgClass = cv2.putText(imgClass, 'Keyboard', pos, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)
        
        # Klasifikasi bila nilai sumbu y lingkaran merah di kanan lebih rendah daripada di kiri
        elif center[1][1] - center[0][1] > 0:

            # Bila letak lingkaran merah kanan berada di bagian bawah
            if center[1][1] in range(int(4*height/6),int(height)):
                imgClass = cv2.putText(imgClass, 'Papan', pos, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)
            
            # Bila letak lingkaran merah kanan berada di bagian tengah
            if center[1][1] in range(int(height/3),int(4*height/6)):
                imgClass = cv2.putText(imgClass, 'Laptop', pos, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)

# Klasifikasi bila nilai sumbu y lingkaran merah di kanan lebih besar daripada di kanan
        else:
		# Segmentasi Lingkaran Biru 
            lowerBlue = np.array([94,80,2])
            upperBlue = np.array([126,255,255])
            blue_mask = cv2.inRange(hsv2, lowerBlue, upperBlue)
            
            contours, hierarchy = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) 
            cv2.drawContours(imgtest, contours, -1, (0, 255, 0), 5)

            center2 = []
            for cnt in contours:
                area2 = cv2.contourArea(cnt)
                if int(area2) > 5000 and int(area2) < 6200:
                    M = cv2.moments(cnt)
                    if M['m00'] == 0:
                        pass
                    else:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        cv2.circle(imgtest, (cx, cy), 2, (255, 255, 255), -1)
                        center2.append(np.array([cx,cy]))
            
            if np.size(center2) == 4:
                if center2[1][0] < center2[0][0]:
                    cent_temp2 = center2[1]
                    center2[1] = center2[0]
                    center2[0] = cent_temp2
            
            # Bila letak lingkaran biru kiri berada di bagian atas
            if center2[0][1] in range(int(height/8),int(height/3)):
               imgClass = cv2.putText(imgClass, 'Monitor', (pos[0]-60,pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)
         
     # Bila letak lingkaran biru kiri tidak berada di bagian atas
            imgClass = cv2.putText(imgClass, 'Kursi', pos, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 69, 255), 2, cv2.LINE_AA)

        row1warp = np.concatenate((imgTag,imgWarpColored),axis = 1)
        row2warp = np.concatenate((imgtest,imgClass),axis = 1)
        AllWarp = np.concatenate((row1warp,row2warp))
        cv2.imshow("Tag Detection",AllWarp)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
