# OncoAI Survival Prediction API

## Overview

The OncoAI Survival Prediction API is a web service designed to predict patient survival rates in oncology using machine learning models. This API provides endpoints for user authentication, survival prediction, and health checks.

## Features

- **User Authentication**: Secure user registration and login using JWT tokens.
- **Survival Prediction**: Predict patient survival rates based on input features.
- **Health Checks**: Verify the status of the API, database connection, and model loading.

## Project Structure

The project is structured as follows:

- `app/`: Contains the main application code.
  - `main.py`: The entry point of the application.
  - `api/`: Contains the API endpoints.
    - `auth.py`: Authentication-related API endpoints.
    - `survival.py`: Survival analysis-related API endpoints.
  - `core/`: Contains core application logic.
    - `config.py`: Configuration settings.
    - `model.py`: Data models.
    - `security.py`: Security-related functions.
    - `utils.py`: Utility functions.
    - `models/`: Contains additional data models.
  - `db/`: Contains database-related code.
    - `crud.py`: CRUD operations.
    - `models.py`: Database models.
    - `session.py`: Database session management.
  - `schemas/`: Contains Pydantic schemas.
    - `auth.py`: Authentication-related schemas.
    - `survival.py`: Survival analysis-related schemas.
- `entorno/`: Contains environment-related files.
- `static/`: Contains static files.
  - `neon-app.js`: JavaScript file for the Neon app.
  - `neon-dark.css`: CSS file for the Neon app.
  - `oncoai-dashboard.html`: HTML file for the OncoAI dashboard.
- `test.db`: SQLite database file.

## Dependencies

The application uses the following dependencies:

- FastAPI: A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- SQLAlchemy: The Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
- Pydantic: Data validation and settings management using Python type annotations.
- Uvicorn: An ASGI server for serving FastAPI applications.
- Passlib: Password hashing library for Python.
- PyJWT: JSON Web Token implementation in Python.
- Python-dotenv: Reads key-value pairs from a .env file and sets them as environment variables.

## Setup

To set up the application, follow these steps:

1. Create a virtual environment and activate it.
2. Install the dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file with the necessary environment variables.
4. Run the application using `uvicorn app.main:app --reload`.

## Testing

To run the tests, use the following command:

```bash
pytest
```

## API Endpoints

### Authentication

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Log in an existing user.
- `POST /token`: Obtain an access token for authentication.

### Survival Prediction

- `POST /api/predict`: Predict patient survival rates based on input features.

### Health Check

- `GET /health`: Verify the status of the API, database connection, and model loading.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
