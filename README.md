# CT Spectral Data Simulation Project

## Project Overview

This project aims to simulate and generate spectral CT data, providing high-quality datasets required for research and development. By considering multiple factors, including the X-ray source energy spectrum, Bowtie filter, material absorption characteristics, and the absorption efficiency of the detector, the project lays the foundation for CT image reconstruction and analysis.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage Instructions](#usage-instructions)
- [License](#license)

## Features

- **Consideration of Multiple Imaging Factors**: Comprehensive consideration of various factors such as the X-ray source energy spectrum, Bowtie filter, and material absorption characteristics.
- **Flexible Simulation Settings**: Supports various parameter configurations to meet different research needs.

## Installation

Please ensure that Python 3.x and pip are installed on your system. Then, you can install the project dependencies using the following command:

```bash
pip install -r requirements.txt


## Usage Instructions
Run the Genimg.py file to generate base material images with different concentrations of iodine, bone, and water. After projecting the base material images (with customizable projection parameters), run the GenHLEnergy_Sino.py file to generate dual-energy sino images. Reconstruction will yield the dual-energy CT images.

## License
This project is licensed under the ELP 2.0 License.
