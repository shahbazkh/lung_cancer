Requirements: 
	*Machine: Azure NC6 with TESLA K-80 GPU 
	*Python Packages: NOTE: Use python2.7
		*Required packages can be installed via `pip install -r project_code/requirements.txt'
		*Notable packages also listed blow for reference 
			-Keras (with Tensor flow as backend, CUDA framework for GPU enabled)  
			-Tensorflow   
			-dicom
			-matplotlib
			-numpy
			-pandas
			-scikit-image
			-scikit-learn
			-scipy
			-xgboost
			-opencv-python
			-mxnet
			-SimpleITK
			-hyperopt
			-zarr
	*Please refer to the following instructions for installing keras with gpu enabled tensor flow: 
		https://medium.com/@acrosson/installing-nvidia-cuda-cudnn-tensorflow-and-keras-69bbf33dce8a
	*Dataset requirements 
		-Kaggle DataScience Bowl Dataset: 
			*Download stage1.7z images from 
			 	-https://www.kaggle.com/c/data-science-bowl-2017/data
				-Recommended to place in /datadrive/data/full_data/stage1/
 			*Dowload stage1_labels.csv
				-https://www.kaggle.com/c/data-science-bowl-2017/data
				-Recommended to place in /datadrive/data
			*Downlaod stage1_solution.csv
				-https://www.kaggle.com/c/data-science-bowl-2017/data
				-Copy paste all labels in stage1_solution.csv to stage1_labels.csv
		
		-LUNA DataSet 
			*Download subset 0 to 9 from 
				-https://drive.google.com/drive/u/0/folders/0Bz-jINrxV740SWE1UjR4RXFKRm8
				-Recommended to place in /datadrive2/luna/subset/
			*Download CSV files from
				-https://drive.google.com/drive/u/0/folders/0Bz-jINrxV740SWE1UjR4RXFKRm8
				-Recommended to place in /datadrive/luna/CSVFILES/annotations.csv

1. Image Processing 
   *Folder: image_processing/ 
   *Description: Uses ideas from our research, cited in our paper to transform the raw DICOM files to a format suitable for
   	CNN.  The general process is to read the files, extract the pixel data and other metadata, transform the images,
	standardize the images, segment the lungs, and store the results.  We experimented with a lot of methods, so the
	code is configurable to output 1 or more of the processed image file formats we tested in our work.  The output of
	this process was used as an input to the Conv3d Model discussed in (2) below.
   *References: Sources are cited in the code where applicable, and in our final paper submission. 
   *Run Instructions: 
   	python ImagePreprocess.py input_dir input_csv output_dir output_size method_list

	For example, to run all of the methods we tested, I used the following command:

	python ImagePreprocess.py ../../../data/full_data/stage1 ../../../data/stage1_labels.csv ../../../output_kaggle/ \
	120,120 1,2,3,4,5,6

2.  Conv3d Model on processed images 
    *Folder: conv3d/
    *Description: Uses TensorFlow implementation to run Conv3D model processed images. Prints out logloss and other metrics  
    *References: First pass through Data w/ 3D ConvNet: https://www.kaggle.com/sentdex/data-science-bowl-2017/first-pass-through-data-w-3d-convnet
    *Run Instructions: 
	1. Set the dataset and prcessed images direcotories on the top of the script
        2. Run tensor_flow_model.py 
       
3.  Conv3d UNET 
    *Folder: conv3d_unet/
    *Description: UNET Segmentation on LUNA and then 3DConv Neural Network on Kaggle after segmenting out the nodules 
    *References: This method aims to reproduce methods by top performers in the kaggle datascience bowl: 
	-3D Segmentation U-Net's & Classification CNN: https://www.kaggle.com/c/data-science-bowl-2017/discussion/31608
	-Full Preprocessing Tutorials: https://www.kaggle.com/gzuidhof/data-science-bowl-2017/full-preprocessing-tutorial
    *Run instructions  
	1. Set the file paths for dataset in conv3d_unet/file_paths.config  
	2. Process LUNA Dataset 
		a. Run luna/image_processing/luna_3d_img_processing.py to process LUNA images 
	3. Run UNET on Processed images 
		a. luna/model/unet_train.py to train a model on processed LUNA images. This takes over 10 hours to run 
	4. Process Kaggle Dataset 
		a. kaggle/image_processing/kaggle_3d_img_processing.py to train process images 
	5. Segment Nodules by running the LUNA UNET trained model to get predictions 
		a. kaggle/segmentation/3dunet_dsb_segmentation.py to segment candidate nodules on processes images 
	6. Run classification - Train 3D CNN Classifier and get classification probabilities. Also prints metrics such as auc, precision, recall on training dataset. This step takes 8 hours to run 
		a. kaggle/classification_model/preds3d_run.py   
    *Structure 
	conv3d_unet/
		├── file_paths.config: Please read this file to set the file paths 
		├── kaggle: Folder for all code used on kaggle dataset 
		│   ├── classification_model: Folder containing code for classification using 3D CNN 
		│   │   ├── preds3d_run.py: main class to run for classification model 
		│   │   └── preds3d_utils.py: helper methods used by preds3d_run.py
		│   ├── image_processing: Folder contains code to standardize kaggle images 
		│   │   ├── kaggle_3d_img_processing.py: Main script to run to process kaggle images 
		│   │   └── kaggle_utils.py: utility methods used by kaggle_3d_img_processing.py
		│   └── segmentation
		│       └── 3dunet_dsb_segmentation.py: Run the model trained on LUNA on kaggle 
		└── luna
    			├── image_processing: Folder to process LUNA images 
    			│   ├── luna_3d_img_processing.py: Main script to process LUNA images 
    			│   └── utils_image_processing.py: utility script used by luna_3d_img_processing.py
    			└── model
        		    └── unet_train.py: Unet model to train on UNET images 

4.	Conv2d Model on processed images
    *Folder: 2dCNN/
    *Description: Uses TensorFlow implementation to run Conv2D model processed images. Generates predictions and accuracy from TensorFlow
    Only works on single iamges per the 2D implementation
    *References: First pass through Data w/ 3D ConvNet: https://www.kaggle.com/sentdex/data-science-bowl-2017/first-pass-through-data-w-3d-convnet - modified for 2D nets
    *Run Instructions: 
	1. Set the dataset and prcessed images direcotories on the top of the script
		- Set images directory to an average of slices
    2. Run 2D_average_slice_CNN.py.py 

5. Supplemental feature modeling
    *Folder: supplemental/
    *Description: Uses supplemental features extracted from the image processing step. Generates predictions and accuracy from tuned models
    *Run Instructions: 
	1. Set the dataset and prcessed images direcotories on the top of the script
    2. Run supplemental_models.py