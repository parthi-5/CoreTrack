import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel,EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai
import models
from database import engine,Sessionlocal


load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")
ai_client=genai.Client(api_key=api_key)

models.Base.metadata.create_all(bind=engine)
app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally: 
        db.close()

class JournalEntrySchema(BaseModel):
    content: str
    user_id: int 

class UserCreateSchema(BaseModel):
    email: str
    password: str
    name: Optional[str] = "Anonymous Developer"

class HabitCreateSchema(BaseModel):
    name:str
    user_id:int

@app.get("/")
def read_root():
    return {"message": "Welcome to CoreTrack API Engine"}

@app.post("/journal")
def create_journal_entry(entry: JournalEntrySchema, db: Session = Depends(get_db)):
    
    # 1. Guard Clause: Check if this user ID even exists in our system before saving!
    user_exists = db.query(models.UserTable).filter(models.UserTable.id == entry.user_id).first()
    if not user_exists:
        return {"status": "error", "message": "Access Denied: Invalid user account account"}

    # 2. Set up our safe fallback default mood
    extracted_mood = "Unknown"
    
    ai_prompt = f"""
    Analyze the emotional sentiment of this journal entry. 
    Respond with exactly ONE word from this list: [Happy, Productive, Anxious, Tired, Peaceful, Sad].
    Do not include punctuation or sentences.
    
    Journal Entry: "{entry.content}"
    """
    
    # 3. Request analysis from our cloud AI engine
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=ai_prompt,
        )
        extracted_mood = response.text.strip()
    except Exception as e:
        print(f"AI Network jam caught safely: {e}")
        extracted_mood = "Calm" # Our safe backup state
        
    # 4. Save EVERYTHING into our physical database row, including the owner's link!
    new_row = models.JournalTable(
        content=entry.content,
        mood=extracted_mood,
        user_id=entry.user_id # <-- Binds this entry securely to our specific user account!
    )
    
    db.add(new_row)
    db.commit()
    db.refresh(new_row)
    
    return {
        "status": "success", 
        "saved_id": new_row.id, 
        "ai_predicted_mood": new_row.mood,
        "owner_email": user_exists.email # Pro proof: pulling the owner's email via our query link!
    }

@app.get("/journal")
def get_all_journal_entries(user_id:int, db:Session=Depends(get_db)):
    personal_entries = db.query(models.JournalTable).filter(models.JournalTable.user_id == user_id).all()
    return personal_entries

@app.post("/register")
def register_user(user_data:UserCreateSchema, db:Session=Depends(get_db)):
    existing_user=db.query(models.UserTable).filter(models.UserTable.email==user_data.email).first()
    if existing_user:
        return{"status":"error", "message": "This email addressis already taken. Try logging in!"}
    
    fake_hash=user_data.password[::-1]
    new_user_row=models.UserTable(
        email=user_data.email,
        hashed_password=fake_hash,
        name=user_data.name 
    )
    db.add(new_user_row)
    db.commit()
    db.refresh(new_user_row)
    return {
        "status": "Account created successfully",
        "message":"User profile initialized perfectly inside the disturbed cluster",
        "user_id": new_user_row.id
        
    }

@app.post("/login")
def login_user(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    db_user = db.query(models.UserTable).filter(models.UserTable.email == user_data.email).first()
    
    if db_user is None:
        return {"status": "error", "message": "Invalid email or password"}
        
    incoming_fake_hash = user_data.password[::-1]
    
    if incoming_fake_hash == db_user.hashed_password:
        return {
            "status": "success", # <-- CHANGED to standard "success" flag!
            "message": f"Welcome back, {db_user.email}!",
            "user_id": db_user.id
        }
    else:
        return {"status": "error", "message": "Invalid email or password"}

@app.get("/journal/analytics")
def get_journal_analytics(user_id:int, db: Session=Depends(get_db)):
    user_entries=db.query(models.JournalTable).filter(models.JournalTable.user_id==user_id).all()
    total_entries=len(user_entries)
    if total_entries==0:
        return{"total_logs": 0, "message": "Log more days to unlock AI diagnostics!"}
    happy_count=0
    anxious_count=0
    tired_count=0

    for entry in user_entries:
        if entry.mood == "Happy":
            happy_count += 1
        elif entry.mood == "Anxious":
            anxious_count += 1
        elif entry.mood == "Tired":
            tired_count += 1

    happy_percentage = (happy_count / total_entries) * 100
    anxious_percentage = (anxious_count / total_entries) * 100

    return {
        "total_days_tracked": total_entries,
        "metrics": {
            "happiness_rate": f"{happy_percentage}%",
            "anxiety_rate": f"{anxious_percentage}%",
            "raw_counts": {
                "happy": happy_count,
                "anxious": anxious_count,
                "tired": tired_count
            }
        }
    }

@app.post("/habits/log")
def log_habit_action(habit_data: HabitCreateSchema, db: Session = Depends(get_db)):
    
    user_exists = db.query(models.UserTable).filter(models.UserTable.id == habit_data.user_id).first()
    if not user_exists:
        return {"status": "error", "message": "Invalid user account authentication token"}

    existing_habit = db.query(models.HabitTable).filter(
        models.HabitTable.name == habit_data.name,
        models.HabitTable.user_id == habit_data.user_id
    ).first()

    if existing_habit:
        existing_habit.streak_count += 1
        db.commit()
        db.refresh(existing_habit)
        active_habit = existing_habit
    else:
        new_habit = models.HabitTable(
            name=habit_data.name,
            streak_count=1,
            user_id=habit_data.user_id
        )
        db.add(new_habit)
        db.commit()
        db.refresh(new_habit)
        active_habit = new_habit

    return {
        "status": "success",
        "habit_name": active_habit.name,
        "current_streak": active_habit.streak_count
    }

@app.get("/user/profile")
def get_user_profile_data(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UserTable).filter(models.UserTable.id == user_id).first()
    
    if not user:
        return {"status": "error", "message": "User profile record not found"}
        
    return {
        "status": "success",
        "id": user.id,
        "email": user.email,
        "name": user.name if user.name else "Anonymous Developer"
    }

class ProfileUpdateSchema(BaseModel):
    user_id: int
    new_name: str

@app.put("/user/profile/update")
def update_user_profile_name(update_data: ProfileUpdateSchema, db: Session = Depends(get_db)):
    user = db.query(models.UserTable).filter(models.UserTable.id == update_data.user_id).first()
    if not user:
        return {"status": "error", "message": "Profile trace record missing."}
        
    user.name = update_data.new_name
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "message": "Global telemetry profile identity string modified.",
        "updated_name": user.name
    }