import os

class Config:
    # Clave secreta para la seguridad de Flask.
    # ¡IMPORTANTE! En un entorno de producción real, NUNCA uses una cadena simple aquí.
    # Asegúrate de que esta clave sea muy larga, aleatoria y se cargue desde una variable de entorno
    # (por ejemplo, en tu servidor de despliegue) para máxima seguridad.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_super_segura_y_aleatoria_para_tu_app_2025'

    # Configuración de la base de datos MySQL.
    # ¡Mantén esta línea tal cual está si ya estás usando MySQL!
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://u472469844_est11:#Bd00011@srv1006.hstgr.io:3306/u472469844_est11'

     # Configuración de la base de datos MySQL local.
    # ¡IMPORTANTE! Reemplaza 'tu_contraseña_de_root' con la contraseña real que estableciste durante la instalación de MySQL Server.
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/u472469844_est11'
    
    
    # Desactiva el seguimiento de modificaciones de objetos SQLAlchemy para ahorrar recursos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración del modo de depuración de Flask.
    # Ponlo en 'True' cuando estés desarrollando para ver errores y recargas automáticas.
    # ¡PERO SIEMPRE CÁMBIALO A 'False' CUANDO TU APLICACIÓN ESTÉ EN PRODUCCIÓN (en línea)
    # por razones de seguridad!
    DEBUG = True