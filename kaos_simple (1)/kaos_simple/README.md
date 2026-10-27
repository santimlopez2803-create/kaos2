# KAOS - tienda web (Flask + SQLAlchemy + Jinja) y panel Tkinter

## Cómo ejecutarlo
    pip install -r requirements.txt
    python app.py          -> abre http://127.0.0.1:5000
    python admin_tk.py     -> panel de escritorio (solo administrador)

Cuentas de prueba (clave kaos1234): admin@kaos.co  y  cliente@kaos.co

La base de datos (carpeta `instance/`) se crea sola la primera vez que corre la app.
Si cambias los modelos, borra la carpeta `instance/` para que se cree de nuevo.

## Qué hace cada archivo
- app.py        Rutas de la página (cada @app.route es una pantalla).
- models.py     Las tablas de la base de datos (clases con SQLAlchemy).
- carrito.py    Clase Carrito (guarda los productos en la sesión).
- datos.py      Productos y usuarios de ejemplo.
- templates/    Páginas HTML con Jinja ({{ variable }}, {% for %}, {% if %}).
- static/       style.css, app.js (vista previa del estudio) e img/ (fotos de productos).
- admin_tk.py   Ventana de escritorio con Tkinter.

El administrador puede cambiar precios, stock y ofertas desde /panel (web) o desde admin_tk.py (precio y stock).
