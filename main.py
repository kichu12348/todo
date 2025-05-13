from dotenv import load_dotenv

load_dotenv()
from models.todo import Base
from services.db import engine
from fastapi import FastAPI,Depends,HTTPException  
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.db import SessionLocal
from models.todo import User,Todo
from models.schema import UserCreate,UserLogin,Token,TodoCreate,TodoUpdate,TodoDelete
from services.auth import hash_password,verify_password,create_access_token,get_current_user
from datetime import datetime


Base.metadata.create_all(bind=engine)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.post('/api/signup',response_model=Token)
async def signup(user:UserCreate,db:Session=Depends(get_db)):
    check_user = db.query(User).filter(User.username==user.username).first()
    if check_user:
        raise HTTPException(status_code=400,detail='User already exists')
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username,hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={'sub':new_user.username})
    return {'access_token':token,'token_type':'bearer'}

@app.post('/api/login',response_model=Token)
async def login(user:UserLogin,db:Session=Depends(get_db)):
    check_user = db.query(User).filter(User.username==user.username).first()
    if not check_user:
        raise HTTPException(status_code=400,detail='User not found')
    
    password_check = verify_password(user.password,check_user.hashed_password)

    if not password_check:
        raise HTTPException(status_code=400,detail='Incorrect password')
    
    token = create_access_token(data={'sub':check_user.username})
    return {'access_token':token,'token_type':'bearer'}

@app.post('/api/todo')
async def create_todo(todo:TodoCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    new_todo = Todo(title=todo.title,description=todo.description,user_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get('/api/todo')
async def get_todo(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    t_now = datetime.datetime.now()
    todos = db.query(Todo).filter(Todo.user_id==current_user.id).all()

    completed=[]
    pending=[]
    for todo in todos:
        if todo.completed:
            completed.append(todo)
        else:
            pending.append(todo)

    return JSONResponse(content={
        'completed':completed,
        'pending':pending,
        'time_now':t_now
    })

@app.put('/api/todo')
async def update_todo(todo:TodoUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    todo_to_update = db.query(Todo).filter(Todo.id==todo.id,Todo.user_id==current_user.id).first()
    if not todo_to_update:
        raise HTTPException(status_code=404,detail='Todo not found')
    
    if todo.title:
        todo_to_update.title = todo.title
    if todo.description:
        todo_to_update.description = todo.description
    if todo.completed is not None:
        todo_to_update.completed = todo.completed
    if todo.due_time:
        todo_to_update.due_time = todo.due_time

    db.commit()
    db.refresh(todo_to_update)
    return todo_to_update

@app.delete('/api/todo')
async def delete_todo(todo:TodoDelete,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    todo_to_delete = db.query(Todo).filter(Todo.id==todo.id,Todo.user_id==current_user.id).first()
    if not todo_to_delete:
        raise HTTPException(status_code=404,detail='Todo not found')
    
    db.delete(todo_to_delete)
    db.commit()
    return JSONResponse(content={'detail':'Todo deleted successfully'})

@app.get('/')
async def root():
    return JSONResponse(content={'detail':'Welcome to the Tudu API'})