# CoreTrack: Full-Stack Behavioral Telemetry & Predictive AI Workspace

CoreTrack is an intelligent, full-stack web application designed to bridge the gap between human behavioral patterns and data science telemetry. The platform tracks daily productivity loops, maintains consecutive routine habit streaks, logs sentiment-driven journals, and processes real-time data analytics.

## Data Science & AI Implementation Architecture

This workspace is engineered not just for tracking, but as a pipeline for behavioral data analytics. The current version and upcoming iterations utilize structured data for statistical profiling:

### 1. NLP Sentiment Logging Pipeline
* **Mechanism:** User journal inputs are transmitted via asynchronous networks to the FastAPI backend layer.
* **Telemetry Data Captured:** Relational text logs are parsed to isolate distinct cognitive mood states (`Happy` vs `Anxious`).
* **Presentation Layer:** Dynamically rendered into a scrollable, descending "Past Entries Archive" feed that updates natively without UI blockages.

### 2. Behavioral Correlation & Analytics Engine
* **Statistical Metrics:** Calculates a real-time **Anxiety Index** percentage based on the density and emotional variance of user inputs.
* **Feature Intersect:** Built on top of a SQLite schema that allows developers to calculate the exact correlation ($r$) between habit consistency loops (Streaks) and mental well-being scores over time.

---

## The Full-Stack Technology Layer

The system layout is built entirely from scratch with no bulky frameworks, maintaining a lightweight memory footprint:

| Layer              | Technology              | Primary Purpose                                                                                 |
| :----------------- | :---------------------- | :---------------------------------------------------------------------------------------------- |
| **Frontend UI**    | HTML5 / CSS3 Grid       | Implements a responsive, sleek dark-mode developer dashboard layout.                            |
| **State Router**   | Native JavaScript (ES6) | Orchestrates persistent multi-user session tokens (`localStorage`) and alert-free DOM updates.  |
| **Backend Engine** | Python / FastAPI        | Drives high-speed RESTful API endpoints (`GET`, `POST`, `PUT`) under an ASGI server model.      |
| **ORM Database**   | SQLAlchemy / SQLite     | Manages relational data integrity shields, unique user constraints, and cascading data streams. |

---

## System Features & User Experience

* **The Guard Gate Pattern:** Full authentication system containing a login and registration toggle wall. Users cannot bypass or visualize analytics maps without a verified relational identity key.
* **Interactive Profile Customization:** Includes an editable profile layout block allowing real-time `PUT` mutations of user data, pulling real registered registration credentials directly from backend queries.
* **Habit Loop Engine:** Leverages behavioral psychology metrics to track continuous routine performance via a persistent data model.

---

## Local Installation & Initialization

To run the full telemetry stack locally on your workstation, execute the following steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/parthi-5/CoreTrack.git](https://github.com/parthi-5/CoreTrack.git)
   cd CoreTrack