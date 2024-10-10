from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contracts = db.relationship('Contract', backref='worker', lazy=True)

    def __repr__(self):
        return f'<Worker {self.name}>'

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(200), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)

    def __repr__(self):
        return f'<Contract {self.details}>'
