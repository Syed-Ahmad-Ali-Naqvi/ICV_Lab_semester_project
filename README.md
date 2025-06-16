# Motion Detection Comparison Tool

A comprehensive web application for comparing custom optical flow implementations with library methods. This tool provides visual comparisons, performance metrics, and detailed analysis of motion detection algorithms.

## ✨ Features

- **Dual Analysis Modes**: Single method analysis or comprehensive comparison
- **Method Categories**: 
  - **Custom Implementations**: Horn-Schunck, Lucas-Kanade Dense, Pyramidal Lucas-Kanade, SSD Block Matching
  - **Library Methods**: Scikit-image (Horn-Schunck, Lucas-Kanade), OpenCV (Farneback, TV-L1)
- **Real-time Metrics**: Execution time, flow statistics, comparison metrics (MSE, MAE, Angular Error, Endpoint Error)
- **Interactive Visualizations**: Flow field arrows, comparison grids, performance charts
- **Modern UI**: Bootstrap-based responsive design with loading indicators
- **Image Management**: Local storage with preview functionality

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd ICV_Lab_semester_project
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   
   On Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   On Windows (Command Prompt):
   ```cmd
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:8000
   ```

## 📖 Usage Guide

### Single Method Analysis

1. **Upload Images**: Select two sequential images using the file inputs
2. **Select Analysis Type**: Choose "Single Method Analysis"
3. **Choose Method**: Select from the dropdown (Custom or Library implementations)
4. **Analyze**: Click "Analyze Motion" to process
5. **View Results**: See the flow visualization and performance metrics

### Comparison Analysis

1. **Upload Images**: Select two sequential images
2. **Select Analysis Type**: Choose "Compare All Methods"
3. **Select Methods**: Check the methods you want to compare
   - Use "Select All Custom" or "Select All Library" for quick selection
4. **Analyze**: Click "Analyze Motion" to process
5. **View Results**: 
   - Visual comparison grid showing all selected methods
   - Performance chart comparing execution times
   - Detailed metrics for each method

### Understanding the Metrics

- **Execution Time**: Time taken to compute optical flow (seconds)
- **Mean Magnitude**: Average flow vector magnitude
- **Max Magnitude**: Maximum flow vector magnitude
- **MSE (Mean Squared Error)**: Comparison metric between methods
- **MAE (Mean Absolute Error)**: Alternative comparison metric
- **Angular Error**: Direction accuracy between flow fields
- **Endpoint Error**: Positional accuracy of flow vectors

## 🔧 Technical Details

### Architecture

```
ICV_Lab_semester_project/
├── app.py                      # FastAPI backend server
├── requirements.txt            # Python dependencies
├── utils/                      # Core utilities
│   ├── __init__.py
│   ├── motion_methods.py       # All optical flow implementations
│   ├── evaluation_metrics.py   # Performance evaluation functions
│   └── visualization.py        # Flow visualization utilities
├── templates/
│   └── index.html             # Enhanced Bootstrap UI
├── static/
│   └── enhanced-script.js     # Frontend JavaScript logic
└── [legacy files]            # Original implementations
```

### Supported Methods

#### Custom Implementations
- **Horn-Schunck**: Global energy minimization approach
- **Lucas-Kanade Dense**: Local window-based method
- **Pyramidal Lucas-Kanade**: Multi-scale Lucas-Kanade
- **SSD Block Matching**: Template matching approach

#### Library Methods
- **Scikit-image Horn-Schunck**: Optimized implementation
- **Scikit-image Lucas-Kanade**: Iterative Lucas-Kanade
- **OpenCV Farneback**: Dense optical flow algorithm
- **OpenCV TV-L1**: Total variation regularized method

### API Endpoints

- `GET /`: Main application interface
- `GET /available-methods`: List all available methods
- `POST /single-method`: Process single method analysis
- `POST /compare-methods`: Compare all methods and return metrics
- `POST /visualize-comparison`: Generate comparison visualization

## 🎯 Use Cases

### Academic Research
- Compare custom algorithm implementations with established methods
- Analyze performance trade-offs between different approaches
- Generate publication-quality visualizations and metrics

### Algorithm Development
- Test new optical flow implementations
- Benchmark against standard methods
- Visualize flow field characteristics

### Educational Purposes
- Understand optical flow algorithm differences
- Interactive learning of computer vision concepts
- Hands-on experimentation with motion detection

## 🐛 Troubleshooting

### Common Issues

1. **"Error loading available methods"**
   - Ensure all dependencies are installed correctly
   - Check that the server is running properly

2. **Slow processing with large images**
   - Consider resizing images to 512x512 or smaller
   - Some methods (especially custom implementations) may be slower

3. **Method comparison fails**
   - Try selecting fewer methods for comparison
   - Ensure images are in supported formats (PNG, JPG)

4. **Charts not displaying**
   - Ensure JavaScript is enabled in your browser
   - Check browser console for any errors

### Performance Tips

- Use images of moderate size (512x512 recommended)
- For comparison analysis, start with 2-3 methods
- Custom implementations may take longer than library methods

## 📋 Dependencies

See `requirements.txt` for complete list. Key dependencies:

- FastAPI: Web framework
- OpenCV: Computer vision library
- NumPy: Numerical computing
- SciPy: Scientific computing
- Scikit-image: Image processing
- Uvicorn: ASGI server

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is developed for academic purposes. Please check with your institution regarding usage and distribution policies.

## 🔗 Related Work

- [OpenCV Optical Flow Tutorial](https://docs.opencv.org/master/d4/dee/tutorial_optical_flow.html)
- [Horn-Schunck Algorithm](https://en.wikipedia.org/wiki/Horn%E2%80%93Schunck_method)
- [Lucas-Kanade Method](https://en.wikipedia.org/wiki/Lucas%E2%80%93Kanade_method)