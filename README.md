# ⚡ PowerPulse AI: Multi-Agent Energy Diagnostic System
### **Comprehensive Technical Documentation v1.0**

**Developer:** Mohammad Amaierh  
**Academic Field:**  Software Development  
**Core Technologies:** Django, CrewAI, OpenAI (GPT-4o & DALL-E 3), Twilio WhatsApp API, Ngrok.

---

## 1. Project Overview
**PowerPulse AI** is a state-of-the-art Multi-Agent System (MAS) designed to provide expert-level energy consultations and electrical fault diagnostics. It bridges the gap between complex power system engineering and residential consumers via a seamless WhatsApp interface.

---

## 2. System Architecture & Workflow
The system follows a modern, asynchronous backend architecture to handle high-latency AI tasks without blocking user communication.

### **The Request Life-cycle:**
1.  **Ingestion:** A user sends a message (e.g., "I see sparks in my AC"). Twilio forwards the payload to a Django Webhook.
2.  **Asynchronous Handling:** Using Python’s `threading` module, Django acknowledges the receipt immediately (HTTP 200) and offloads the processing to a background thread.
3.  **Local Tunneling (ngrok):** During development, `ngrok` provides a secure public URL (`https://your-id.ngrok-free.app`) to route Twilio's external requests to the local Django server.
4.  **Intelligent Routing:** The `PowerPulseFlow` classifies the request:
    * **Emergency:** Instant safety instructions (bypassing the Agents).
    * **Technical/Advice:** Triggers the CrewAI Agents.
5.  **Persistence Layer:** Django ORM creates an `EnergyConsumer` and a `ServiceTicket` in the database.
6.  **Visual Output:** **DALL-E 3** generates a technical schematic or safety poster.
7.  **Dispatch:** Final response (Text + Image URL + Ticket Ref ID) is sent back to WhatsApp.

---

## 3. Multi-Agent Design (CrewAI)
The system's "Brain" consists of three specialized agents working in a **Sequential Process**:

| Agent | Role | Technical Responsibility |
| :--- | :--- | :--- |
| **Energy Planner** | Dispatcher | Performs Intent Classification and identifies core technical terms. |
| **Energy Advisor** | Consultant | Provides ROI-focused energy-saving advice and efficiency tips. |
| **Electrical Specialist** | Diagnostician | Provides step-by-step fault diagnosis with a **Safety-First** priority. |

---

## 4. Database Schema (Persistence)
The backend is powered by a robust Django ORM schema to ensure every interaction is traceable.

* **EnergyConsumer:** Stores user profiles (Phone Number, Meter ID, Avg. Consumption).
* **ServiceTicket:** Tracks every inquiry with a unique ID (`TIC-XXXXXX`), category, and status (Open/Resolved).
* **GeneratedEnergyContent:** Archives AI-generated texts, the specific prompts used, and the URLs of generated diagrams.

---

## 5. Key Implementation Details

### **A. Safety-First Protocol**
For electrical hazards (e.g., sparks, fire), the system utilizes a **Short-Circuit Logic**. It skips the LLM deliberation and immediately sends critical safety warnings (Shut off breaker, evacuate, call emergency services).

### **B. WhatsApp Optimization**
* **Character Limit:** A specialized utility in `whatsapp_sender.py` monitors the 1600-character WhatsApp limit. It automatically truncates long reports to ensure the message and image link are delivered.
* **Decoupling:** The UI is entirely handled by WhatsApp/Twilio, making the backend modular and ready to integrate with Telegram or Web-UIs in the future.

### **C. Security & Logging**
* **Environment Variables:** All sensitive keys (OpenAI, Twilio, Django Secret) are managed via a `.env` file.
* **Logging:** A `FileHandler` logs all system events into `power_pulse_debug.log`, tracking API errors and successful dispatches.

---

## 6. Setup & Deployment Guide
1.  **Dependencies:** `pip install django crewai litellm twilio python-dotenv`
2.  **Database Migration:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```
3.  **Local Tunneling:**
    - Run `ngrok http 8000`.
    - Update Twilio Webhook URL with the `ngrok` address.
4.  **Execution:**
    `python manage.py runserver`

---

## 7. Future Roadmap
* **RAG Integration:** Connecting agents to official "Electrical Grid Codes" and appliance PDF manuals.
* **Computer Vision:** Analyzing photos of electricity bills or meters to update consumer consumption data automatically.
* **Multi-Lingual Support:** Expanding diagnostic accuracy for colloquial Arabic and technical English.

---
