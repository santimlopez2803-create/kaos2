from flask import Flask, flash, redirect, render_template, request, session, url_for

from carrito import Carrito
from datos import cargar_datos
from models import Diseno, ItemPedido, Pedido, Producto, Usuario, db

# Configuración
app = Flask(__name__)
app.config["SECRET_KEY"] = "kaos-clave-secreta"          
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kaos.db"   # se guarda en la carpeta instance/
db.init_app(app)

PRECIO_PERSONALIZADO = 59900
ESTADOS = ["En preparación", "En camino", "Entregado"]
CATEGORIAS = ["Todos", "Camisetas", "Tazas", "Gorras", "Ofertas"]


# Ayudas para las plantillas
@app.template_filter("cop")
def formato_precio(valor):
    """74900 -> $74.900"""
    return "$" + f"{valor:,}".replace(",", ".")


def usuario_actual():
    id_usuario = session.get("usuario_id")
    if id_usuario:
        return db.session.get(Usuario, id_usuario)
    return None


@app.context_processor
def variables_globales():
    
    return {"usuario": usuario_actual(), "carrito": Carrito(session)}


# Tienda
@app.route("/")
def inicio():
    categoria = request.args.get("categoria", "Todos")
    buscar = request.args.get("q", "")

    consulta = Producto.query
    if categoria == "Ofertas":
        consulta = consulta.filter(Producto.precio_anterior.is_not(None))
    elif categoria != "Todos":
        consulta = consulta.filter_by(categoria=categoria)
    if buscar:
        consulta = consulta.filter(Producto.nombre.ilike("%" + buscar + "%"))

    return render_template(
        "inicio.html",
        productos=consulta.all(),
        destacados=Producto.query.limit(6).all(),
        categorias=CATEGORIAS, categoria=categoria, q=buscar,
        precio_personalizado=PRECIO_PERSONALIZADO)


@app.route("/producto/<int:id>")
def producto(id):
    return render_template("producto.html", p=db.get_or_404(Producto, id))


# Carrito
@app.post("/agregar/<int:id>")
def agregar(id):
    p = db.get_or_404(Producto, id)
    if p.stock <= 0:
        flash("Ese producto está agotado.")
        return redirect(url_for("inicio"))
    Carrito(session).agregar({
        "producto_id": p.id, "nombre": p.nombre, "precio": p.precio,
        "imagen": p.imagen, "talla": request.form.get("talla", ""), "color": ""})
    flash(p.nombre + " se agregó al carrito")
    return redirect(url_for("ver_carrito"))


@app.route("/carrito")
def ver_carrito():
    return render_template("carrito.html")


@app.post("/quitar/<int:posicion>")
def quitar(posicion):
    Carrito(session).quitar(posicion)
    return redirect(url_for("ver_carrito"))


# Personalizar (estudio)
@app.post("/personalizar")
def personalizar():
    tipo = request.form["producto"]
    color = request.form["color"]
    talla = request.form.get("talla", "") if tipo == "Camiseta" else ""
    texto = request.form.get("texto", "").upper()[:25]
    grafico = request.form.get("grafico", "")
    color_texto = request.form.get("color_texto", "Automático")

    usuario = usuario_actual()
    diseno = Diseno(usuario_id=usuario.id if usuario else None, producto=tipo,
                    color=color, talla=talla, texto=texto, grafico=grafico,
                    color_texto=color_texto)
    db.session.add(diseno)
    db.session.commit()

    Carrito(session).agregar({
        "producto_id": None, "nombre": tipo + " personalizada",
        "precio": PRECIO_PERSONALIZADO, "talla": talla, "color": color,
        "imagen": "img/black-sheep.jpg"})
    flash("Tu diseño se agregó al carrito")
    return redirect(url_for("ver_carrito"))


# Hacer el pedido
@app.route("/pedido", methods=["GET", "POST"])
def hacer_pedido():
    carrito = Carrito(session)
    if carrito.cantidad() == 0:
        flash("Tu carrito está vacío.")
        return redirect(url_for("inicio"))

    if request.method == "POST":
        usuario = usuario_actual()
        pedido = Pedido(
            usuario_id=usuario.id if usuario else None,
            nombre=request.form["nombre"], email=request.form["email"],
            telefono=request.form["telefono"], direccion=request.form["direccion"],
            ciudad=request.form["ciudad"], pago=request.form["pago"],
            total=carrito.total())

        for item in carrito.items():
            pedido.items.append(ItemPedido(
                producto_id=item["producto_id"], nombre=item["nombre"],
                precio=item["precio"], talla=item["talla"], color=item["color"]))
            if item["producto_id"]:                      # descontar inventario
                db.session.get(Producto, item["producto_id"]).stock -= 1

        db.session.add(pedido)
        db.session.commit()
        pedido.codigo = "KA-" + str(2000 + pedido.id)    # código fácil de recordar
        db.session.commit()

        carrito.vaciar()
        flash("¡Pedido confirmado! Tu código es " + pedido.codigo)
        return redirect(url_for("seguimiento", codigo=pedido.codigo))

    return render_template("pedido.html")


