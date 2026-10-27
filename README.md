# \# NLP Chatbot

# 

# A full-stack Natural Language Processing (NLP) chatbot built with Python, scikit-learn, FastAPI, React, and TypeScript. The application classifies user intent using a TF-IDF vectorizer and Logistic Regression model, then returns an appropriate response.

# 

# \## Features

# 

# \- \*\*Intent classification:\*\* TF-IDF features and Logistic Regression.

# \- \*\*Response generation:\*\* Intent-based responses configured in JSON.

# \- \*\*Phrase matching:\*\* Handles known phrases reliably.

# \- \*\*Fallback handling:\*\* Responds to unfamiliar or low-confidence messages.

# \- \*\*REST API:\*\* FastAPI endpoints for health checks and chat.

# \- \*\*Interactive interface:\*\* React and TypeScript chat UI.

# \- \*\*Automated tests:\*\* Python tests for chatbot behavior and API validation.

# \- \*\*Local execution:\*\* Run the frontend and backend on your own machine.

# 

# \## Technology Stack

# 

# | Component | Technologies |

# |---|---|

# | NLP and machine learning | Python, scikit-learn, pandas |

# | Backend | FastAPI, Uvicorn, Pydantic |

# | Frontend | React, TypeScript, Vite, CSS |

# | Model features | TF-IDF |

# | Classifier | Logistic Regression |

# | Testing | pytest, FastAPI TestClient |

# | Data format | JSON |

# 

# \## Project Structure

# 

# ```text

# NLP-Chatbot/

# ├── backend/

# │   └── main.py

# ├── data/

# │   └── intents.json

# ├── frontend/

# │   ├── src/

# │   ├── index.html

# │   ├── package.json

# │   └── vite.config.ts

# ├── models/

# ├── src/

# │   └── nlp/

# │       ├── chatbot.py

# │       └── train.py

# ├── tests/

# │   ├── test\_api.py

# │   └── test\_chatbot.py

# ├── .gitignore

# └── README.md

# ```

# 

# \## Requirements

# 

# \- Python 3.11 or a compatible Python version

# \- Node.js and npm

# \- Git

# 

# \## Installation

# 

# \### 1. Clone the repository

# 

# ```bash

# git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

# cd NLP-Chatbot

# ```

# 

# Replace the placeholder with your actual GitHub repository URL.

# 

# \### 2. Create and activate a Python environment

# 

# Windows CMD:

# 

# ```cmd

# python -m venv venv

# venv\\Scripts\\activate.bat

# ```

# 

# \### 3. Install Python dependencies

# 

# Install the project's required Python packages. If a `requirements.txt` file is available:

# 

# ```cmd

# python -m pip install -r requirements.txt

# ```

# 

# If it is not available, create one containing the project's required backend and testing dependencies before following this step.

# 

# \### 4. Install frontend dependencies

# 

# ```cmd

# cd frontend

# npm install

# cd ..

# ```

# 

# \## Model Training

# 

# Train the intent classifier from the project root:

# 

# ```cmd

# python -m src.nlp.train

# ```

# 

# The training script reads the configured intent data, trains and evaluates the classifier, and saves the trained model if the training completes successfully.

# 

# Ensure the trained model is available locally before starting the chatbot. Follow the paths configured by the training and chatbot scripts.

# 

# \## Running the Application

# 

# Run the backend and frontend in separate terminals.

# 

# \### Terminal 1: Backend

# 

# From the project root, activate the virtual environment and start FastAPI:

# 

# ```cmd

# venv\\Scripts\\activate.bat

# python -m uvicorn backend.main:app --reload

# ```

# 

# Backend URL: `http://127.0.0.1:8000`

# 

# Interactive API documentation: `http://127.0.0.1:8000/docs`

# 

# Health endpoint: `http://127.0.0.1:8000/health`

# 

# \### Terminal 2: Frontend

# 

# ```cmd

# cd frontend

# npm run dev

# ```

# 

# Open the local URL printed by Vite, normally `http://127.0.0.1:5173`.

# 

# \## API Endpoints

# 

# | Method | Endpoint | Purpose |

# |---|---|---|

# | GET | `/` | API information |

# | GET | `/health` | Backend health check |

# | POST | `/chat` | Submit a message and receive a chatbot response |

# 

# Example request:

# 

# ```json

# {

# &#x20; "message": "Hello!"

# }

# ```

# 

# The chat endpoint returns the response and intent-related information defined by the backend response schema.

# 

# \## Testing

# 

# Run the Python tests from the project root:

# 

# ```cmd

# python -m pytest -v

# ```

# 

# The current test run completed with \*\*19 passed tests\*\* covering chatbot behavior and API endpoints.

# 

# Build the frontend for production:

# 

# ```cmd

# cd frontend

# npm run build

# ```

# 

# The frontend production build has completed successfully.

# 

# \## Current Limitations

# 

# \- The chatbot is based on a predefined set of intents and responses.

# \- It is not a general-purpose generative AI model.

# \- Response quality depends on the training examples, intent configuration, and confidence threshold.

# \- A production deployment would require additional security, monitoring, configuration, and deployment work.

# 

# \## Future Improvements

# 

# \- Expand and balance the intent dataset.

# \- Evaluate per-intent precision, recall, and F1 score.

# \- Improve confidence calibration and fallback behavior.

# \- Add conversation persistence if needed.

# \- Add more API and frontend integration tests.

# \- Deploy the application with appropriate security and monitoring.

# 

# \## License

# 

# Add a license file if you intend to distribute this project publicly.



