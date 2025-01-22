# Image Dataset with Attributes - Bachelor Thesis Project

## Overview
This repository contains the implementation of a web application developed as part of my bachelor thesis titled **"Image Dataset with Attributes"**. The project involves creating a Czech-language image dataset with attributes, emphasizing:

- The systematic collection of data through a web application.
- Automating the process of dataset creation.
- Designing an accessible, user-friendly interface for data collection.

The project and showcases skills in **Python (Flask)**, **PostgreSQL**, **front-end development**, and **data processing**, as well as experience with **deploying applications on Heroku** I learned during my studies.

## Features

1. **Web Application**:
   - Collects user responses to annotate images with descriptive attributes.
   - Includes two main modules:
     - Initial attribute collection for dataset structure.
     - Main data collection for assigning attribute values to images.
   - Built with Flask and Jinja2 for dynamic content rendering.

2. **Dataset**:
   - Contains annotated images of furniture (e.g., chairs, tables, beds).
   - Available in multiple formats:
     - JSON: Comprehensive and compact versions.
     - CSV: Tabular format for easy analysis.

3. **Deployment**:
   - Previously hosted on Heroku for public access.
   - Includes automated scripts for data export and dynamic dataset updates.

4. **Database**:
   - Utilizes PostgreSQL for robust data management.
   - Schema designed to handle objects, attributes, and user responses efficiently.

## Project Structure

```plaintext
bakalarska_prace/
├── app.py               # Main Flask application
├── models.py            # Database models and ORM
├── requirements.txt     # Python dependencies
├── Procfile             # Heroku deployment configuration
├── download/            # Pre-generated datasets (CSV, JSON)
├── static/              # Static assets (CSS, images)
├── templates/           # HTML templates
└── venv/                # Virtual environment (optional)
```

## Datasets

The dataset created through this project is available for download via the repository:

- **CSV**: Easy to import into spreadsheet software.
- **JSON**: Includes detailed annotations for machine learning and data analysis.

## Deployment

The application was previously hosted on Heroku during the project's active phase. While it is no longer live, the code and setup instructions allow for redeployment if needed.

## Thesis

For more details about the methodology and design, refer to the full thesis: [Image Dataset with Attributes (PDF)](./bakalarka.pdf).

## Skills Demonstrated

- **Programming**: Python (Flask), SQL, HTML/CSS.
- **Database Management**: PostgreSQL, SQLAlchemy ORM.
- **Web Development**: Responsive UI, form handling, dynamic content rendering.
- **Data Handling**: JSON and CSV formats, automated dataset generation.
- **Deployment**: Heroku, GitHub integration, environment setup.

## Contact

For any inquiries, feel free to contact me via [LinkedIn](https://linkedin.com/in/lukejiricek).
