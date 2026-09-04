from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text , Date , ForeignKey , UniqueConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint

Base=declarative_base()

class Expenseschema(Base):
    __tablename__ = 'Expense'

    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False) 
    amount = Column(Integer,nullable=False)
    date = Column(Date,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    user_id=Column(Integer,ForeignKey("Users.user_id",ondelete="CASCADE"),nullable=False)
    category_id=Column(Integer,ForeignKey('category.category_id',ondelete='CASCADE'),nullable=True) # nullable is set to TRUE bcz not every expense needs an id and if nullable is FALSE user has to mentioon category every time they make an expense
    

    user = relationship("UserSchema")
    category = relationship("CategorySchema")


class UserSchema(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False)
    password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))


class CategorySchema(Base):
    __tablename__='category'
    
    category_id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    user_id=Column(Integer,ForeignKey("Users.user_id",ondelete="CASCADE"),nullable=False) 

    user = relationship("UserSchema")

    __table_args__=(
        UniqueConstraint('user_id','name',name='name_userid'),
    )

