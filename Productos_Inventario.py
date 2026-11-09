import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema de Inventario y Ventas", page_icon="📦", layout="wide")

# 1. Inicialización del inventario en session_state
if "inventario" not in st.session_state:
    data_inicial = {
        "ID": [1, 2, 3, 4, 5],
        "Producto": ["Camiseta Algodón Básica", "Pantalón Jeans Slim Fit", "Zapatillas Deportivas",
                     "Gorra Casual Urbana", "Reloj Minimalista"],
        "Clasificación": ["Ropa", "Ropa", "Calzado", "Accesorios", "Accesorios"],
        "Costo Unitario ($)": [8.00, 22.00, 35.00, 5.50, 40.00],
        "Precio Venta ($)": [18.50, 49.99, 79.90, 14.99, 95.00],
        "Stock Bodega": [45, 12, 4, 30, 2]
    }
    st.session_state.inventario = pd.DataFrame(data_inicial)

if "carrito" not in st.session_state:
    st.session_state.carrito = []

# Referencia rápida al DataFrame
df = st.session_state.inventario

st.title("📦 Sistema de Contabilidad y Control de Inventario")

# Menú lateral
menu = st.sidebar.radio("Navegación", ["🔍 Buscador & Cotizador", "📋 Gestión de Inventario", "📈 Resumen Financiero"])

