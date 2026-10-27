"""MODELOS: cada clase es una tabla de la base de datos (SQLAlchemy)."""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    clave_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default="cliente")  # "cliente" o "admin"

    def poner_clave(self, clave):
        # Guardamos la contraseña cifrada, nunca en texto normal
        self.clave_hash = generate_password_hash(clave)

    def clave_correcta(self, clave):
        return check_password_hash(self.clave_hash, clave)

    def es_admin(self):
        return self.rol == "admin"


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(30), nullable=False)  # Camisetas, Tazas...
    precio = db.Column(db.Integer, nullable=False)
    precio_anterior = db.Column(db.Integer)  # si tiene valor, está en oferta
    imagen = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, default="")
    stock = db.Column(db.Integer, default=40)

    def en_oferta(self):
        return self.precio_anterior is not None


class Diseno(db.Model):
    """Una prenda personalizada que creó el cliente."""
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    producto = db.Column(db.String(20))  # Camiseta, Gorra o Taza
    color = db.Column(db.String(20))
    talla = db.Column(db.String(5))
    texto = db.Column(db.String(30))
    grafico = db.Column(db.String(20), default="")      # Rayo, Estrella... (vacío = solo frase)
    color_texto = db.Column(db.String(20), default="Automático")
    fecha = db.Column(db.DateTime, default=datetime.now)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(30))
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(50))
    pago = db.Column(db.String(40))
    estado = db.Column(db.String(30), default="En preparación")
    total = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.now)
    # Un pedido tiene muchos items
    items = db.relationship("ItemPedido", backref="pedido")

    def resumen(self):
        return ", ".join(item.nombre for item in self.items)


class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"))
    producto_id = db.Column(db.Integer)  # vacío si es personalizado
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Integer)
    talla = db.Column(db.String(5))
    color = db.Column(db.String(20))
