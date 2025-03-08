from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

Base = declarative_base()

class DownloadRequest(Base):
    __tablename__ = 'download_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    music_url = Column(String)
    track_numbers = Column(String)
    gofile_link = Column(String, nullable=True)
    status = Column(String, default='pending')

def init_db(pooling=True):
    """Initialize database with connection pooling"""
    engine = create_engine(
        'sqlite:///music_bot.db',
        poolclass=QueuePool if pooling else None,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)

def add_request(session, user_id, music_url, track_numbers):
    request = DownloadRequest(
        user_id=user_id,
        music_url=music_url,
        track_numbers=track_numbers
    )
    session.add(request)
    session.commit()
    return request.id

def update_gofile_link(session, request_id, link):
    request = session.query(DownloadRequest).filter_by(id=request_id).first()
    request.gofile_link = link
    request.status = 'completed'
    session.commit()

def get_pending_request(session):
    return session.query(DownloadRequest)\
        .filter_by(status='pending')\
        .order_by(DownloadRequest.id)\
        .first()

def cleanup_request(session, request_id):
    request = session.query(DownloadRequest).filter_by(id=request_id).first()
    if request:
        session.delete(request)
        session.commit()

def cleanup_all_requests(session):
    """Delete all requests from database"""
    try:
        session.query(DownloadRequest).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to cleanup database: {str(e)}")

def cleanup_non_indian_requests(session):
    """Remove all requests that don't have Indian region URLs"""
    try:
        requests = session.query(DownloadRequest).filter_by(status='pending').all()
        for request in requests:
            if '/in/album/' not in request.music_url:
                session.delete(request)
        session.commit()
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to cleanup non-Indian requests: {str(e)}")
