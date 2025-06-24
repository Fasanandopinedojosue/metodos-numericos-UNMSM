# main.py — Compatible con PyScript 2025.5
"""
Numerical Works – Suite de Optimización Web
Frontend en PyScript que muestra tres paneles (unimodal, multimodal,
multivariante) y llama a las rutinas numéricas definidas en methods.py
"""
from pyscript import document
from pyodide.ffi import create_proxy
import methods
import math, numpy as np
import asyncio

# ------------------------------------------------------------
# 1.  Utilidades DOM
# ------------------------------------------------------------
_Q = lambda sel: document.querySelector(sel)

def html(id_: str, content: str, *, append=False):
    el = _Q(f"#{id_}")
    el.innerHTML = el.innerHTML + content if append else content

def add_class(id_, cls):    _Q(f"#{id_}").classList.add(cls)
def remove_class(id_, cls): _Q(f"#{id_}").classList.remove(cls)
def val(id_):               return _Q(f"#{id_}").value
def checked(id_):           return _Q(f"#{id_}").checked

# ------------------------------------------------------------
# 2.  Plantillas HTML (Sin cambios)
# ------------------------------------------------------------
UNIMODAL_HTML = """
<h2>Optimización Unimodal</h2>
<div class='form-grid'>
  <label>f(x) =</label><input id='uni-func' type='text' value='x**2 - 4*x + 7'>
  <label>a</label><input id='uni-a' type='number' value='0'>
  <label>b</label><input id='uni-b' type='number' value='5'>
  <label>ε</label><input id='uni-err' type='number' value='0.001' step='0.0001'>
  <label>Método</label>
  <select id='uni-method'>
    <option value='fibonacci'>Fibonacci</option>
    <option value='razon_dorada'>Razón dorada</option>
  </select>
  <label>Objetivo</label>
  <label><input id='uni-max' type='checkbox'> Maximizar</label>
  <button id='btn-calc-unimodal' class='calc-button'>Calcular ↵</button>
</div>
<div id='result-unimodal'></div>
"""
MULTIMODAL_HTML = """
<h2>Optimización Multimodal</h2>
<div class='form-grid'>
  <label>f(x) =</label><input id='multi-func' type='text' value='x**4 - 14*x**2 + 24*x'>
  <label>ε</label><input id='multi-tol' type='number' value='0.0001' step='0.0001'>
  <label>Método</label>
  <select id='multi-method'>
    <option value='biseccion'>Bisección sobre f'(x)</option>
    <option value='newton'>Newton amortiguado</option>
  </select>
  <div id='multi-extra-biseccion'>
    <label>a</label><input id='multi-a' type='number' value='-5'>
    <label>b</label><input id='multi-b' type='number' value='5'>
    <label>f'(x) =</label><input id='multi-deriv' type='text' value='4*x**3 - 28*x + 24'>
  </div>
  <div id='multi-extra-newton' class='hidden'>
    <label>x₀</label><input id='multi-x0' type='number' value='1'>
  </div>
  <label>Objetivo</label>
  <label><input id='multi-max' type='checkbox'> Maximizar</label>
  <button id='btn-calc-multimodal' class='calc-button'>Calcular ↵</button>
</div>
<div id='result-multimodal'></div>
"""
MULTIVARIANTE_HTML = """
<h2>Optimización Multivariante</h2>
<div class='form-grid'>
  <label>f(x₁,x₂) =</label>
  <input id='mv-func' type='text' value='x1**2 + x2**2 - 4*x1 - 6*x2'>
  <label>x₁⁰</label><input id='mv-x1' type='number' value='0'>
  <label>x₂⁰</label><input id='mv-x2' type='number' value='0'>
  <label>ε</label><input id='mv-tol' type='number' value='0.0001' step='0.0001'>
  <label>Método</label>
  <select id='mv-method'>
    <option value='gradiente'>Gradiente con búsqueda de línea</option>
  </select>
  <label>Objetivo</label>
  <label><input id='mv-max' type='checkbox'> Maximizar</label>
  <button id='btn-calc-multivariante' class='calc-button'>Calcular ↵</button>
</div>
<div id='result-multivariante'></div>
"""

