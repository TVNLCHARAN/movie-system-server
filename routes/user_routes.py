from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import not_
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
# from script import get_links_for_titles, get_links_with_api
import random

router = APIRouter(prefix="/user", tags=["user"])

DATABASE_URL = "sqlite:///../app/database/database.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "cH@r@n$n3h@"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_iso():
    utc = datetime.utcnow()
    return utc.date()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True)
    date_joined = Column(Date, default=get_iso)

class Show(Base):
    __tablename__ = "shows"
    show_id = Column(Integer, primary_key=True)
    title = Column(String)
    listed_in = Column(String)
    release_year = Column(Integer)
    rating = Column(String)
    date_added = Column(String)
    description = Column(String)

class MoviesWatched(Base):
    __tablename__ = "movies_watched"
    watched_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    show_id = Column(Integer, ForeignKey("shows.show_id"))
    watch_date = Column(DateTime, default=get_iso)

class MoviesLiked(Base):
    __tablename__ = "movies_liked"
    liked_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    show_id = Column(Integer, ForeignKey("shows.show_id"))
    liked_date = Column(DateTime, default=get_iso)


class UserUpdate(BaseModel):
    email: str

class ShowIDRequest(BaseModel):
    show_id: int

Base.metadata.create_all(bind=engine)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return db.query(User).filter(User.username == username).first()
    except JWTError:
        raise credentials_exception

@router.post("/add-user/")
def add_user(username: str, password: str, email: str):
    hashed_password = get_password_hash(password)
    try:
        user = User(username=username, password=hashed_password, email=email)
        db.add(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")
    return {"message": "User created successfully"}

@router.put("/update-user-details/")
def update_user_details(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = user_update.email
    db.commit()
    
    updated_user = db.query(User).filter(User.username == current_user.username).first()

    return {"message": "User details updated successfully", "user": updated_user}

@router.post("/add-watched/")
def add_watched(show_data: ShowIDRequest, current_user: User = Depends(get_current_user)):
    watched = MoviesWatched(user_id=current_user.user_id, show_id=show_data.show_id)
    db.add(watched)
    db.commit()
    return {"message": "Added to watched list"}

@router.post("/add-liked/")
def add_liked(show_data: ShowIDRequest, current_user: User = Depends(get_current_user)):
    liked = MoviesLiked(user_id=current_user.user_id, show_id=show_data.show_id)
    db.add(liked)
    db.commit()
    return {"message": "Added to liked list"}

@router.get("/get-movies")
def all_movies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    movies = db.query(Show).all()
    return movies

@router.get("/get-watched/")
def get_watched(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    watched = db.query(MoviesWatched).filter(current_user.user_id == MoviesWatched.user_id).all()
    return watched

@router.get("/get-liked/")
def get_liked(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    liked = db.query(MoviesLiked).filter(current_user.user_id == MoviesLiked.user_id).all()
    return liked

@router.get("/get-genre-{genre}")
def get_by_genre(genre: str,current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    watched_show_ids = db.query(MoviesWatched.show_id).filter(
        MoviesWatched.user_id == current_user.user_id
    ).subquery()
    
    shows = db.query(Show).filter(
        Show.listed_in.ilike(f"%{genre}%"),
        not_(Show.show_id.in_(watched_show_ids))
    ).all()
    # titles = []
    # movies = []
    # for show in shows[:30]:
    #     titles.append(show.title)
    # image_urls = get_links_with_api(titles)
    # for i, show in enumerate(shows[:20]):
    #     movie_data = show.__dict__.copy()
    #     if image_urls[i]:
    #         movie_data["image_url"] = image_urls[i]
    #         movies.append(movie_data)
    # return movies
    return shows[:20]


@router.get("/get-random-movies/")
def get_random_movies():
    movies = db.query(Show).all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found")
    return random.sample(movies, min(15, len(movies)))

@router.get("/get-movies-by-genre/")
def get_movies_by_genre(genre: str):
    movies = db.query(Show).filter(Show.listed_in.contains(genre)).all()
    return movies

@router.get("/get-movies-by-rating/")
def get_movies_by_rating(rating: str):
    movies = db.query(Show).filter(Show.rating == rating).all()
    return movies

@router.get("/get-movies-by-year/")
def get_movies_by_year(year: int):
    movies = db.query(Show).filter(Show.release_year == year).all()
    return movies

@router.post("/login/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user-profile/")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "date_joined": current_user.date_joined,
    }

@router.get("/trending")
def get_trending(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    movies = db.query(Show).all()

    def safe_parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%B %d, %Y")
        except ValueError:
            return datetime.min
    
    sorted_movies = sorted(
        movies,
        key=lambda x: safe_parse_date(x.date_added),
        reverse=True 
    )
    trending = sorted_movies[:10]
    movies_with_images = []
    titles = []

    for movie in trending:
        titles.append(movie.title)

    # image_urls = get_links_for_titles(titles)
    # 10 ['Dick Johnson Is Dead', 'Blood & Water', 'Ganglands', 'Jailbirds New Orleans', 'Kota Factory', 'Midnight Mass', 'My Little Pony: A New Generation', 'Sankofa', 'The Great British Baking Show', 'The Starling']
    trending_urls = ['https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjQb7YZ4-9qByodLASl_gBgDp_Cb67QaSRoA&s',
    'https://m.media-amazon.com/images/M/MV5BYjVlMWUxYzItMmZkOC00YmVlLWE3M2QtMjc2YTZjMWJjOGYyXkEyXkFqcGc@._V1_.jpg',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfP_IcnSVeNIkXlRJHfIDAOGNgsB8_-kYNuw&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRLNvv4b9Qo1FGQFv8OX4r7CeSIVpTTcN9nog&s',
    'https://m.media-amazon.com/images/M/MV5BY2U5MjY1NWEtZDI2MS00NTlhLWEyODQtYzE0MzY3NDUyNzE3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_pDw-HHw_bPMVcKxpNLlRYidnPNpy4wJroQ&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcST-MzoTc760kre5VavlBszYesdvPP7tEtikQ&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHwIswy5S_TG1-VYnS9EsWvuMTfk8PNTShlA&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTnYv_RiokOGFx6iq0olUvZg3rbkUnp4_i_Hg&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQWG_eMkfLTDY-OhqSTWEJEkLerd_ur1uYBng&s']

    # trending_urls = get_links_with_api(titles)
    
    for i, movie in enumerate(trending):
        movie_data = movie.__dict__.copy()
        movie_data["image_url"] = trending_urls[i]
        movies_with_images.append(movie_data)
    return movies_with_images
