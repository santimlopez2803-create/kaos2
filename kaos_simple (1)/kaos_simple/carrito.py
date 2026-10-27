
class Carrito:
    def __init__(self, sesion):
        self.sesion = sesion

    def items(self):
        return self.sesion.get("carrito", [])

    def agregar(self, item):
        lista = self.items()
        lista.append(item)
        self.sesion["carrito"] = lista

    def quitar(self, posicion):
        lista = self.items()
        if 0 <= posicion < len(lista):
            lista.pop(posicion)
        self.sesion["carrito"] = lista

    def vaciar(self):
        self.sesion["carrito"] = []

    def cantidad(self):
        return len(self.items())

    def total(self):
        return sum(item["precio"] for item in self.items())