# ==============================================================================
# MÓDULO 1: BUSCADOR & COTIZADOR (SELECCIÓN CON PRECIO, + / - Y STOCK)
# ==============================================================================
if menu == "🔍 Buscador & Cotizador":
    st.header("Buscador de Productos y Control de Salidas")

    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.subheader("1. Buscar y Seleccionar Producto")

        # Filtro de búsqueda por nombre o categoría
        busqueda = st.text_input("🔍 Escribe el nombre o categoría del producto:",
                                 placeholder="Ej. Camiseta, Ropa, Reloj...")

        # Filtrado dinámico
        df_filtrado = df.copy()
        if busqueda.strip():
            df_filtrado = df_filtrado[
                df_filtrado["Producto"].str.contains(busqueda, case=False, na=False) |
                df_filtrado["Clasificación"].str.contains(busqueda, case=False, na=False)
                ]

        if df_filtrado.empty:
            st.warning("No se encontraron productos que coincidan con la búsqueda.")
        else:
            # Lista desplegable para seleccionar el producto encontrado
            opciones_productos = df_filtrado["Producto"].tolist()
            prod_seleccionado_nombre = st.selectbox("Selecciona un producto de la lista:", opciones_productos)

            # Obtener datos del producto seleccionado
            idx = df[df["Producto"] == prod_seleccionado_nombre].index[0]
            precio_unitario = df.loc[idx, "Precio Venta ($)"]
            stock_bodega = int(df.loc[idx, "Stock Bodega"])
            categoria = df.loc[idx, "Clasificación"]
            prod_id = int(df.loc[idx, "ID"])

            st.markdown("---")
            st.subheader("2. Detalle del Producto")

            # Tarjetas de información: Precio Unitario y Stock en Bodega
            m1, m2, m3 = st.columns(3)
            m1.metric("Categoría", categoria)
            m2.metric("Precio Unitario", f"${precio_unitario:.2f}")
            m3.metric("Stock en Bodega", f"{stock_bodega} unids", delta="¡Stock Bajo!" if stock_bodega < 5 else None,
                      delta_color="inverse")

            # Selector de cantidad con botones + y -
            st.write("#### Cantidad deseada:")

            # Clave dinámica para reiniciar la cantidad si se cambia de producto
            key_qty = f"qty_{prod_id}"
            if key_qty not in st.session_state:
                st.session_state[key_qty] = 1

            col_btn_menos, col_num, col_btn_mas, col_espacio = st.columns([1, 2, 1, 4])

            with col_btn_menos:
                if st.button("➖", key=f"btn_sub_{prod_id}", use_container_width=True):
                    if st.session_state[key_qty] > 1:
                        st.session_state[key_qty] -= 1
                        st.rerun()

            with col_num:
                st.markdown(f"<h3 style='text-align: center; margin: 0;'>{st.session_state[key_qty]}</h3>",
                            unsafe_allow_html=True)

            with col_btn_mas:
                if st.button("➕", key=f"btn_add_{prod_id}", use_container_width=True):
                    if st.session_state[key_qty] < stock_bodega:
                        st.session_state[key_qty] += 1
                        st.rerun()
                    else:
                        st.error(f"Solo hay {stock_bodega} unidades en bodega.")

            cantidad_seleccionada = st.session_state[key_qty]

            # Botón para agregar al carrito
            if st.button("🛒 Agregar a la Cotización", type="primary", use_container_width=True):
                if stock_bodega == 0:
                    st.error("Producto agotado en bodega.")
                else:
                    # Comprobar si ya existe en la cotización
                    existe = False
                    for item in st.session_state.carrito:
                        if item["id"] == prod_id:
                            if item["cantidad"] + cantidad_seleccionada > stock_bodega:
                                st.error("No puedes superar el stock disponible en bodega.")
                            else:
                                item["cantidad"] += cantidad_seleccionada
                                st.success(f"Se agregaron {cantidad_seleccionada} unidades más a la cotización.")
                            existe = True
                            break
                    if not existe:
                        st.session_state.carrito.append({
                            "id": prod_id,
                            "producto": prod_seleccionado_nombre,
                            "precio": precio_unitario,
                            "cantidad": cantidad_seleccionada
                        })
                        st.success(f"¡{prod_seleccionado_nombre} agregado a la cotización!")
                    st.rerun()

    with col_der:
        st.subheader("📋 Cotización / Resumen")

        if not st.session_state.carrito:
            st.info("La lista está vacía. Selecciona un producto para agregar.")
        else:
            total_cotizacion = 0.0
            for idx_c, item in enumerate(st.session_state.carrito):
                subtotal_item = item["precio"] * item["cantidad"]
                total_cotizacion += subtotal_item

                c_item1, c_item2 = st.columns([3, 1])
                with c_item1:
                    st.write(f"**{item['producto']}**")
                    st.caption(f"${item['precio']:.2f} x {item['cantidad']} = **${subtotal_item:.2f}**")
                with c_item2:
                    if st.button("🗑️", key=f"del_{idx_c}"):
                        st.session_state.carrito.pop(idx_c)
                        st.rerun()
                st.markdown("---")

            iva = total_cotizacion * 0.12
            total_final = total_cotizacion + iva

            st.write(f"**Subtotal:** ${total_cotizacion:.2f}")
            st.write(f"**IVA (12%):** ${iva:.2f}")
            st.markdown(f"### **Total:** `${total_final:.2f}`")

            if st.button("✅ Registrar Salida de Bodega", type="primary", use_container_width=True):
                for item in st.session_state.carrito:
                    idx_inv = df[df["ID"] == item["id"]].index[0]
                    st.session_state.inventario.loc[idx_inv, "Stock Bodega"] -= item["cantidad"]

                st.session_state.carrito = []
                st.balloons()
                st.success("¡Salida de bodega registrada con éxito!")
                st.rerun()

            if st.button("Vaciar Lista", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

# ==============================================================================
# MÓDULO 2: GESTIÓN DE INVENTARIO
# ==============================================================================
elif menu == "📋 Gestión de Inventario":
    st.header("Catálogo General de Inventario")

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("➕ Agregar Nuevo Producto")
    with st.form("nuevo_prod_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            nombre = st.text_input("Nombre del Producto")
            cat = st.text_input("Categoría / Clasificación")
        with c2:
            costo = st.number_input("Costo Unitario ($)", min_value=0.0, format="%.2f")
            precio = st.number_input("Precio Venta ($)", min_value=0.0, format="%.2f")
        with c3:
            stock = st.number_input("Stock Inicial en Bodega", min_value=0, step=1)

        guardar = st.form_submit_button("Guardar en Inventario")
        if guardar:
            if nombre.strip() == "" or cat.strip() == "":
                st.error("Por favor completa el nombre y la categoría.")
            else:
                nuevo_id = int(df["ID"].max() + 1) if not df.empty else 1
                nuevo_registro = pd.DataFrame({
                    "ID": [nuevo_id],
                    "Producto": [nombre],
                    "Clasificación": [cat],
                    "Costo Unitario ($)": [costo],
                    "Precio Venta ($)": [precio],
                    "Stock Bodega": [int(stock)]
                })
                st.session_state.inventario = pd.concat([df, nuevo_registro], ignore_index=True)
                st.success(f"Producto '{nombre}' agregado exitosamente.")
                st.rerun()

# ==============================================================================
# MÓDULO 3: RESUMEN FINANCIERO
# ==============================================================================
elif menu == "📈 Resumen Financiero":
    st.header("Resumen Financiero e Inventario")

    inversion_total = (df["Costo Unitario ($)"] * df["Stock Bodega"]).sum()
    venta_estimada = (df["Precio Venta ($)"] * df["Stock Bodega"]).sum()
    ganancia_potencial = venta_estimada - inversion_total
    productos_bajo_stock = len(df[df["Stock Bodega"] < 5])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Inversión (Costo Total)", f"${inversion_total:,.2f}")
    m2.metric("Venta Total Estimada", f"${venta_estimada:,.2f}")
    m3.metric("Ganancia Potencial", f"${ganancia_potencial:,.2f}")
    m4.metric("Items con Stock Bajo (<5)", productos_bajo_stock)

    st.markdown("---")
    st.subheader("Desglose del Inventario por Categoría")

    df["Valor Costo Total"] = df["Costo Unitario ($)"] * df["Stock Bodega"]
    df["Valor Venta Total"] = df["Precio Venta ($)"] * df["Stock Bodega"]

    resumen_cat = df.groupby("Clasificación")[
        ["Stock Bodega", "Valor Costo Total", "Valor Venta Total"]].sum().reset_index()
    st.dataframe(resumen_cat, use_container_width=True, hide_index=True)