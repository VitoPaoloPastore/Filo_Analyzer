"""    Source file name: Filo_analyzer.py    Description: empty file for installation requirements    Copyright (C) <2020>  <Vito Paolo Pastore, Simone Bianco>    This program is free software: you can redistribute it and/or modify    it under the terms of the GNU General Public License as published by    the Free Software Foundation, version 3 of the License.    This program is distributed in the hope that it will be useful,    but WITHOUT ANY WARRANTY; without even the implied warranty of    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the    GNU General Public License for more details.    You should have received a copy of the GNU General Public License    along with this program.  If not, see <https://www.gnu.org/licenses/>."""import cv2import numpy as npimport osfrom skimage.morphology import thinfrom tkinter import filedialogfrom tkinter import *from tkinter import messageboximport copyimport matplotlibmatplotlib.use("TkAgg")from matplotlib import pyplot as pltfrom scipy import ndimage as ndifrom tkinter import *import tkinterfrom matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk################################# new imports ###################################from itertools import chainfrom skimage.io import imread, imshow, imread_collection, concatenate_imagesfrom skimage.transform import resizefrom skimage.morphology import labelimport segmentation_modelsfrom segmentation_models import Unet, PSPNet, Linknet, FPNfrom itertools import chainfrom skimage.io import imread, imshow, imread_collection, concatenate_imagesfrom skimage.transform import resizefrom skimage.morphology import labelfrom tensorflow.keras.models import Model, load_modelfrom tensorflow.keras.layers import Inputfrom tensorflow.keras.layers import Dropout, Lambdafrom tensorflow.keras.layers import Conv2D, Conv2DTransposefrom tensorflow.keras.layers import MaxPooling2Dfrom tensorflow.keras.layers import concatenatefrom tensorflow.keras.callbacks import EarlyStopping, ModelCheckpointfrom tensorflow.compat.v1.keras import backend as Kfrom tensorflow.keras.optimizers import RMSpropimport tensorflow.compat.v1 as tftf.disable_v2_behaviorsession_config = tf.compat.v1.ConfigProto(    gpu_options=tf.compat.v1.GPUOptions(allow_growth=True, per_process_gpu_memory_fraction=0.6))session = tf.compat.v1.Session(config=session_config)##################################################class filopodia():    def __init__(self):        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))        CONFIG_PATH = os.path.dirname(os.path.join(ROOT_DIR, 'configuration.conf'))  # requires `import os`        class_weight = [0.2, 0.8]        loss = segmentation_models.losses.DiceLoss(class_weights=class_weight)        metric = segmentation_models.metrics.Recall()        model = load_model('model-dsbowl2018-1232.h5',                           custom_objects={'loss': loss, 'dice_loss': segmentation_models.losses.DiceLoss,                                           'recall': metric})        filename = ""        threshold_image = 35        erosion = 30        dilation = 20        filopodia_minimum_length = 10        filopodia_width_threshold = 40        gamma = 1.0        tkTop = tkinter.Tk()        already_view = 0        histogram = plt.figure(3)        al = 0        x = np.zeros((1,4))        y=np.zeros((1,4))        sigma = 1.0        checked = tkinter.IntVar()        end = 0    def thinning(self,img2):        img4 = copy.copy(img2)        img2 = thin(img2, max_iter=1)        img4[np.where(img2 == False)] = 0        return img4    def adjust_gamma(self,image, gamma=1.0):    # build a lookup table mapping the pixel values [0, 255] to    # their adjusted gamma values        invGamma = 1.0 / gamma        table = np.array([((l / 255.0) ** invGamma) * 255                          for l in np.arange(0, 256)]).astype("uint8")        # apply gamma correction using the lookup table        return cv2.LUT(image, table)    def browse_button(self):        temp = self.filename        self.filename = filedialog.askopenfilename()        if self.filename != temp:            self.hide_me(self.tkButtonCompute)        self.ROI= 0    def start(self):        plt.close("all")        self.hide_me(self.tkButtonCompute)        self.threshold_image = self.tkScale.get()        self.erosion = self.tkScale_erosion.get()        self.dilation = self.tkScale_dilation.get()        self.filopodia_width_threshold = self.tkScale_filopodia.get()        self.gamma = self.tkScale_gamma.get()        self.sigma = self.tkScale_edge.get()        thresh = self.threshold_image        self.tkScale.config(state='disabled')        filename = self.filename        img = cv2.imread(filename)        #automatic selection of cell and nuclues channel        self.shapes = np.zeros((1,np.shape(img)[2]))        for i in range(0,np.shape(img)[2]):            if cv2.countNonZero(img[:,:,i]) != 0:                a = cv2.blur(img[:,:,i],(15,15))                self.shapes[0,i] = cv2.countNonZero(a)        if self.shapes[0,0] == self.shapes[0,1] and self.shapes[0,1] == self.shapes[0,2]:            self.onlyonereplicatechannel=1        else:            self.onlyonereplicatechannel=0        self.shapes = np.argsort(self.shapes)        body =  copy.copy(img[:,:,self.shapes[0,2]])        if self.ROI == 1 :            body2 = np.zeros_like(body)            body2[int(self.Y[0, 0]):int(self.Y[3, 0]),int(self.X[0, 0]):int(self.X[3, 0])] = body[int(self.Y[0, 0]):int(self.Y[3, 0]),int(self.X[0, 0]):int(self.X[3, 0])]            body = body2        plt.imshow(body)        tempt = copy.copy(body)        self.nucleus = img[:,:,self.shapes[0,1]]        figure = plt.figure(1)        #body = cv2.medianBlur(body, 1)        body[body < 0.3 * np.mean((body))] = 0        body = self.adjust_gamma(body, gamma=self.gamma)        tempt[tempt < 0.3 * np.mean((body))] = 0        tempt = self.adjust_gamma(tempt, gamma=self.gamma)        #tempt = cv2.equalizeHist(tempt)        #body = cv2.equalizeHist(body)        result = ndi.gaussian_laplace(tempt, sigma=self.sigma)        #body[body < np.mean((body)) + 0.25 * np.std((body))] = 0        plt.subplot(221)        plt.imshow(body)        if self.automatic.get()==1 and self.checked_Triangle.get()==1:            messagebox.showerror("Threshold Selection", "Multiple threshold selected, check only one between adaptive and triangle")        if self.automatic.get()==1:            test = copy.copy(body)            test2 = copy.copy(body)            temp_fig = plt.figure()            A = plt.hist(body.ravel(), bins=256, range=(0.0, 255), fc='k', ec='k')            plt.close(temp_fig)            body = cv2.adaptiveThreshold(test, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,                                         655, 5)            body = cv2.morphologyEx(body, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))            body = ndi.binary_fill_holes(body).astype(np.uint8)            # body[body == 1] = 255            x, hierarchy = cv2.findContours(body, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)            ttttt = np.zeros_like(body)            for i in x:                mom = cv2.moments(i)                area = mom['m00']                max_area = 0                if area > 10000 and area < 2000000:                    cv2.drawContours(ttttt, [i], -1, (255, 144, 255), -1)            # cv2.imshow('a', ttttt)            body = copy.copy(ttttt)        elif self.checked_Triangle.get() == 1:            # # body = cv2.adaptiveThreshold(body, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,            # #                                              19, 2)            # body = cv2.adaptiveThreshold(test, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,            #                              1005, 25)            #            # body = cv2.morphologyEx(body, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))            test2 = copy.copy(body)            test = copy.copy(body)            temp_fig = plt.figure()            A = plt.hist(body.ravel(), bins=256, range=(0.0, 255), fc='k', ec='k')            ret, body = cv2.threshold(body, thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)            ret, body4 = cv2.threshold(test, thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)            s = A[0][int(ret):int(ret) + 12]            s[np.where(s == 0)] = np.max(s)            t = np.argmin(s) + int(ret)            ret, body = cv2.threshold(test2, t, 255, cv2.THRESH_BINARY)            body = ndi.binary_fill_holes(body).astype(np.uint8)            plt.close(temp_fig)        else:            ret, body = cv2.threshold(body, thresh, 255, cv2.THRESH_BINARY)        # aaa = ndi.binary_fill_holes(body).astype(int)        #        #        #        # body[aaa==1] = 255        self.body = body        xc = list()        yc = list()        #        xc_max = 0.0        yc_max = 0.0        x,hierarchy = cv2.findContours(body, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)        for i in x:            mom = cv2.moments(i)            area = mom['m00']            max_area = 0            if area > 1000 and area < 2000000:                # extract some features                moments = cv2.moments(i)                if moments['m00'] != 0.0:                    #     # centroid                    xc.append(str(moments['m10'] / moments['m00']))                    yc.append(str(moments['m01'] / moments['m00']))                    if area>max_area:                        max_area = area                        xc_max = (moments['m10'] / moments['m00'])                        yc_max = (moments['m01'] / moments['m00'])        if self.checked_larger.get() == 0:            xc = np.asarray(xc).astype(np.float)            yc = np.asarray(yc).astype(np.float)        else:            xc = copy.copy(xc_max)            yc = copy.copy(yc_max)        plt.subplot(222)        plt.imshow(body, alpha=1)        #plt.scatter(x=[xc], y=yc, c='r', s=40)        plt.subplot(223)        result[body == 0] = 0        plt.imshow(result)        plt.subplot(224)        nucleus = cv2.morphologyEx(body, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.erosion, self.erosion)))        nucleus = cv2.morphologyEx(nucleus, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.dilation, self.dilation)))        #nucleus = cv2.morphologyEx(body, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (self.erosion, self.erosion)))        result[nucleus!=0]=0        #a = result - nucleus        #bod = cv2.cvtColor((img[:,:,self.shapes[0,2]]),cv2.COLOR_GRAY2RGB)        #result[result>30] = 255        #result[result <= self.filopodia_width_threshold]=0        #result = self.thinning(result)        #result = cv2.morphologyEx(result, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_CROSS, (1,1)))        body = cv2.cvtColor(img[:,:,self.shapes[0,2]],cv2.COLOR_GRAY2RGB)        if self.ROI == 1:            body2 = np.zeros_like(body)            body2[int(self.Y[0, 0]):int(self.Y[3, 0]), int(self.X[0, 0]):int(self.X[3, 0])] = body[int(self.Y[0, 0]):int(                self.Y[3, 0]), int(self.X[0, 0]):int(self.X[3, 0])]            body = body2            #result = cv2.cvtColor(result,cv2.COLOR_GRAY2RGB)        x, hierarchy = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)        self.result = result        img_copy = copy.copy(img)        if self.deep.get()==1:            img = body            img = img / 255.0            im = resize(img, (288, 288), mode='constant', preserve_range=True)            im = im[:, :, 0]            im = im[np.newaxis]            im = np.reshape(im, (1, 288,288))            im2 = self.model.predict(im)            im2 = np.argmax(im2, axis=3)[0, :, :]            # img = self.adjust_gamma(img, 1.8)            # im = resize(img, (288, 288), mode='constant', preserve_range=True)            # im[np.where(im2 != 0)] = [0, 0, 255]            result2 = ndi.gaussian_laplace(tempt, sigma=self.sigma)            a, result2 = cv2.threshold(result2, 100, 255, cv2.THRESH_BINARY)            result2 = cv2.medianBlur(result2,3)            im2 = (resize(np.squeeze(im2),                          (np.shape(result2)[0], np.shape(result2)[1]),                          mode='constant', preserve_range=True))            im2[np.where(result2 == 0)] = 0            im2 = cv2.morphologyEx(im2, cv2.MORPH_ERODE,                                       cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.erosion, self.erosion)))            im2 = cv2.morphologyEx(im2, cv2.MORPH_DILATE,                                       cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.dilation, self.dilation)))            # Convert the image to gray-scale            # Find the edges in the image using canny detector            im2 = im2 * 255            a, im2 = cv2.threshold(im2, 254, 255, cv2.THRESH_BINARY)            result = im2            # Read image            # Show result            self.result = result        img = copy.copy(img_copy)        for_drawing2 = cv2.cvtColor((img[:, :, self.shapes[0, 2]]), cv2.COLOR_GRAY2RGB)        for i in x:            mom = cv2.moments(i)            area = mom['m00']            if area > self.filopodia_width_threshold and area < 200000:                # extract some features                moments = cv2.moments(i)                if moments['m00'] != 0.0:                    #     # centroid                    ellip = cv2.fitEllipse(i)                    (center, axes, orientation) = ellip                    major_axis = max(axes)                    minor_axis = min(axes)                    if np.sqrt(1 - (minor_axis * minor_axis) / (major_axis * major_axis)) > 0.7:                        cv2.drawContours(for_drawing2, [i], -1, (0, 255, 255), -1)        if self.deep.get() == 1:            for_drawing2 = result        plt.imshow(for_drawing2, cmap='inferno')        final = plt.figure(3)        plt.imshow(for_drawing2, cmap='inferno')        self.figure_result = final        self.figure = figure       # plt.imshow(result, cmap='inferno', alpha=0.8)        if self.al == 0:            if self.checked.get() == 1:                self.canvas = FigureCanvasTkAgg(self.figure_result,self.bottom_Frame)            else:                self.canvas = FigureCanvasTkAgg(self.figure,self.bottom_Frame)            self.canvas.get_tk_widget().pack(side = tkinter.BOTTOM,fill = tkinter.BOTH, expand = True)            self.al = 2        else:            self.canvas.get_tk_widget().destroy()            if self.checked.get() == 1:                self.canvas = FigureCanvasTkAgg(self.figure_result,self.bottom_Frame)            else:                self.canvas = FigureCanvasTkAgg(self.figure,self.bottom_Frame)            self.canvas.get_tk_widget().pack(side = tkinter.BOTTOM,fill = tkinter.BOTH, expand = True)        self.tkScale.config(state='normal')        self.tkButtonCompute.pack()    def __init__(self):        self.tkTop.winfo_toplevel().title("filo_analyzer")        self.left_frame = Frame(self.tkTop,                                background="light blue",                                borderwidth=5,                                relief=RIDGE,                                width=200,                                )        self.bottom_Frame = Frame(self.tkTop,                                 background="white",                                 borderwidth=0,                                 relief=RIDGE,                                 width=1000,                                 )        self.right_frame = Frame(self.tkTop,                                background="light blue",                                borderwidth=5,                                relief=RIDGE,                                width=200,                                )        self.left_frame.pack(side=LEFT, expand=NO, fill=Y)        self.bottom_Frame.pack(side=LEFT, expand=YES, fill=Y)        self.right_frame.pack(side=RIGHT, expand=NO, fill=Y)        self.tkTop.geometry('1500x1000')        self.menuBar = tkinter.Menu(self.tkTop)        self.fileMenu = tkinter.Menu(self.menuBar, tearoff=0)        # self.filemenu.add_command(label="Save",  command=donothing)        self.menuBar.add_cascade(label="File", menu=self.fileMenu)        self.fileMenu.add_command(label="Open", command=lambda: self.browse_button())        self.fileMenu.add_command(label="Open_dir_to_analyze", command=lambda: self.browse_dir())        self.fileMenu.add_command(label="Save", command=lambda: self.save())        self.tkButtonStart = tkinter.Button(self.left_frame, text="Start", command=lambda: self.start())        self.tkScale = tkinter.Scale(self.left_frame, from_=1, to=255, orient=tkinter.HORIZONTAL)        self.tkScale_erosion = tkinter.Scale(self.left_frame, from_=1, to=50, orient=tkinter.HORIZONTAL)        self.tkScale_dilation = tkinter.Scale(self.left_frame, from_=1, to=40, orient=tkinter.HORIZONTAL)        self.tkScale_filopodia = tkinter.Scale(self.left_frame, from_=1, to=100, orient=tkinter.HORIZONTAL)        self.tkScale_gamma = tkinter.Scale(self.left_frame, from_=0.1, to=5.0, orient=tkinter.HORIZONTAL, resolution = 0.1)        self.tkScale_edge = tkinter.Scale(self.left_frame, from_=0.5, to=5.0, orient=tkinter.HORIZONTAL, resolution = 0.1)        self.tkScale.set(150)        self.tkScale_erosion.set(20)        self.tkScale_dilation.set(20)        self.tkScale_filopodia.set(40)        self.automatic = IntVar()        self.checked_larger = IntVar()        self.checked_Triangle = IntVar()        self.deep = IntVar()        self.tkScale_gamma.set(1.0)        self.tkScale_edge.set(1.0)        self.automatic_threshold = tkinter.Checkbutton(self.left_frame, text="Automatic threshold (Adaptive)",                                                       variable= self.automatic)        self.automatic_threshold.pack()        self.triang = tkinter.Checkbutton(self.left_frame, text="Automatic threshold (Triangle)",                                                       variable=self.checked_Triangle)        self.triang.pack()        self.onlylargerobject = tkinter.Checkbutton(self.left_frame, text="Consider only larger object", variable=self.checked_larger)        self.onlylargerobject.pack()        self.deeplearning = tkinter.Checkbutton(self.left_frame, text="Deep_learning prediction",                                                    variable=self.deep)        self.deeplearning.pack()        self.label = tkinter.Label(self.left_frame, text="threshold for image edge extraction")        self.label.pack()        self.tkScale.pack()        self.label2 = tkinter.Label(self.left_frame, text="erosion factor")        self.label2.pack()        self.tkScale_erosion.pack()        self.label3 = tkinter.Label(self.left_frame, text="dilation factor")        self.label3.pack()        self.tkScale_dilation.pack()        self.label4 = tkinter.Label(self.left_frame, text="filopodia width factor")        self.label4.pack()        self.tkScale_filopodia.pack()        self.label5 = tkinter.Label(self.left_frame, text="gamma for highlight filopodia")        self.label5.pack()        self.tkScale_gamma.pack()        self.label6 = tkinter.Label(self.left_frame, text="sigma for edge detection")        self.label6.pack()        self.tkScale_edge.pack()        self.onlyresult = tkinter.Checkbutton(self.left_frame, text="Show only the final figure", variable=self.checked)        self.onlyresult.pack()        self.tkButtonStart.pack()        self.tkButtonROI = tkinter.Button(self.left_frame, text="Select ROI", command=lambda: self.getROI())        self.tkButtonROI.pack()        self.tkButtonCompute = tkinter.Button(self.left_frame, text="Compute", command=lambda: self.extract_statistics())        self.labelr1 = tkinter.Label(self.right_frame, text="Result",background = 'dark green')        self.labelr2 = tkinter.Label(self.right_frame, text="Average distance per cell",background = 'light green')        self.labelr22 = tkinter.Label(self.right_frame, text="",background = 'dark green')        self.labelr3 = tkinter.Label(self.right_frame, text="Average Number filopodia per cell",background = 'light green')        self.labelr33 = tkinter.Label(self.right_frame, text="",background = 'dark green')        self.labelr4 = tkinter.Label(self.right_frame, text="Average diameter filopodia",background = 'light green')        self.labelr44 = tkinter.Label(self.right_frame, text="",background = 'dark green')        self.labelr4.config(font=("Courier", 20))        self.labelr44.config(font=("Courier", 20))        self.labelr33.config(font=("Courier", 20))        self.labelr3.config(font=("Courier", 20))        self.labelr22.config(font=("Courier", 20))        self.labelr2.config(font=("Courier", 20))        self.labelr1.config(font=("Courier", 20))        self.tkTop.protocol("WM_DELETE_WINDOW", self.on_closing)    def hide_me(self,widget):            widget.pack_forget()    # x2 is the list of x centroid    # y2 is the list of the y centroid    # x1 is the filopodia centroid    def retrieve_distance_distribution (self,x1,y1,x2,y2):        dist = np.zeros((1,len(x2)))        for i in range(0, len(x2)):            dist[0,i] = np.sqrt((x1-x2[i])**2 + (y1-y2[i])**2)        sorted_dist = np.sort(dist)        centroid = [x2[np.argmin(dist)],y2[np.argmin(dist)]]        angle = np.arctan((y1 - centroid[1])/(x1 - centroid[0]))        if (x1-centroid[0])<0 :            angle = np.arctan((centroid[1] - y1) / (centroid[0] - x1)) + np.pi        angle = angle + np.pi/2        return np.min(dist),angle    def on_closing(self):        if messagebox.askokcancel("Quit", "Do you want to quit?"):            self.tkTop.destroy()    def startloop(self):        self.tkTop.config(menu=self.menuBar)        tkinter.mainloop()    def save(self):        f = filedialog.asksaveasfilename()        if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".            return        self.figure_result.savefig(f + '_complete')        self.histogram.savefig(f + '_histogram')        self.figure.savefig(f + '_final')        text_file = open(f + 'writer.txt', "w")        text_file_single = open(f + 'single_length.txt', "w")        for i in self.txtlist:            text_file.write(i + "\n")        text_file.close()        for i in self.filopodia_single:            text_file_single.write(str(i) + "\n")        text_file_single.close()    def extract_statistics(self):        # filopodia single length extraction, as requested        self.filopodia_single = list()        plt.close("all")        if cv2.countNonZero(self.nucleus) !=0 and self.onlyonereplicatechannel==0:            ret, nucl = cv2.threshold(self.nucleus, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)        else:            nucl = self.body        x, hierarchy = cv2.findContours(nucl, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)        num_filopodia = 0        length =0        diameter_eq = 0        diameter_eq2 = 0        distance = 0        angles = np.zeros((24,1))        xc = list()        num_cell = 0        yc = list()        for i in x:            mom = cv2.moments(i)            area = mom['m00']            if area > 5000 and area < 2000000:                # extract some features                moments = cv2.moments(i)                if moments['m00'] != 0.0:                    #     # centroid                    xc.append(moments['m10'] / moments['m00'])                    yc.append(moments['m01'] / moments['m00'])                    num_cell+=1        if self.deep:            self.result = self.result.astype(np.uint8)        x2, hierarchy = cv2.findContours(self.result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)        for i in x2:            moments = cv2.moments(i)            area = moments['m00']            if area > 10 and area < 200000:                if cv2.contourArea(i)>10:                    if moments['m00'] != 0.0:                        #     # centroid                        x = (moments['m10'] / moments['m00'])                        y = (moments['m01'] / moments['m00'])                    ellip = cv2.fitEllipse(i)                    (center, axes, orientation) = ellip                    major_axis = max(axes)                    minor_axis = min(axes)                    if np.sqrt(1 - (minor_axis * minor_axis) / (major_axis * major_axis)) > 0.7:                        num_filopodia += 1                        length += cv2.arcLength(i,True)                        diameter_eq += max(axes)                        self.filopodia_single.append( max(axes))                        diameter_eq2 += min(axes)                        dist,angle = self.retrieve_distance_distribution(x,y,xc,yc)                        distance += dist                        if angle != 2*np.pi:                            angles[int(12 * angle/np.pi),0] +=1                        else:                            angles[24,0] +=1        distance = distance/num_filopodia        diameter_eq = diameter_eq/num_filopodia        diameter_eq2 = diameter_eq2/num_filopodia        num_filopodia = num_filopodia/num_cell        figg =  plt.figure(2)        y_pos = np.arange(24,dtype = float)        y_pos2 = np.arange(24,dtype = float)        for i in range (0,24):             y_pos2[i]= angles[i]        plt.bar(y_pos,y_pos2, align='center',width = 1, edgecolor= 'k',color= 'b')        plt.xlabel('Quadrant')        plt.ylabel('Frequency')        plt.title('Filopodia Distribution')        self.histogram = figg        self.txtlist = list()        self.txtlist.append('average distance per cell = ' + str(distance)[0:5])        self.txtlist.append('average number of filopodia per cell = ' + str(num_filopodia))        self.txtlist.append('average lenght per cell = ' + str(diameter_eq)[0:5])        self.txtlist.append('average diameter per cell = ' + str(diameter_eq2)[0:5])        for ad in range (0,24):            self.txtlist.append(str(angles[ad].max()))        if self.al == 2:            try:                self.canvas2.get_tk_widget().destroy()            except:                pass            self.canvas2 = FigureCanvasTkAgg(self.histogram ,self.right_frame)            self.labelr1.pack()            self.labelr2.pack()            self.labelr22['text'] = str(distance)[0:5]            self.labelr22.pack()            self.labelr3.pack()            self.labelr33['text'] = str(num_filopodia)            self.labelr33.pack()            self.labelr4.pack()            self.labelr44['text'] = str(diameter_eq)[0:5]            self.labelr44.pack()            self.canvas2.get_tk_widget().pack(side = tkinter.BOTTOM, expand = False)    def getROI(self):        plt.close("all")        #root = self.tkTop        #root.bind('<Button 1>', self.motion)        self.fig = plt.figure()        self.met = self.fig.canvas.mpl_connect('button_press_event',self.motion)        plt.ion()        img = cv2.imread(self.filename)        plt.imshow(img[:,:,self.shapes[0,2]])        self.x = np.zeros((2,1))        self.y = np.zeros((2,1))    def motion(self,event):            x1, y1 = event.xdata, event.ydata            self.x[self.end] = x1            self.y[self.end] = y1            self.end += 1            if self.end ==2:                self.end= 0                x = np.zeros((4, 1))                y = np.zeros((4, 1))                y[3, 0] = np.max(self.y)                x[3, 0] = self.x[np.argmax(self.y)]                temp = np.argmax(self.y)                self.x = np.delete(self.x, temp)                self.y = np.delete(self.y, temp)                x[0, 0] = np.max(self.x)                y[0, 0] = self.y[np.argmax(self.x)]                temp = np.argmax(self.y)                temp = np.argmax(self.x)                y[1, 0] = y[0,0]                x[1, 0] = x[3,0]                x[2, 0] = x[0,0]                y[2, 0] = y[3,0]                self.end = 0                self.x = np.zeros((2,1))                self.y = np.zeros((2,1))                img = cv2.imread(self.filename)                #img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)                for_drawing =copy.copy(img)                cv2.line(for_drawing, (int(x[2]), int(y[2])), (int(x[3]), int(y[3])), thickness=3, color=(0, 255, 255))                cv2.line(for_drawing,(int(x[2]),int(y[2])),(int(x[0]) ,int(y[0])),thickness=3,color = (0,255,255))                cv2.line(for_drawing, (int(x[1]), int(y[1])), (int(x[0]), int(y[0])), thickness=3, color=(0, 255, 255))                cv2.line(for_drawing,(int(x[3]),int(y[3])),(int(x[1]) ,int(y[1])),thickness=3,color = (0,255,255))                #self.tkTop.unbind('<Button 1>', self.motion)                #temp_image[[x[3,0]:x[0,0]],y[0,0]:y[3,3]] = self.body[[x[3,0]:x[0,0]],y[0,0]:y[3,3]]                temp_image  = np.zeros_like(self.body)                plt.imshow(for_drawing)                self.ROI = 1                self.X = x                self.Y = y                plt.ioff()                self.fig.canvas.mpl_disconnect(self.met)filop = filopodia()filop.startloop()