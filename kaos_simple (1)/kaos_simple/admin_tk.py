import tkinter as tk
from tkinter import messagebox, ttk

from app import app, ESTADOS          # importar app también crea la base de datos
from models import Pedido, Producto, Usuario, db

app.app_context().push()              # permite usar la base de datos fuera de Flask


class Ventana(tk.Tk):
    """Ventana principal: primero pide login, luego muestra las pestañas."""

    def __init__(self):
        super().__init__()
        self.title("KAOS - Administración")
        self.mostrar_login()

    def limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------- Login
    def mostrar_login(self):
        self.limpiar()
        self.geometry("320x240")
        marco = ttk.Frame(self, padding=25)
        marco.pack(expand=True)

        ttk.Label(marco, text="KAOS", font=("Arial", 24, "bold")).pack()
        self.email = tk.StringVar(value="admin@kaos.co")
        self.clave = tk.StringVar()
        ttk.Label(marco, text="Correo").pack(anchor="w")
        ttk.Entry(marco, textvariable=self.email, width=30).pack()
        ttk.Label(marco, text="Contraseña").pack(anchor="w")
        ttk.Entry(marco, textvariable=self.clave, show="*", width=30).pack()
        ttk.Button(marco, text="Ingresar", command=self.entrar).pack(pady=12)

    def entrar(self):
        usuario = Usuario.query.filter_by(email=self.email.get().strip().lower()).first()
        if usuario and usuario.clave_correcta(self.clave.get()) and usuario.es_admin():
            self.mostrar_panel()
        else:
            messagebox.showerror("Error", "Datos incorrectos o no eres administrador.")

    # ------------------------------------------------------------- Panel
    def mostrar_panel(self):
        self.limpiar()
        self.geometry("900x500")
        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True)

        self.hacer_pestana_pedidos(pestanas)
        self.hacer_pestana_productos(pestanas)

    # ---- Pestaña 1: pedidos
    def hacer_pestana_pedidos(self, pestanas):
        marco = ttk.Frame(pestanas, padding=10)
        pestanas.add(marco, text="Pedidos")

        self.tabla_pedidos = ttk.Treeview(
            marco, columns=("codigo", "cliente", "total", "estado"), show="headings")
        for columna in ("codigo", "cliente", "total", "estado"):
            self.tabla_pedidos.heading(columna, text=columna.capitalize())
        self.tabla_pedidos.pack(fill="both", expand=True)

        barra = ttk.Frame(marco)
        barra.pack(pady=8)
        self.estado = tk.StringVar(value=ESTADOS[0])
        ttk.Combobox(barra, textvariable=self.estado, values=ESTADOS,
                     state="readonly").pack(side="left", padx=5)
        ttk.Button(barra, text="Cambiar estado", command=self.cambiar_estado).pack(side="left")
        self.cargar_pedidos()

    def cargar_pedidos(self):
        self.tabla_pedidos.delete(*self.tabla_pedidos.get_children())
        for p in Pedido.query.order_by(Pedido.id.desc()).all():
            self.tabla_pedidos.insert("", "end", iid=str(p.id),
                                      values=(p.codigo, p.nombre, p.total, p.estado))

    def cambiar_estado(self):
        elegido = self.tabla_pedidos.selection()
        if not elegido:
            messagebox.showwarning("Aviso", "Selecciona un pedido primero.")
            return
        pedido = db.session.get(Pedido, int(elegido[0]))
        pedido.estado = self.estado.get()
        db.session.commit()
        self.cargar_pedidos()

    # ---- Pestaña 2: productos
    def hacer_pestana_productos(self, pestanas):
        marco = ttk.Frame(pestanas, padding=10)
        pestanas.add(marco, text="Productos")

        self.tabla_productos = ttk.Treeview(
            marco, columns=("nombre", "categoria", "precio", "stock"), show="headings")
        for columna in ("nombre", "categoria", "precio", "stock"):
            self.tabla_productos.heading(columna, text=columna.capitalize())
        self.tabla_productos.pack(fill="both", expand=True)

        barra = ttk.Frame(marco)
        barra.pack(pady=8)
        self.nuevo_stock = tk.StringVar()
        ttk.Label(barra, text="Nuevo stock:").pack(side="left")
        ttk.Entry(barra, textvariable=self.nuevo_stock, width=8).pack(side="left", padx=5)
        ttk.Button(barra, text="Guardar stock", command=self.guardar_stock).pack(side="left")
        self.nuevo_precio = tk.StringVar()
        ttk.Label(barra, text="   Nuevo precio:").pack(side="left")
        ttk.Entry(barra, textvariable=self.nuevo_precio, width=10).pack(side="left", padx=5)
        ttk.Button(barra, text="Guardar precio", command=self.guardar_precio).pack(side="left")
        self.cargar_productos()

    def cargar_productos(self):
        self.tabla_productos.delete(*self.tabla_productos.get_children())
        for p in Producto.query.all():
            self.tabla_productos.insert("", "end", iid=str(p.id),
                                        values=(p.nombre, p.categoria, p.precio, p.stock))

    def guardar_stock(self):
        elegido = self.tabla_productos.selection()
        if not elegido or not self.nuevo_stock.get().isdigit():
            messagebox.showwarning("Aviso", "Selecciona un producto y escribe un número.")
            return
        producto = db.session.get(Producto, int(elegido[0]))
        producto.stock = int(self.nuevo_stock.get())
        db.session.commit()
        self.cargar_productos()

    def guardar_precio(self):
        elegido = self.tabla_productos.selection()
        if not elegido or not self.nuevo_precio.get().isdigit() or int(self.nuevo_precio.get()) <= 0:
            messagebox.showwarning("Aviso", "Selecciona un producto y escribe un precio mayor que 0.")
            return
        producto = db.session.get(Producto, int(elegido[0]))
        producto.precio = int(self.nuevo_precio.get())
        producto.precio_anterior = None      # si estaba en oferta, se quita
        db.session.commit()
        self.cargar_productos()


if __name__ == "__main__":
    Ventana().mainloop()