@app.route("/seguimiento")
def seguimiento():
    codigo = request.args.get("codigo", "").strip().upper()
    pedido = Pedido.query.filter_by(codigo=codigo).first() if codigo else None
    return render_template("seguimiento.html", codigo=codigo, pedido=pedido)


# Cuenta
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        u = Usuario.query.filter_by(email=email).first()
        if u and u.clave_correcta(request.form["clave"]):
            session["usuario_id"] = u.id
            return redirect(url_for("panel"))
        flash("Correo o contraseña incorrectos.")
    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo.")
        else:
            u = Usuario(nombre=request.form["nombre"], email=email)
            u.poner_clave(request.form["clave"])
            db.session.add(u)
            db.session.commit()
            session["usuario_id"] = u.id
            return redirect(url_for("panel"))
    return render_template("registro.html")


@app.route("/salir")
def salir():
    session.pop("usuario_id", None)
    return redirect(url_for("inicio"))


# Panel
@app.route("/panel")
def panel():
    u = usuario_actual()
    if not u:
        return redirect(url_for("login"))

    if u.es_admin():     # el administrador ve todo
        pedidos = Pedido.query.order_by(Pedido.id.desc()).all()
    else:                # el cliente solo ve lo suyo
        pedidos = Pedido.query.filter_by(usuario_id=u.id).order_by(Pedido.id.desc()).all()

    return render_template(
        "panel.html", pedidos=pedidos, estados=ESTADOS,
        productos=Producto.query.all() if u.es_admin() else [],
        usuarios=Usuario.query.all() if u.es_admin() else [],
        disenos=Diseno.query.filter_by(usuario_id=u.id).all())


@app.post("/panel/estado/<int:id>")
def cambiar_estado(id):
    u = usuario_actual()
    if u and u.es_admin():
        db.get_or_404(Pedido, id).estado = request.form["estado"]
        db.session.commit()
    return redirect(url_for("panel"))


@app.post("/panel/stock/<int:id>")
def cambiar_stock(id):
    u = usuario_actual()
    if u and u.es_admin():
        db.get_or_404(Producto, id).stock = int(request.form["stock"])
        db.session.commit()
    return redirect(url_for("panel"))


@app.post("/panel/precio/<int:id>")
def cambiar_precio(id):
    """El administrador cambia el precio de un producto."""
    u = usuario_actual()
    if not (u and u.es_admin()):
        return redirect(url_for("inicio"))
    p = db.get_or_404(Producto, id)
    try:
        precio = int(request.form["precio"])
    except (KeyError, ValueError):
        precio = 0
    if precio <= 0:
        flash("El precio debe ser un número mayor que 0")
        return redirect(url_for("panel"))
    p.precio = precio
    if p.en_oferta():                 # si estaba en oferta, el nuevo precio es el normal
        p.precio_anterior = None
        flash("Nuevo precio de " + p.nombre + ". Se quitó su oferta.")
    else:
        flash("Nuevo precio de " + p.nombre + ": " + formato_precio(precio))
    db.session.commit()
    return redirect(url_for("panel"))


@app.post("/panel/oferta/<int:id>")
def cambiar_oferta(id):
    """El administrador pone o quita una prenda de oferta (descuento en %)."""
    u = usuario_actual()
    if not (u and u.es_admin()):
        return redirect(url_for("inicio"))
    p = db.get_or_404(Producto, id)
    if request.form.get("accion") == "quitar":
        if p.en_oferta():
            p.precio, p.precio_anterior = p.precio_anterior, None
            flash("Quitaste la oferta de " + p.nombre)
    else:
        try:
            descuento = int(request.form["descuento"])
        except (KeyError, ValueError):
            descuento = 0
        if not 1 <= descuento <= 90:
            flash("El descuento debe estar entre 1% y 90%")
            return redirect(url_for("panel"))
        base = p.precio_anterior if p.en_oferta() else p.precio  # siempre se calcula sobre el precio normal
        p.precio_anterior = base
        p.precio = round(base * (100 - descuento) / 100 / 100) * 100  # redondeado a 100 pesos
        flash(p.nombre + " ahora está en oferta (" + str(descuento) + "% de descuento)")
    db.session.commit()
    return redirect(url_for("panel"))


# Arranque
with app.app_context():
    db.create_all()      
    cargar_datos()       

if __name__ == "__main__":
    app.run(debug=True)
