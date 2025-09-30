Urja-Link: Deep Learning for City-Scale Rooftop Solar Potential ️
Welcome to Urja-Link! This repository contains the official code for SolarNet+, our deep learning framework designed for high-precision, city-scale rooftop solar potential estimation, as detailed in our paper: "Deep learning-based framework for city-scale rooftop solar potential estimation by considering roof superstructures".

Traditional methods often overestimate solar potential by ignoring rooftop obstacles like vents, chimneys, or skylights. SolarNet+ solves this by being the first framework to simultaneously identify roof orientations and segment these superstructures, leading to a much more accurate assessment.

Suggestion: Replace the link above with a cool banner image! You could show an aerial photo on the left, your model's segmentation masks in the middle, and the final 3D PV potential map on the right.

 Key Features
 Superstructure-Aware: Accurately detects rooftop obstacles (superstructures) that prevent solar panel installation, avoiding overestimation.

 Simultaneous Learning: A novel network that learns both roof orientation and superstructure segmentation in a single pass.

State-of-the-Art Performance: Outperforms other leading approaches on benchmark datasets for both segmentation tasks.

City-Scale Analysis: Proven to be effective for large-scale applications, as demonstrated in our case study of Brussels.

 The Problem We Solve
Solar energy is key to a sustainable future, but knowing exactly how many panels can fit on a roof is tricky. Most automated systems look at a roof and see a blank slate. They miss the small things—vents, skylights, chimneys—that take up valuable space. This leads to over-optimistic estimates of a city's solar capacity.

Our solution, SolarNet+, uses aerial imagery to create a detailed map of every roof, marking out not just the usable surfaces and their orientation to the sun, but also all the pesky obstacles. This data-driven approach gives city planners, energy companies, and homeowners a far more realistic view of their true solar potential.

 How It Works
The Urja-Link framework processes aerial imagery in a multi-step pipeline:

Image Segmentation: The trained SolarNet+ model takes an aerial image as input.

Mask Generation: It outputs precise segmentation masks for:

The overall roof area.

The orientation of each roof plane (e.g., North, South, East, West-facing).

All rooftop superstructures.

PV Potential Calculation: A final script uses these masks to calculate the practical yearly photovoltaic (PV) energy generation (kWh/year) for each roof segment and generates a GeoJSON file visualizing where panels can be installed.

 Getting Started
Prerequisites
Python 3.8+

PyTorch

GDAL

Other dependencies
