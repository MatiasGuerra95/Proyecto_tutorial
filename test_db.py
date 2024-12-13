from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:password@db:5432/mydb"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("¡Conexión exitosa a la base de datos!")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
