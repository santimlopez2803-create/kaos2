// Vista previa del Estudio KAOS: la maqueta cambia según producto, color, diseño y frase
const prenda = document.getElementById("prenda");

if (prenda) {
  const maqueta = document.getElementById("maqueta");
  const producto = document.getElementById("producto");
  const grafico = document.getElementById("grafico");
  const texto = document.getElementById("texto");
  const colorTexto = document.getElementById("color-texto");
  const filaTalla = document.getElementById("fila-talla");

  // Dibujos disponibles (viewBox 24x24, se pintan con el color del texto)
  const dibujos = {
    "Rayo": '<path d="M13 2L4 14h6l-1 8 9-12h-6z" fill="currentColor"/>',
    "Estrella": '<path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z" fill="currentColor"/>',
    "Corazón": '<path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z" fill="currentColor"/>',
    "Llama": '<path d="M12 2s5.5 4.5 5.5 10a5.5 5.5 0 0 1-11 0c0-2 .9-3.4 1.8-4.5.2 1.5 1 2.3 2 2.5C10 8 11 5 12 2z" fill="currentColor"/>',
    "Carita": '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="8.5" cy="10" r="1.5" fill="currentColor"/><circle cx="15.5" cy="10" r="1.5" fill="currentColor"/><path d="M7.5 14.5c1.2 2.2 7.8 2.2 9 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "Corona": '<path d="M3 18L2 7l5 4 5-8 5 8 5-4-1 11z M3 20h18v2H3z" fill="currentColor"/>'
  };
  const coloresTexto = { Blanco: "#ffffff", Negro: "#111111", Amarillo: "#f4c20d", Rojo: "#c62828" };
  const clarosAuto = ["Blanco", "Amarillo", "Rosado"]; // sobre estos colores el texto automático es oscuro

  function actualizar() {
    const elegido = document.querySelector('input[name="color"]:checked');
    const nombreColor = elegido.value;

    // Producto y color de la prenda
    maqueta.dataset.producto = producto.value;
    maqueta.style.setProperty("--c", elegido.dataset.hex);
    document.getElementById("nombre-prenda").textContent = producto.value;

    // La talla solo aplica para camisetas
    filaTalla.style.display = producto.value === "Camiseta" ? "block" : "none";

    // Color del texto y del dibujo
    let tinta = coloresTexto[colorTexto.value];
    if (!tinta) tinta = clarosAuto.includes(nombreColor) ? "#111111" : "#ffffff";
    prenda.style.setProperty("--t", tinta);

    // Tamaño de letra según el largo de la frase
    const largo = texto.value.length;
    prenda.style.setProperty("--fs", largo <= 8 ? 9 : largo <= 14 ? 7 : largo <= 20 ? 5.5 : 4.5);

    // Estampa: el dibujo arriba y la frase abajo
    prenda.innerHTML = "";
    if (dibujos[grafico.value]) {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 0 24 24");
      svg.setAttribute("class", "grafico");
      svg.innerHTML = dibujos[grafico.value];
      prenda.appendChild(svg);
    }
    if (texto.value.trim()) {
      const frase = document.createElement("span");
      frase.textContent = texto.value.toUpperCase();
      prenda.appendChild(frase);
    }
  }

  document.querySelectorAll('input[name="color"]').forEach(function (r) {
    r.addEventListener("change", actualizar);
  });
  [producto, grafico, texto, colorTexto].forEach(function (campo) {
    campo.addEventListener("input", actualizar);
  });
  actualizar();
}
