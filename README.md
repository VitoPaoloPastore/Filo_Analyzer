# Filo_Analyzer

Filo_Analyzer: a toolbox to provide cell filopodia detection and analysis 

## Introduction
Filo_Analyzer is a python Toolbox to provide image processing- and deep-learning- based detection and analysis of cell filopodia.

## Installation 

To install Filo_Analyzer, you can use:

**pip install -e git+https://github.com/VitoPaoloPastore/Filo_Analyzer.git#egg=Filo_Analyzer**

### Deep learning Efficient Net segmentation model download

The model file has been uploaded using git lfs (https://git-lfs.github.com/). To correctly download the model and use it for prediction,
please download the file "model-dsbowl2018-1232.h5" from the folder Model in this repository, and copy and paste in the model directory
of your local repository (usually, *users/user_name/src/Filo_Analyzer/Model*).

### Operative System supported

Filo_Analyzer is a multi-platform toolbox, it is compatible and been tested on Ubuntu, Windows and MacOS.

### Running Filo_Analyzer

To run Filo_Analyzer, simply open python and use the following lines of code:

```
From Filo_Analyzer import Filo_analyzer

```

Filo_Analyzer's GUI will automatically pop-up. 

## Main Graphical User Interface (GUI)

Fig.1 shows Filo_Analyzer's GUI. 


![FIG1](https://user-images.githubusercontent.com/51142446/111635111-75535700-87f7-11eb-99a3-70c7439d8cb4.PNG)

*Figure 1. Filo Analyzer GUI. Red rectangle: thresholding tools, black rectangle: image processing tools, blue rectangle: pre-processing tools, orange rectangle: select the region of interest, purple rectangle: deep learning-based segmentation*

### Detailed Buttons description

#### Preprocessing the image 

##### Region Of Interest (ROI) selection 
The button indicated with the orange box in Fig.1 can be used to select a region of interest in the image. Up to now, we only offer rectangular ROIs. The user will simply click on the left top vertex and on the right bottom one, and the ROI will be draw and extracted. The ROI extraction can be particularly indicated when light condition is not optimal, the cell appears quite different from the background so to avoid consequent thresholding accuracy deterioration. It may be not necessary if you are using deep-learning based segmentation.



##### Gamma correction
Gamma correction can be used to highlight the filopodia when image contrast is not high enough. The button in blue square Fig.1 can be used to set the value of the gamma parameter. 


##### Thresholding procedure



Filo Analyzer offers 3 different thresholding procedures up to now (Red rectangle Fig. 1). Please, check the option correspondent to the desired thresholding algorithm. The first implemented one is a manual hard thresholding. A scale button allows to set the hard threshold value (in pixel intensity). Move this button to get the best possible segmentation (ideally, the cell and the filopodia should be both well distinguishable in the segmented binary image). 
A second possibility is to set an automatic threshold, which is based either on the triangle thresholding procedure or on the adaptive thresholding algorithm, where the hard threshold is automatically computed from the gray-values histogram. Ideally, one could try the automatic approach, and, if the segmentation accuracy is not high enough, apply a manual thresholding fine tuning the threshold. Fig 2A-B show an example of a correct and highly accurate segmentation. Finally, Filo_Analyzer's implement a deep learning-based segmentation algorithm.
 
##### Model

In the folder Model in this repository, the user can find a pre-trained model on filopodia images. The model is a LinkNet with  EfficientNetb1 (https://arxiv.org/abs/1905.11946) backbone, pre-trained on ImageNet to improve generalization. The network has been implemented using the library *segmentation_models* (https://github.com/qubvel/segmentation_models), and trained on 99 filopodia images. 

![af_final](https://user-images.githubusercontent.com/51142446/111639468-94ec7e80-87fb-11eb-88b2-4c8552eb3c50.png)

Fig2. Example of Filo_Analyzer filopodia analysis. A fluorescence cell image. B cell segmentation. C Laplacian of Gaussians (LoG) results. D detected filopodia. 

##### Filopodia detection refinement: Erosion, dilation and sigma parameter

Dilation and erosion can be used to improve the fine details segmentation of the images. In fact, it is fundamental that the filopodia survive the segmentation process, otherwise they will be lost and not detected in the final image. Use the button indicated in the yellow rectangle of Fig.1 to set them. 
**important: if you are running deep learning-based segmentation, please set Erosion and dilation to the minimum value (i.e., 1)**. 

Then, you can change this value to obtain better detection in post-processing. 
The Sigma parameter in edge detection can be used to eliminate false positives, the higher the sigma, the lower the number of detected filopodia. The filopodia width factor is the threshold applied after contour detection for filopodia, on the minimum area for each of the detected filopodia. The higher the width factor, the higher the area detection accuracy (but some filopodia could be no more detected). 

##### Statistics computation 

![FIG2](https://user-images.githubusercontent.com/51142446/111640172-37a4fd00-87fc-11eb-9f41-afb9d91798bf.PNG) 

Fig3. The compute button appears after filopodia detection has been performed 

When the user is satisfied with the segmentation results, it is possible to extract few parameters from the analysis. In particular, the output consists of two text files. 
File 1:
-	Detected Filopodia single length (i.e., a list of all detected filopodia lengths, separeted). 
File 2:
 - 	average distance per cell; 
 - 	average number of filopodia per cell;
 -	average lenght per cell;
 -	average diameter per cell;
 - 	Histogram reporting the number of filopodia per each radiant with a step of 15 degrees. 
