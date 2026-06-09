# Sujata Fashion (SFA) Project

This project is a comprehensive web application for Sujata Fashion, featuring a modern frontend and a FastAPI backend.

## Project Structure

- `backend/`: FastAPI backend logic and data management.
- `js/`: Frontend JavaScript modules.
- `css/`: Styling files.
- `assets/`: Static images and resources.
- `docs/`: Project documentation and roadmap.
- `tests/`: Automated test suites.

## Setup and Installation

### Prerequisites

- Python 3.11+
- `pip`

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sujata-fashion-test-stylist
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

5. **Run the Backend:**
   ```bash
   uvicorn backend.main:app --reload
   ```

## Roadmap

The project follows a structured roadmap available in `roadmap_index.md`.