# ------------------------------------------------------------
# 3.  Mostrar paneles y oyentes de eventos
# ------------------------------------------------------------
# <-- CAMBIO: Código formateado correctamente
def _attach_inner_listeners(panel_id):
    if panel_id == "panel-unimodal":
        _Q("#btn-calc-unimodal").addEventListener("click", create_proxy(run_unimodal_web))
    elif panel_id == "panel-multimodal":
        _Q("#btn-calc-multimodal").addEventListener("click", create_proxy(run_multimodal_web))
        _Q("#multi-method").addEventListener("change", create_proxy(handle_multimodal_method_change))
    elif panel_id == "panel-multivariante":
        _Q("#btn-calc-multivariante").addEventListener("click", create_proxy(run_multivariante_web))

# <-- CAMBIO: Código formateado correctamente
async def show_panel(panel_id, html_content):
    all_panels = ["panel-unimodal", "panel-multimodal", "panel-multivariante"]
    for pid in all_panels:
        if pid == panel_id:
            remove_class(pid, "hidden")
            if _Q(f"#{pid}").innerHTML.strip() == "":
                html(pid, html_content)
                await asyncio.sleep(0)
                _attach_inner_listeners(pid)
        else:
            add_class(pid, "hidden")

def handle_multimodal_method_change(evt):
    method = val("multi-method")
    if method == "biseccion":
        remove_class("multi-extra-biseccion", "hidden")
        add_class("multi-extra-newton", "hidden")
    else:
        add_class("multi-extra-biseccion", "hidden")
        remove_class("multi-extra-newton", "hidden")

# ------------------------------------------------------------
# 4.  Helper para tablas de resultados
# ------------------------------------------------------------
def _make_table(headers, keys, rows, info=""):
    table = f"{info}<table class='result-table'><thead><tr><th>"
    table += "</th><th>".join(headers) + "</th></tr></thead><tbody>"
    for row in rows:
        table += "<tr>"
        for k in keys:
            value = row.get(k)
            if isinstance(value, float):
                table += f"<td>{value:.6f}</td>"
            else:
                table += f"<td>{value}</td>"
        table += "</tr>"
    table += "</tbody></table>"
    return table

# ------------------------------------------------------------
# 5.  Controladores de cálculo
# ------------------------------------------------------------
# <-- CAMBIO: Código formateado correctamente
def run_unimodal_web(evt=None):
    result_id = "result-unimodal"
    html(result_id, "")
    try:
        method = val("uni-method")
        func_str = val("uni-func")
        a = float(val("uni-a"))
        b = float(val("uni-b"))
        err_tol = float(val("uni-err"))
        objetivo = "Maximizar" if checked("uni-max") else "Minimizar"
        
        if method == "fibonacci":
            hist, (x_opt, f_opt), n = methods.metodo_fibonacci(func_str, a, b, objetivo, err_tol)
            headers = ["k", "a", "b", "L_k", "x1", "x2", "f(x1)", "f(x2)"]
            keys = ["k", "a", "b", "L_k", "x1", "x2", "fx1", "fx2"]
            info = f"<p>Se determinó n = {n} iteraciones.</p>"
        else:
            hist, (x_opt, f_opt) = methods.metodo_razon_dorada(func_str, a, b, objetivo, err_tol)
            headers = ["k", "a", "b", "x1", "x2", "f(x1)", "f(x2)"]
            keys = ["k", "a", "b", "x1", "x2", "fx1", "fx2"]
            info = ""
        
        table_html = _make_table(headers, keys, hist, info)
        final_html = f"<div class='final-result'>Resultado Óptimo: f({x_opt:.6f}) = {f_opt:.6f}</div>"
        html(result_id, table_html + final_html)
    except Exception as e:
        html(result_id, f"<div class='error-message'>Error: {e}</div>")

