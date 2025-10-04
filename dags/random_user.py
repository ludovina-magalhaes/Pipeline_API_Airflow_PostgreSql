from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import psycopg2

# --- Funções ---

def extract_random_user_data(**kwargs):
    """Extrai 100 utilizadores da API Random User e envia via XCom"""
    url = "https://randomuser.me/api/?results=100"
    data = requests.get(url).json()["results"]
    return data  # retorna lista de utilizadores para o XCom

def transform_random_user_data(**kwargs):
    """Transforma uma lista de utilizadores"""
    ti = kwargs['ti']
    users = ti.xcom_pull(task_ids='task1_get_random_user')
    
    transformed_list = []
    for data in users:
        transformed_list.append({
            "user_id": data["login"]["uuid"],
            "gender": data["gender"],
            "title": data["name"]["title"],
            "first_name": data["name"]["first"],
            "last_name": data["name"]["last"],
            "email": data["email"],
            "phone": data["phone"],
            "cell": data["cell"],
            "nat": data["nat"],
            "dob_date": data["dob"]["date"],
            "dob_age": data["dob"]["age"],
            "registered_date": data["registered"]["date"],
            "registered_age": data["registered"]["age"],
            "street_number": data["location"]["street"]["number"],
            "street_name": data["location"]["street"]["name"],
            "city": data["location"]["city"],
            "state": data["location"]["state"],
            "country": data["location"]["country"],
            "postcode": str(data["location"]["postcode"]),
            "latitude": data["location"]["coordinates"]["latitude"],
            "longitude": data["location"]["coordinates"]["longitude"],
            "timezone_offset": data["location"]["timezone"]["offset"],
            "timezone_description": data["location"]["timezone"]["description"],
            "username": data["login"]["username"],
            "password": data["login"]["password"],
            "salt": data["login"]["salt"],
            "md5": data["login"]["md5"],
            "sha1": data["login"]["sha1"],
            "sha256": data["login"]["sha256"],
            "id_name": data["id"]["name"],
            "id_value": data["id"]["value"],
            "picture_large": data["picture"]["large"],
            "picture_medium": data["picture"]["medium"],
            "picture_thumbnail": data["picture"]["thumbnail"],
            "etl_timestamp": datetime.now().isoformat()
        })
    return transformed_list


def load_random_user_postgres(**kwargs):
    """Carrega lista de utilizadores no Postgres"""
    ti = kwargs['ti']
    users = ti.xcom_pull(task_ids='task2_clean_data')  # lista de dicts
    
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="airflow",
            user="airflow",
            password="airflow",
            port=5432
        )
        print("Conexão bem-sucedida!")

        with conn.cursor() as cur:
            # cria tabela se não existir
            cur.execute("""
                CREATE TABLE IF NOT EXISTS random_user_data (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    gender VARCHAR(50),
                    title VARCHAR(50),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    cell VARCHAR(50),
                    nat VARCHAR(10),
                    dob_date TIMESTAMP,
                    dob_age INT,
                    registered_date TIMESTAMP,
                    registered_age INT,
                    city VARCHAR(100),
                    state VARCHAR(100),
                    country VARCHAR(100),
                    street_number INT,
                    street_name VARCHAR(255),
                    postcode VARCHAR(50),
                    latitude VARCHAR(50),
                    longitude VARCHAR(50),
                    timezone_offset VARCHAR(20),
                    timezone_description VARCHAR(255),
                    username VARCHAR(100),
                    password VARCHAR(100),
                    salt VARCHAR(50),
                    md5 VARCHAR(100),
                    sha1 VARCHAR(100),
                    sha256 VARCHAR(100),
                    id_name VARCHAR(50),
                    id_value VARCHAR(50),
                    picture_large TEXT,
                    picture_medium TEXT,
                    picture_thumbnail TEXT,
                    etl_timestamp TIMESTAMP
                )
            """)

            # insere todos os utilizadores
            for data in users:
                cur.execute("""
                    INSERT INTO random_user_data (
                        user_id, gender, title, first_name, last_name, email, phone, cell, nat,
                        dob_date, dob_age, registered_date, registered_age, city, state, country,
                        street_number, street_name, postcode, latitude, longitude, timezone_offset,
                        timezone_description, username, password, salt, md5, sha1, sha256,
                        id_name, id_value, picture_large, picture_medium, picture_thumbnail,
                        etl_timestamp
                    )
                    VALUES (
                        %(user_id)s, %(gender)s, %(title)s, %(first_name)s, %(last_name)s, %(email)s,
                        %(phone)s, %(cell)s, %(nat)s, %(dob_date)s, %(dob_age)s,
                        %(registered_date)s, %(registered_age)s, %(city)s, %(state)s, %(country)s,
                        %(street_number)s, %(street_name)s, %(postcode)s, %(latitude)s, %(longitude)s,
                        %(timezone_offset)s, %(timezone_description)s, %(username)s, %(password)s,
                        %(salt)s, %(md5)s, %(sha1)s, %(sha256)s, %(id_name)s, %(id_value)s,
                        %(picture_large)s, %(picture_medium)s, %(picture_thumbnail)s, %(etl_timestamp)s
                    )
                """, {
                    **data,
                    "dob_date": datetime.fromisoformat(data["dob_date"].replace("Z", "+00:00")),
                    "registered_date": datetime.fromisoformat(data["registered_date"].replace("Z", "+00:00")),
                    "etl_timestamp": datetime.fromisoformat(data["etl_timestamp"])
                })

        conn.commit()
        print(f"{len(users)} utilizadores inseridos com sucesso!")

    except psycopg2.Error as e:
        print(f"Erro ao conectar ou inserir: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# --- DAG ---

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1
}

with DAG(
    dag_id="random_user_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
) as dag:

    task1_get_user = PythonOperator(
        task_id="task1_get_random_user",
        python_callable=extract_random_user_data,
        provide_context=True
    )

    task2_clean_data = PythonOperator(
        task_id="task2_clean_data",
        python_callable=transform_random_user_data,
        provide_context=True
    )

    task3_insert_postgres = PythonOperator(
        task_id="task3_insert_postgres",
        python_callable=load_random_user_postgres,
        provide_context=True
    )

    task1_get_user >> task2_clean_data >> task3_insert_postgres

