#base de datos y funciones
import sqlite3
import sys
from typing import Self
import bcrypt
from datetime import datetime

# Conexión a la base de datos
conn = sqlite3.connect('banco.db')
c = conn.cursor()

# Creación de la tabla de usuarios
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             nombre TEXT NOT NULL,
             contrasena TEXT NOT NULL,
             saldo REAL NOT NULL,
             fecha_apertura TEXT NOT NULL)''')

conn.commit()
conn.close()

# Funciones de seguridad
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

#clase

class Cuenta:
    def __init__(self, cliente, saldo):
        self.cliente = cliente
        self.saldo = saldo
        self.fecha_apertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.numero = self.crear_cuenta()

    def crear_cuenta(self):
        conn = sqlite3.connect('banco.db')
        c = conn.cursor()
        c.execute('''INSERT INTO usuarios (nombre, contrasena, saldo, fecha_apertura) 
                     VALUES (?, ?, ?, ?)''', (self.cliente, hash_password('default'), self.saldo, self.fecha_apertura))
        conn.commit()
        cuenta_id = c.lastrowid
        conn.close()
        return cuenta_id

    def depositar(self, monto):
        if monto < 0:
            print("ERROR: el monto no puede ser negativo")
        else:
            self.saldo += monto
            self.actualizar_saldo()
            print(f"Se depositó exitosamente {monto}$ en la cuenta {self.numero}. Su nuevo saldo es {self.saldo}$")

    def retirar(self, monto):
        if monto < 0:
            print("ERROR: el monto no puede ser negativo")
        elif monto > self.saldo:
            print("ERROR: fondo insuficiente")
        else:
            self.saldo -= monto
            self.actualizar_saldo()
            print(f"Se retiró exitosamente {monto}$ de la cuenta {self.numero}. Su nuevo saldo es de: {self.saldo}$")

    def transferir(self, monto, otra_cuenta):
        if monto < 0:
            print("ERROR: el monto no puede ser negativo")
        elif monto > self.saldo:
            print("ERROR: fondo insuficiente")
        else:
            conn = sqlite3.connect('banco.db')
            c = conn.cursor()
            c.execute('SELECT saldo FROM usuarios WHERE id = ?', (otra_cuenta,))
            result = c.fetchone()
            if result:
                self.saldo -= monto
                nuevo_saldo_destino = result[0] + monto
                c.execute('UPDATE usuarios SET saldo = ? WHERE id = ?', (nuevo_saldo_destino, otra_cuenta))
                self.actualizar_saldo()
                conn.commit()
                print(f"Se transfirió {monto}$ de la cuenta nro: {self.numero} a la cuenta nro: {otra_cuenta}")
            else:
                print("ERROR: cuenta destino no existente")
            conn.close()

    def actualizar_saldo(self):
        conn = sqlite3.connect('banco.db')
        c = conn.cursor()
        c.execute('UPDATE usuarios SET saldo = ? WHERE id = ?', (self.saldo, self.numero))
        conn.commit()
        conn.close()

    def get_saldo(self):
        return self.saldo
    
    #interfaz 
    import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class BancoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sistema Bancario')
        self.setGeometry(100, 100, 280, 220)
        
        layout = QVBoxLayout()

        self.menu_button = QPushButton('Menú Principal')
        self.menu_button.clicked.connect(self.open_menu_window)
        layout.addWidget(self.menu_button)

        self.setLayout(layout)

    def open_menu_window(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Menú Principal')
        self.setGeometry(100, 100, 280, 220)
        
        layout = QVBoxLayout()

        self.registro_button = QPushButton('Registrarse')
        self.registro_button.clicked.connect(self.open_registro_window)
        layout.addWidget(self.registro_button)

        self.login_button = QPushButton('Iniciar Sesión')
        self.login_button.clicked.connect(self.open_login_window)
        layout.addWidget(self.login_button)

        self.back_button = QPushButton('Volver')
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def open_registro_window(self):
        self.registro_window = RegistroWindow()
        self.registro_window.show()
        self.close()

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def go_back(self):
        self.banco_app = BancoApp()
        self.banco_app.show()
        self.close()

class RegistroWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Registro de Usuario')
        self.setGeometry(100, 100, 280, 220)
        
        layout = QVBoxLayout()

        self.nombre_label = QLabel('Nombre:')
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_label)
        layout.addWidget(self.nombre_input)

        self.contrasena_label = QLabel('Contraseña:')
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.contrasena_label)
        layout.addWidget(self.contrasena_input)

        self.saldo_label = QLabel('Saldo Inicial:')
        self.saldo_input = QLineEdit()
        layout.addWidget(self.saldo_label)
        layout.addWidget(self.saldo_input)

        self.registrar_button = QPushButton('Registrar')
        self.registrar_button.clicked.connect(self.registrar)
        layout.addWidget(self.registrar_button)

        self.back_button = QPushButton('Volver')
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def registrar(self):
        nombre = self.nombre_input.text()
        contrasena = self.contrasena_input.text()
        saldo = float(self.saldo_input.text())

        # Conexión a la base de datos
        conn = sqlite3.connect('banco.db')
        c = conn.cursor()
        
        # Hash de la contraseña
        hashed_contrasena = hash_password(contrasena)
        
        # Inserción del usuario
        c.execute('''INSERT INTO usuarios (nombre, contrasena, saldo, fecha_apertura) 
                     VALUES (?, ?, ?, ?)''', (nombre, hashed_contrasena, saldo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Registro', 'Usuario registrado con éxito!')
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def go_back(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Iniciar Sesión')
        self.setGeometry(100, 100, 280, 170)
        
        layout = QVBoxLayout()

        self.nombre_label = QLabel('Nombre:')
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_label)
        layout.addWidget(self.nombre_input)

        self.contrasena_label = QLabel('Contraseña:')
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.contrasena_label)
        layout.addWidget(self.contrasena_input)

        self.login_button = QPushButton('Iniciar Sesión')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.back_button = QPushButton('Volver')
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def login(self):
        nombre = self.nombre_input.text()
        contrasena = self.contrasena_input.text()
        
        # Conexión a la base de datos
        conn = sqlite3.connect('banco.db')
        c = conn.cursor()

        # Buscar el usuario en la base de datos
        c.execute('SELECT id, contrasena, saldo FROM usuarios WHERE nombre = ?', (nombre,))
        result = c.fetchone()
        
        if result and check_password(result[1], contrasena):
            QMessageBox.information(self, 'Login', f'Bienvenido, {nombre}!')
            self.open_transaccion_window(result[0], result[2])
        else:
            QMessageBox.warning(self, 'Login', 'Nombre o contraseña incorrectos')
        
        conn.close()

    def open_transaccion_window(self, cuenta_id, saldo):
        self.transaccion_window = TransaccionWindow(cuenta_id, saldo)
        self.transaccion_window.show()
        self.close()

    def go_back(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

class TransaccionWindow(QWidget):
    def __init__(self, cuenta_id, saldo):
        super().__init__()
        self.cuenta_id = cuenta_id
        self.saldo = saldo
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Realizar Transacción')
        self.setGeometry(100, 100, 280, 220)
        
        layout = QVBoxLayout()

        self.saldo_label = QLabel(f'Saldo Actual: {self.saldo}$')
        layout.addWidget(self.saldo_label)

        self.monto_label = QLabel('Monto:')
        self.monto_input = QLineEdit()
        layout.addWidget(self.monto_label)
        layout.addWidget(self.monto_input)

        self.depositar_button = QPushButton('Depositar')
        self.depositar_button.clicked.connect(self.depositar)
        layout.addWidget(self.depositar_button)

        self.retirar_button = QPushButton('Retirar')
        self.retirar_button.clicked.connect(self.retirar)
        layout.addWidget(self.retirar_button)

        self.transferir_label = QLabel('Cuenta Destino:')
        self.transferir_input = QLineEdit()
        layout.addWidget(self.transferir_label)
        layout.addWidget(self.transferir_input)

        self.transferir_button = QPushButton('Transferir')
        self.transferir_button.clicked.connect(self.transferir)
        layout.addWidget(self.transferir_button)

        #añadido boton para actualizar el saldo
        self.actualizar_button = QPushButton('Actualizar Saldo')
        self.actualizar_button.clicked.connect(self.actualizar_saldo)
        layout.addWidget(self.actualizar_button)


        self.back_button = QPushButton('Volver')
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def depositar(self):
        texto_monto = self.monto_input.text()
        if texto_monto:  # Verifica si el texto no está vacío
            try:
                monto = float(texto_monto)
                self.saldo += monto
                self.actualizar_saldo()
                print(f"Depositando {monto}$")
            except ValueError:
                print("El valor ingresado no es un número válido.")
        else:
            print("Por favor, ingresa un monto.")
            #Este código verifica si texto_monto no está vacío antes de intentar 
            #convertirlo a un flotante y maneja el caso en que el valor ingresado no sea un número válido. 

    def retirar(self):
        texto_monto = self.monto_input.text()
        if texto_monto:  # Verifica si el texto no está vacío
            try:
                monto = float(texto_monto)
                if monto <= self.saldo:
                    self.saldo -= monto
                    self.actualizar_saldo()
                    print(f"Retirando {monto}$")
                else:
                    print("Saldo insuficiente.")
            except ValueError:
                print("El valor ingresado no es un número válido.")
        else:
            print("Por favor, ingresa un monto.")

            #Este código verifica si texto_monto no está vacío antes de intentar 
            #convertirlo a un flotante y maneja el caso en que el valor ingresado no sea un número válido. 
    def transferir(self):
        texto_monto = self.monto_input.text()
        if texto_monto:  # Verifica si el texto no está vacío
            try:
                monto = float(texto_monto)
                cuenta_destino = self.transferir_input.text()
                if monto <= self.saldo:
                    self.saldo -= monto
                    self.actualizar_saldo()
                    print(f"Transfiriendo {monto}$ a la cuenta {cuenta_destino}")
                else:
                    print("Saldo insuficiente.")
            except ValueError:
                print("El valor ingresado no es un número válido.")
        else:
            print("Por favor, ingresa un monto.")
            #Este código verifica si texto_monto no está vacío antes de intentar 
            #convertirlo a un flotante y maneja el caso en que el valor ingresado no sea un número válido. 

        #definimos el metodo para actualizar la etiqueta del monto luego de cada transaccion.
    def actualizar_saldo(self):
        conn = sqlite3.connect('banco.db')
        c = conn.cursor()
        c.execute('UPDATE usuarios SET saldo = ? WHERE id = ?', (self.saldo, self.cuenta_id))
        conn.commit()
        conn.close()
        self.saldo_label.setText(f'Saldo Actual: {self.saldo}$')

    def go_back(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BancoApp()
    ex.show()
    sys.exit(app.exec_())