# <-- CAMBIO: El resto de las funciones también están formateadas
def run_multimodal_web(evt=None):
    result_id="result-multimodal"
    html(result_id,"")
    try:
        method = val("multi-method")
        func_str = val("multi-func")
        tol = float(val("multi-tol"))
        objetivo = "Maximizar" if checked("multi-max") else "Minimizar"

        if method == "biseccion":
            f_prime_str, a, b = val("multi-deriv"), float(val("multi-a")), float(val("multi-b"))
            hist, x_opt = methods.metodo_biseccion(f_prime_str, a, b, objetivo, tol)
            f_opt = eval(f"lambda x:{func_str}", {"math":math, "np":np})(x_opt)
            headers, keys = ["k","a","b","xm","f'(a)","f'(b)","f'(xm)","Error"], ["k","a","b","xm","fa_prime","fb_prime","fxm_prime","error"]
        else:
            x0 = float(val("multi-x0"))
            hist, x_opt, f_opt = methods.metodo_newton_amortiguado(func_str, x0, objetivo, tol)
            headers, keys = ["k","x_k","f(x_k)","f'(x_k)","α","x_{k+1}"], ["k","xk","fxk","fxk_prime","alpha","xk_new"]
        
        table_html = _make_table(headers, keys, hist)
        final_html = f"<div class='final-result'>Resultado Óptimo: f({x_opt:.6f}) = {f_opt:.6f}</div>"
        html(result_id, table_html + final_html)
    except Exception as e:
        html(result_id, f"<div class='error-message'>Error: {e}</div>")

def run_multivariante_web(evt=None):
    result_id = "result-multivariante"
    html(result_id,"")
    try:
        method = val("mv-method")
        func_str = val("mv-func")
        x1_0, x2_0 = float(val("mv-x1")), float(val("mv-x2"))
        tol = float(val("mv-tol"))
        objetivo = "Maximizar" if checked("mv-max") else "Minimizar"
        
        hist, (x1_opt, x2_opt, f_opt) = methods.solve_multivariante(func_str, x1_0, x2_0, objetivo, method, tol)
        headers = ["k","x₁","x₂","f(X)","∇f₁","∇f₂","α*","x₁'","x₂'","f(X')"]
        keys = ["k","x1","x2","f_val","grad1","grad2","k_val","next_x1","next_x2","f_new"]
        
        table_html = _make_table(headers, keys, hist)
        final_html = f"<div class='final-result'>Resultado Óptimo: f({x1_opt:.6f}, {x2_opt:.6f}) = {f_opt:.6f}</div>"
        html(result_id, table_html + final_html)
    except Exception as e:
        html(result_id,f"<div class='error-message'>Error: {e}</div>")

# ------------------------------------------------------------
# 6.  Configuración de listeners principales
# ------------------------------------------------------------
async def handle_cat1_click(evt):
    await show_panel("panel-unimodal", UNIMODAL_HTML)
async def handle_cat2_click(evt):
    await show_panel("panel-multimodal", MULTIMODAL_HTML)
async def handle_cat3_click(evt):
    await show_panel("panel-multivariante", MULTIVARIANTE_HTML)

def setup_main_listeners():
    _Q("#btn-cat1").addEventListener("click", create_proxy(handle_cat1_click))
    _Q("#btn-cat2").addEventListener("click", create_proxy(handle_cat2_click))
    _Q("#btn-cat3").addEventListener("click", create_proxy(handle_cat3_click))
    print(">>> Listeners principales configurados correctamente.")

# --- Punto de entrada del Script ---
setup_main_listeners()
asyncio.ensure_future(show_panel("panel-unimodal", UNIMODAL_HTML))