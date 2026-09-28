"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

schools = {
    "Mergington High School": {
        "name": "Mergington High School",
        "short_name": "MHS",
        "join_code": "MHS123",
        "members": ["student@mergington.edu", "teacher@mergington.edu"],
        "admins": ["admin@mergington.edu"],
        "announcements": ["Welcome to Mergington High School!"],
    }
}

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "school": "Mergington High School",
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "school": "Mergington High School",
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "school": "Mergington High School",
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "school": "Mergington High School",
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "school": "Mergington High School",
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "school": "Mergington High School",
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "school": "Mergington High School",
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "school": "Mergington High School",
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "school": "Mergington High School",
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/schools")
def get_schools():
    return schools


@app.post("/schools", status_code=201)
def create_school(school: dict):
    """Create a new school and attach it to the in-memory registry."""
    name = school.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="School name is required")

    if name in schools:
        raise HTTPException(status_code=400, detail="School already exists")

    school_record = {
        "name": name,
        "short_name": school.get("short_name") or name[:3].upper(),
        "join_code": school.get("join_code") or "SCHOOL123",
        "members": [],
        "admins": [],
        "announcements": [],
    }
    schools[name] = school_record
    return school_record


@app.post("/schools/{school_name}/join")
def join_school(school_name: str, email: str = Query(...), join_code: str = Query(...)):
    """Allow a student to join a school with the published join code."""
    if school_name not in schools:
        raise HTTPException(status_code=404, detail="School not found")

    school = schools[school_name]
    if join_code != school["join_code"]:
        raise HTTPException(status_code=400, detail="Invalid join code")

    if email not in school["members"]:
        school["members"].append(email)

    return school


@app.get("/activities")
def get_activities(school: str | None = None):
    if school is None:
        return activities

    if school not in schools:
        raise HTTPException(status_code=404, detail="School not found")

    filtered = {
        name: activity
        for name, activity in activities.items()
        if activity.get("school") == school
    }
    return filtered


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
