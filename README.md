OpsPilot: Your Smart Assistant for Emails, Meetings, and More
OpsPilot is an intelligent assistant designed to streamline the management of emails, meetings, and tasks. It automates scheduling, email tracking, and meeting coordination, helping you stay on top of your responsibilities with ease. Powered by AI, OpsPilot optimizes your workflow and improves productivity by integrating various tools and services into a cohesive platform.

Features
Smart Email Management:

Automatically fetch and filter your important emails.

Track your inbox and categorize emails based on importance and relevance.

AI-Powered Meeting Scheduler:

Schedule meetings with AI assistance based on participants' calendars, routines, and preferences.

Get suggestions for optimal meeting times with smart negotiation and conflict detection.

Role-Based User Profiles:

Personalized user profiles to manage access to emails, meetings, and tasks based on roles (e.g., HR, managers, or developers).

Integration with Google Services:

Google OAuth for user authentication.

Google Calendar integration for scheduling meetings and sending reminders.

Data Security:

Secrets and sensitive information (e.g., API keys, OAuth tokens) are excluded from version control.

Flexible Agent Communication:

Multi-agent system using Coral Protocol for seamless communication between various agents (e.g., calendar, email, and negotiation agents).

Installation
To set up and run OpsPilot locally, follow these steps:

Prerequisites
Python 3.8+

Git

Google API credentials for Gmail and Google Calendar

Access to the Groq API (for AI-powered features)

Setup
Clone the repository:

bash
Copy
Edit
git clone https://github.com/maria2469/Opspilot.git
cd Opspilot
Install dependencies:

Install the necessary Python packages listed in requirements.txt:

bash
Copy
Edit
pip install -r requirements.txt
Google OAuth Setup:

Create a project on Google Cloud Console.

Enable Gmail API and Google Calendar API.

Download the credentials.json file and place it in the root of the project directory.

Configure environment variables:

Set up your environment variables in a .env file:

env
Copy
Edit
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GMAIL_API_KEY=your-api-key
CALENDAR_API_KEY=your-calendar-api-key
Run the application:

Start the OpsPilot app:

bash
Copy
Edit
streamlit run main.py
Usage
Once the app is running:

Login using Google OAuth to authenticate and access your Gmail and Google Calendar.

Dashboard will display metrics on your email inbox, meetings, and tasks.

Meeting Scheduler: Input the details of your meeting and let the AI suggest the best time for all participants.

Email Assistant: View your important emails, categorized by priority, and take action.

Troubleshooting
Missing files or directories: If files like .env, credentials.json, or tokens/ are not found, ensure you have added them to your project directory as per the setup instructions above.

Google API Authentication issues: Ensure that your credentials file is valid and that you have properly set up the Google API permissions.

License
This project is licensed under the MIT License - see the LICENSE file for details.
