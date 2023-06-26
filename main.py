from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from auth import create_access_token, authenticate_user, get_password_hash, get_user, secret_key, jwt, algorithm, JWTError
from models import User, Conversation
from summarizer import Summarizer

app = FastAPI()
security = HTTPBearer()

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


def generate_summary(text, num_sentences=3):
    # Initialize the Summarizer
    model = Summarizer()

    # Generate the summary
    summary = model(text, num_sentences=num_sentences)

    return summary


# Dependency for getting the current user based on the token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user(token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Routes
@app.post("/login")
def login(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/conversations")
def get_user_conversations(current_user: User = Depends(get_current_user)):
    return {"conversations": current_user.conversations}


@app.post("/conversations")
def create_user_conversation(text: str, current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    summary = generate_summary(text)
    conversation = Conversation(text=text, summary=summary, user_id=current_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    session.close()
    return {"message": "Conversation created successfully", "conversation": conversation}


@app.post("/conversations/{conversation_id}/parts")
def add_conversation_part(conversation_id: int, part_text: str, current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    conversation = session.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation.text += part_text
    session.commit()
    session.close()
    return {"message": "Conversation part added successfully"}


@app.delete("/conversations/{conversation_id}")
def delete_user_conversation(conversation_id: int, current_user: User = Depends(get_current_user)):
    session = SessionLocal()
    conversation = session.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    session.delete(conversation)
    session.commit()
    session.close()
    return {"message": "Conversation deleted successfully"}