 Sylvan Sentinel

Sylvan Sentinel is an intuitive, nature-inspired sustainability tracking application built to help users actively monitor, manage, and reduce their environmental footprint. 

Developed as a solo submission for the SkillUp Hackathon in collaboration with IBM SkillsBuild, this tool blends foundational backend logic with a calm, forest-inspired vision of active environmental stewardship.

---

 🍃 Core Project Structure

The project is structured as a clean Python application, separating core functionality, user data, and logic validation:

* 📁 **`tracker/`** – Contains the primary application environment, logic processing modules, and data pipeline configurations.
* 📄 **`app.py`** – The main execution file that launches the application interface and coordinates tracking functionalities.
* 📁 **`data/`** – The storage directory handling localized sustainability logs, metrics, and user footprint records.
* 📁 **`tests/`** – Comprehensive test suites utilized during development to ensure reliable computation of carbon and consumption metrics.
* 📄 **`requirements.txt`** – Defines all foundational Python packages and core library dependencies required to spin up the application seamlessly.

---

 🛡️ Built With

* Python – The fundamental logic architecture.
* IBM Developer Toolkit – Leveraged during structural prototyping to map out data relations efficiently.

---

 How to Run Locally

 # Prerequisites

Before running this project, ensure you have Python installed on your system. You can download it from [python.org](https://python.org).

## Setup and Installation Instructions

Follow these step-by-step instructions to get the application running locally on your machine.

### 1. Clone the Repository
Open your terminal or command prompt and clone this repository:
```bash
git clone https://github.com
```

### 2. Navigate to the Project Directory
Change your directory to the folder containing the project files:
```bash
cd sustainability-tracker
```

### 3. Set Up a Virtual Environment (Recommended)
To keep your dependencies organized, create and activate a virtual environment.

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```
*Note: If you receive a script execution error on Windows, run your terminal as an Administrator and execute `Set-ExecutionPolicy RemoteSigned -Scope Process`, then try activating again.*

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Required Packages
Install all the necessary libraries and dependencies listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 5. Run the Application
Launch the Streamlit web application by running:
```bash
streamlit run app.py
```

### 6. View the App
Once the server starts, it will automatically open in your default web browser. If it doesn't, navigate to the local URL provided in your terminal:
---

## 🌍 Hackathon Details
* **Developer:** Tanish Kumawat
* **Team Profile Name:** Sylvan Sentinel
* **Hackathon:** SkillUp Hackathon (In collaboration with IBM SkillsBuild)
*

# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.
