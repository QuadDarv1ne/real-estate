from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Enum, DECIMAL, TIMESTAMP, func, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

# Модель для клиента
class Client(db.Model, UserMixin):
    __tablename__ = 'client'

    client_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(255))

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def get_id(self) -> int:
        return self.client_id


# Модель для агента
class Agent(db.Model):
    __tablename__ = 'agent'

    agent_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    commission_rate = db.Column(DECIMAL(5, 2), nullable=False)
    properties = db.relationship('Property', backref='agent', lazy=True)
    transactions = db.relationship('Transaction', backref='agent', lazy=True)

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


# Модель для недвижимости
class Property(db.Model):
    __tablename__ = 'property'

    property_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    property_type = db.Column(Enum('Квартира', 'Дом', 'Таунхаус', 'Коммерческая недвижимость'), nullable=False)
    area = db.Column(DECIMAL(10, 2), nullable=False)
    rooms = db.Column(db.Integer)
    price = db.Column(DECIMAL(15, 2), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(Enum('Продается', 'Сдается', 'Продано', 'Снято'), nullable=False)
    date_added = db.Column(TIMESTAMP, default=func.current_timestamp())
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'))
    images = db.relationship('PropertyImage', backref='property', lazy=True)
    features = db.relationship('PropertyFeature', backref='property', lazy=True)
    transactions = db.relationship('Transaction', backref='property', lazy=True)


# Модель для транзакций
class Transaction(db.Model):
    __tablename__ = 'transaction'

    transaction_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    transaction_date = db.Column(TIMESTAMP, default=func.current_timestamp())
    price = db.Column(DECIMAL(15, 2), nullable=False)
    transaction_type = db.Column(Enum('Продажа', 'Аренда'), nullable=False)
    status = db.Column(Enum('В процессе', 'Завершена', 'Отменена'), nullable=False)


# Модель для изображений недвижимости
class PropertyImage(db.Model):
    __tablename__ = 'property_image'

    image_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)


# Модель для характеристик недвижимости
class PropertyFeature(db.Model):
    __tablename__ = 'property_feature'
    feature_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id'), nullable=False)
    feature_name = db.Column(db.String(255), nullable=False)
    feature_value = db.Column(db.String(255))


# Модель предпочтений клиента
class ClientPreference(db.Model):
    __tablename__ = 'client_preference'

    preference_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    property_type = db.Column(db.String(50))
    min_area = db.Column(DECIMAL(10, 2))
    max_price = db.Column(DECIMAL(15, 2))
    other_preferences = db.Column(db.Text)


# Тестирование соединения с базой данных
def test_database_connection(db_uri: str) -> bool:
    try:
        engine = create_engine(db_uri)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError as e:
        print(f"Ошибка соединения с базой данных: {e}")
        return False


if __name__ == "__main__":
    db_uri = 'mysql+mysqlconnector://root:Qwerty2006@localhost:3306/librarydb?auth_plugin=mysql_native_password'
    if test_database_connection(db_uri):
        print("Соединение с базой данных успешно!")
    else:
        print("Ошибка соединения с базой данных.")
