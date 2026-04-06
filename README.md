# Real Estate Search, Audit and Anomaly Platform

## The Problem
Our analysts aren't struggling to find deals—they're struggling to vet them. Too much time is wasted on manual "sanity checks": verifying market prices, flagging bad data, and running the same financial models over and over.

## The Solution: Intelligent First-Pass Screening
We’ve automated the "sanity checks" so analysts can skip the grunt work. The platform provides:
* **Instant Financials:** Yields and costs are pre-calculated and ready on demand.
* **Automatic Flagging:** The system benchmarks listings against zip-code peers to catch bad data or price outliers.
* **Background Heavy Lifting:** Complex math runs every 6 hours. This keeps the UI fast and ensures analysts never wait on a loading screen.

## Strategic Value
This shifts the team from manual data entry to **exception-based reviewing**:
* **Speed & Focus:** Analysts spend time on high-potential deals, not noise.
* **Consistency:** Every listing is judged by the same logic across all geographies.
* **Governance:** No "black box" math—every flag is persisted and easy to explain.

## Tech Structure
* Backend: FastAPI + SQLAlchemy
* Frontend: React (Vite)
* Database: PostgreSQL via DATABASE_URL
* Orchestration: Docker Compose
* Dependency management: Poetry
* Batch processing: dedicated batch container running python -m app.batch.batch_update

## Operating Model
The platform follows a split model:

- Interactive path for user-driven retrieval.
- Scheduled path for analytical refresh.

This keeps response times practical while maintaining freshness and repeatability of derived signals.

## Controls and Reliability
The delivery process includes structured testing and production-readiness checks to ensure outputs remain reliable across updates.

Operational procedures and release controls are documented separately for engineering and operations teams in [OPERATIONS.md](OPERATIONS.md). 

## Risks & Management Focus
As we scale, we’re keeping a close eye on a few key areas:
* **Data & Performance:** Watching for "garbage in" from listing sources and ensuring the UI stays snappy as deal volume grows.
* **Governance:** Strengthening access controls and observability as more users join the platform.
* **Quality Standards:** Formalizing our release criteria to ensure every update meets our baseline before it hits the team.


## Team and Collaboration
### **The Team: Owners, Not Just Builders**
We’ve moved beyond "data experiments" to a reliable product by owning the full lifecycle:
* **End-to-End Delivery:** We own everything from the financial math to the UI.
* **Business-First:** Our architecture ensures business goals, not tech limits, drive the roadmap.
* **High Velocity:** Clear ownership means faster pivots and zero "too many cooks" friction.

## The Bottom Line
We’ve replaced messy spreadsheets with a professional, automated engine that streamlines your real-estate screening into a single, scalable interface.
