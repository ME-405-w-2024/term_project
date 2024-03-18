# Term Project for ME405 at California Polytechnic University

## Contributors: Kevin Jung, Aidan Schwing, Noah Fitzgerald

Documentation available at: https://me-405-w-2024.github.io/term_project/

---

## Introduction
The code and CAD files present in this repository serve as reference for a fixed position, single-axis mechanism intended to shoot NERF RIVAL balls of approximately 1" diameter. This robot participated in a duel-style competition where two teams with similarly designed mechanisms competed to shoot the opposing team as quickly as possible. Robots were required to begin facing backwards, rotate 180 degrees, target with a thermal camera, and shoot the opponent.

Our team designed a custom shooting mechanism and implemented a stepper motor as our rotating axis. The specific implementation was intended for use by students in Cal Poly's ME 405 course, though use in the future is not limited to those individuals. Files are provided under the MIT License.  

While the documentation provided here may provide a good baseline, it is *not* comprehensive and *is not* intended to provide step-by-step instructions for recreation. 


## Hardware Overview
Much of the mechanical design was based on COTS hardware and components available on-hand. Shooting is performed with a [BLDC motor](https://hobbyking.com/en_us/propdrive-v2-2836-1800kv-brushless-outrunner-motor.html?wrh_pdp=3) driven by an [ESC](https://www.rcelectricparts.com/40a-esc---classic-series.html) and was sized to shoot at approximately the same speed as a stock NERF rifle. Balls are pushed into the wheels with a MG90s servo.

CAD images:

![para front](https://github.com/ME-405-w-2024/term_project/blob/main/media/Picture1.png)
![para rear](https://github.com/ME-405-w-2024/term_project/blob/main/media/Picture2.png)
![top view](https://github.com/ME-405-w-2024/term_project/blob/main/media/Picture3.png)
![side section](https://github.com/ME-405-w-2024/term_project/blob/main/media/Picture4.png)


![completed project](https://github.com/ME-405-w-2024/term_project/blob/main/media/CompletedProject.png)

## Software Design
Fill in later.

## Electrical Design
![schematic](https://github.com/ME-405-w-2024/term_project/blob/main/media/ElecDiagram.png)

## Results
The system was tested in multiple stages as mechanical hardware and the respective code implementations were completed. Almost all of the mechanical hardware was 3D printed before final implementation.

>shooting

Shooting was tested off of the main pivot mechanism. Due to the speed of wheel rotation, belt tension was essential to ensuring functionality. 3D printed bearing mounts and mounting plates were iterated multiple times before the final design. 

> main pivot mech?

> code / stepper discussion

## Lessons Learned
Implementation of a custom shooting mechanism proved to be quite challenging indeed. Much of the hardware was iterated at least 3 separate times before being deemed successful. 

The servo-based feed mechanism was remarkably successful due to the prevalence of robust servo hardware and ease of code implementation. The rotation-to-linear motion linkage proved highly reliable. 

Shaft alignment, concentricity, and belt tension proved the most challenging aspects of mechanical design. Proper belt tension provisions must be taken and rotating components should fit as tight as possible to any shafts to prevent excess losses. 

> stepper discussion
