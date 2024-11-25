# WhatsApp Payment Invoice Bot with AI Image Processing

This project is a **WhatsApp bot** designed to handle **payment invoices** with **AI-powered image processing**. The bot processes invoices using **TensorFlow** for image recognition, **OpenAI Vision** for understanding the content, and **Flask** for backend API management. The solution is containerized using **Docker** and deployed on **Google Cloud Run** for scalability.

## Technologies Used:
- **Python Flask** – Backend API to handle bot logic.
- **TensorFlow** – AI model for image processing and data extraction from invoices.
- **OpenAI Vision & Chat** – Used for enhancing invoice content understanding.
- **Docker** – Containerization for consistent deployment across environments.
- **Google Cloud Run** – Scalable and serverless deployment for the bot.

---

### Prerequisites:
- **Docker**: Installed for containerized setup.
- **Python 3.8+** and **pip**: If you prefer running the app locally without Docker.
- **Google Cloud** account: Needed for deployment.

---


### Step 1: Clone Repository

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/whatsapp-bot.git
   cd whatsapp-bot

### Step 2: Set Up Environment Variables

2. **Copy the `.env-example` file to `.env`**:
   
   First, you need to copy the `.env-example` file to a new `.env` file to set up your environment variables. Use the following bash command:

   ```bash
   cp .env-example .env

### Step 3: Build and Run Docker Container
If you're using Docker, you can build and run the container with the following commands: 

1. **Build the Docker image**:
   
   Now that you have your environment variables set up, the next step is to build the Docker image. Use the following command to build the image:

   ```bash
   docker build -t whatsapp-bot .
2. **Run the Docker image**:
   
   Now run the docker image file

   ```bash
   docker run -p 8082:8082 --env-file .env whatsapp-bot

### Step 4: Run Locally Without Docker (Optional)
If you prefer not to use Docker, you can run the application directly on your machine by following these steps:

1. **Install the necessary Dependencies**:

   ```bash
   pip install -r requirements.txt
   
2. **Run the Flask app**:

   ```bash
   python run.py


## Conclusion:
Now you're all set up to run the WhatsApp payment invoice bot either locally with Docker or without.

For more details, just contact me **arslanaslam173@gmail.com**

Thank you.
