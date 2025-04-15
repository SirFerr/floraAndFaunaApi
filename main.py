from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, Integer, String, Text, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from passlib.context import CryptContext
from typing import List, Optional
import uvicorn

DATABASE_URL = "sqlite:///./flora_fauna.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# ==================== MODELS ====================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    scientific_name = Column(String)
    description = Column(Text)
    type = Column(String)  # flora/fauna
    image_url = Column(String)  # ссылка на изображение

Base.metadata.create_all(bind=engine)

# ==================== UTILS ====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# ==================== AUTH ====================
@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created", "user_id": new_user.id}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # В реальных условиях вернем JWT
    return {"access_token": user.email, "token_type": "bearer"}

# ==================== SPECIES ====================
@app.post("/species")
def create_species(name: str, scientific_name: str, description: str, type: str, image_url: str, db: Session = Depends(get_db)):
    existing = db.query(Species).filter(Species.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Species already exists")
    new_species = Species(
        name=name,
        scientific_name=scientific_name,
        description=description,
        type=type,
        image_url=image_url
    )
    db.add(new_species)
    db.commit()
    db.refresh(new_species)
    return new_species

@app.get("/species/search")
def search_species(name: str, db: Session = Depends(get_db)):
    results = db.query(Species).filter(Species.name.ilike(f"%{name}%")).all()
    return results

@app.get("/species/{species_id}")
def get_species(species_id: int, db: Session = Depends(get_db)):
    species = db.query(Species).filter(Species.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return species

@app.delete("/species/{species_id}")
def delete_species(species_id: int, db: Session = Depends(get_db)):
    species = db.query(Species).filter(Species.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    db.delete(species)
    db.commit()
    return {"msg": "Species deleted"}

# ==================== RUN ====================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
