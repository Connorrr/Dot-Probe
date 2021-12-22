# TobiiEyetrackerAnalysis
Python program that takes the output of an Open Sesame Project using the tobii eyetracking plugin to refine relevant data.  The example OpenSesamy project can be used to generate raw data that will be interpreted by the Analysis software.

![image3](https://user-images.githubusercontent.com/7636403/147014640-b31ea7c9-bf38-43f6-b5ad-84d92b00a138.gif)

Areas of intrest are defined using a click and drag tool.

![image4](https://user-images.githubusercontent.com/7636403/147014703-214eb2a0-a979-47d7-ba52-9de6a99d2e32.gif)

A variable fixation size can be used but defailts to the size outlined in the raw eyetracking data.

![image5](https://user-images.githubusercontent.com/7636403/147014793-da1f15ca-b492-4612-8ebc-3a63e3fdb64f.gif)

The gaze points are plotted on top of stimulus images and fixations are displayed with a white circle.

![image6](https://user-images.githubusercontent.com/7636403/147014889-671b63cc-459f-4c12-bfda-82fb0a57f9a4.gif)

An output file is generated that refines hte original gaze point data file down to information about each area of intrest.  For each  trial there is a value for first fixations, total number of fixations and number of fixations for each AOI.
