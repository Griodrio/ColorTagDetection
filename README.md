# ColorTagDetection

This repository is about creating script that can detect color tag and identify the object based on the pattern on the color tag.

The example of the color tag is as shown below.

<p align="center">
  <img  src="https://user-images.githubusercontent.com/93776676/182359353-5f55887d-508c-452e-aa0b-c150574a548f.jpg">
</p>

The pattern for each object will be different. The test images used for this projects are shown below.

<p align="center">
  <img width="300" height="400" src="https://user-images.githubusercontent.com/93776676/182124599-49bc5d18-9134-49c6-b752-3316c3d1a37f.png">
</p>

The objectives of the project is to try detect a color tag in an image and recognize the pattern of the tag using image processing then identify it object. 
In this project it use corner detection to search for a color tag. Beside detecting the corner of the color tag, the area of the color tag needed to be know. This is to make sure that the detected points are corner of the tag.

The process of detecting color tag corner is shown below.

<p align="center">
  <img width="300" height="400" src="https://user-images.githubusercontent.com/93776676/182127598-eff58660-8cba-41c4-b863-cba3b7b3cfcc.png">
</p>

After getting each corner points of the tag, next step is to rearrange the order of the points so the order is always the same, where the first point is at the top left, second corner is top right, third corner is at bottom left, and last corner is at bottom right, the function reorder(myPoints) will reorder the points. The illustration of the objective is as shown below.

<p align="center">
  <img src="https://user-images.githubusercontent.com/93776676/182128537-ceaf8b46-1988-4464-b6d0-d45cea9f2968.png">
</p>

from the illustration we can see that the first corner (red dot) the sum of it will always have the lowest score. The same goes to 4th/last corner points, if we add the x and y value it will have highest sum. at point 2 (green) the value on the y axis (0) is reduced by the x (w) axis, which is 0 – w (image width) it will produce a -w value. This shows that at point 2 will produce the smallest difference value than the value at point 3 (blue).

The objective of rearangging the corner points is to warp perspective so it will only display the detected tag. From that we can continue to search for the pattern of the tag. To make the script robust from rotation, we can try to detect the top of the color tag by identifying where is the green square located and rotate the tag. To differentiate the color tag we can use the centroid of each circle (red, green, blue) and compared one color of circle, for example the red circle on the left with the same on the right. If the centroid has the same or slight difference then we can be sure that is a keyboard. The example of detection is as shown below.

<p align="center">
  <img src="https://user-images.githubusercontent.com/93776676/182129996-85450ff6-801a-4129-87d7-cc50e549a7fd.png">
</p>

