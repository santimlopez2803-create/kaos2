from models import db, Producto, Usuario

# nombre, categoría, precio, precio anterior, imagen
PRODUCTOS = [
    ("Black Sheep", "Camisetas", 74900, None, "black-sheep.jpg"),
    ("Minimal Vibes", "Camisetas", 69900, None, "minimal-vibes.jpg"),
    ("Retro Gaming", "Camisetas", 79900, None, "retro-gaming.jpg"),
    ("Good Luck", "Camisetas", 64900, 79900, "good-luck.jpg"),
    ("All We Need", "Camisetas", 72900, None, "all-we-need.jpg"),
    ("Three Monkeys", "Camisetas", 76900, None, "three-monkeys.jpg"),
    ("Mugiwara", "Camisetas", 82900, None, "mugiwara.jpg"),
    ("Bad Boys", "Camisetas", 74900, None, "bad-boys.jpg"),
    ("Pinky & The Brain", "Tazas", 34900, None, "pinky-brain.jpg"),
    ("Manchester City", "Tazas", 32900, None, "manchester-city.jpg"),
    ("Stitch", "Tazas", 34900, None, "stitch.jpg"),
    ("Clásicos del fútbol", "Tazas", 39900, None, "clasicos-futbol.jpg"),
    ("Gorra Kaos Piedra", "Gorras", 54900, None, "gorra-kaos-piedra.jpg"),
    ("Gorra Kaos Negra", "Gorras", 54900, None, "gorra-kaos-negra.jpg"),
    ("Gorra Kaos Azul Marino", "Gorras", 54900, None, "gorra-kaos-azul-marino.jpg"),
    ("Gorra Kaos Oliva", "Gorras", 54900, None, "gorra-kaos-oliva.jpg"),
    ("Gorra Kaos Roja", "Gorras", 54900, None, "gorra-kaos-roja.jpg"),
    ("Gorra Kaos Hueso", "Gorras", 54900, None, "gorra-kaos-hueso.jpg"),
]

DESCRIPCION = {
    "Camisetas": "Camiseta oversize en algodón premium. Estampado de alta definición y costuras reforzadas.",
    "Tazas": "Taza de cerámica con impresión envolvente y acabado brillante.",
    "Gorras": "Gorra snapback con el logo Kaos bordado en relieve. Ajuste regulable.",
}


def cargar_datos():
    if Producto.query.count() == 0:
        for nombre, categoria, precio, anterior, imagen in PRODUCTOS:
            db.session.add(Producto(
                nombre=nombre, categoria=categoria, precio=precio,
                precio_anterior=anterior, imagen="img/" + imagen,
                descripcion=DESCRIPCION[categoria]))

    if Usuario.query.count() == 0:
        admin = Usuario(nombre="Administrador", email="admin@kaos.co", rol="admin")
        admin.poner_clave("kaos1234")
        cliente = Usuario(nombre="Cliente Demo", email="cliente@kaos.co")
        cliente.poner_clave("kaos1234")
        db.session.add_all([admin, cliente])

    db.session.commit()
