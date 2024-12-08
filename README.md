# DunamisMax.com

This is the source code for **DunamisMax.com**, a Flask-based web application.

## Project Structure

```
DunamisMax.com/
├── dunamismax/                # Main application directory
│   ├── venv/                # Virtual environment
│   ├── static/             # Static files (CSS, JavaScript, images)
│   ├── templates/          # HTML templates
│   ├── config.py           # Configuration file
│   ├── run.py              # Application entry point
├── requirements.txt          # Python dependencies
```

## Prerequisites

- Python 3.x
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dunamismax.com.git
   cd dunamismax.com/dunamismax
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Server

To run the development server:
```bash
flask run --host=0.0.0.0 --port=42069
```

### Production Server

For production, use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:42069 run:app
```

## Features

- Home page and blog page
- Responsive design
- Open Sans font integration

## Deployment

This application can be deployed with a production WSGI server such as Gunicorn, optionally behind a reverse proxy like NGINX.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

