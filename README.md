# IGCSE Mathematics Paper Generator

A powerful web application that generates customized mathematics exam papers and practice questions for IGCSE Extended Mathematics (0580) and Additional Mathematics (0606) syllabi.

![Paper Generator Interface](assets/interface.png)

## Features

### 1. Custom Paper Generation
- Generate full exam papers tailored to specific topics
- Adjustable total marks (15-150)
- Support for both Extended (0580) and Additional (0606) Mathematics
- Optional inclusion of question information (year, paper, marks)
- Topic-specific selection for targeted practice

### 2. Random Question Generator
- Generate individual practice questions on demand
- Filter questions by specific topics
- View detailed question information:
  - Topic
  - Marks
  - Year
  - Month/Session
  - Paper number
  - Variant
- High-quality question images with zoom functionality

### 3. Modern User Interface
- Clean and intuitive design
- Responsive layout for all devices
- Real-time progress indicators
- Smooth animations and transitions
- Professional PDF viewer with controls:
  - Page navigation
  - Zoom controls
  - Download option
  - Print functionality

## Technology Stack

- **Frontend:**
  - HTML5
  - CSS3 (with modern features like CSS Grid, Flexbox)
  - JavaScript (ES6+)
  - PDF.js for PDF rendering

- **Backend:**
  - Python
  - AWS Lambda
  - AWS S3 for storage
  - API Gateway

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Shahu-123/PaperGenerator.git
   cd PaperGenerator
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials:
   - Set up an AWS account
   - Configure AWS CLI with your credentials
   - Create necessary AWS resources (Lambda, S3, API Gateway)

4. Start the local development server:
   ```bash
   python -m http.server 8000
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

### Generating a Full Paper

1. Select the subject (Extended or Additional Mathematics)
2. Set the desired total marks using the slider
3. Choose whether to include question information
4. Select specific topics or use "Select all topics"
5. Click "Generate Paper"
6. View, download, or print the generated PDF

### Using the Random Question Generator

1. Select the subject
2. Optionally choose a specific topic
3. Click "Generate Random Question"
4. View the question details and image
5. Use the zoom feature for better visibility

## API Documentation

### Paper Generation Endpoint

```json
POST /dev
{
  "topic": ["algebra", "trigonometry"],
  "mark": 50,
  "subjectId": "0570",
  "info": true
}
```

### Random Question Endpoint

```json
POST /dev
{
  "action": "random_question",
  "topic": "algebra",
  "subjectId": "0570"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/new-feature
   ```
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- IGCSE Mathematics syllabus and questions © Cambridge Assessment International Education
- PDF.js library by Mozilla
- Icons from Heroicons

## Contact

Shahu Wagh - [GitHub](https://github.com/Shahu-123)

Project Link: [https://github.com/Shahu-123/PaperGenerator](https://github.com/Shahu-123/PaperGenerator)