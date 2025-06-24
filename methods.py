# methods.py — Módulo de métodos numéricos
import math
import numpy as np
import sympy

# ------------------------------------------------------------
# 1.  Métodos Unimodales
# ------------------------------------------------------------

def _fibonacci_sequence(n_target):
    """Genera la secuencia de Fibonacci hasta el n-ésimo término."""
    fib_seq = [1, 1]
    while len(fib_seq) <= n_target:
        fib_seq.append(fib_seq[-1] + fib_seq[-2])
    return fib_seq

def metodo_fibonacci(func_str, a, b, objetivo, err_tol):
    """Método de Fibonacci para optimización unimodal."""
    f = eval(f'lambda x: {func_str}', {"math": math, "np": np})
    if a >= b:
        raise ValueError("'a' debe ser menor que 'b'.")

    # Determinar n
    L_inicial = b - a
    ratio = err_tol / L_inicial
    n = 2
    fib_seq_temp = [1, 1]
    while fib_seq_temp[-1] < 1 / ratio:
        fib_seq_temp.append(fib_seq_temp[-1] + fib_seq_temp[-2])
        n += 1
    
    fib_seq = _fibonacci_sequence(n)
    
    historial = []
    L = b - a
    x1 = b - (fib_seq[n-2] / fib_seq[n-1]) * L
    x2 = a + (fib_seq[n-2] / fib_seq[n-1]) * L
    fx1, fx2 = f(x1), f(x2)

    for k in range(n - 2):
        L_k = b - a
        historial.append({"k": k + 1, "a": a, "b": b, "L_k": L_k, "x1": x1, "x2": x2, "fx1": fx1, "fx2": fx2})
        
        # Condición de maximización/minimización
        condicion_min = objetivo == "Minimizar" and fx1 < fx2
        condicion_max = objetivo == "Maximizar" and fx1 > fx2

        if condicion_min or condicion_max:
            b = x2
            x2, fx2 = x1, fx1
            L = b - a
            x1 = b - (fib_seq[n-k-3] / fib_seq[n-k-2]) * L
            fx1 = f(x1)
        else:
            a = x1
            x1, fx1 = x2, fx2
            L = b - a
            x2 = a + (fib_seq[n-k-3] / fib_seq[n-k-2]) * L
            fx2 = f(x2)
    
    x_opt = (a + b) / 2
    f_opt = f(x_opt)
    return historial, (x_opt, f_opt), n

def metodo_razon_dorada(func_str, a, b, objetivo, tol):
    """Método de la razón dorada para optimización unimodal."""
    f = eval(f'lambda x: {func_str}', {"math": math, "np": np})
    if a >= b:
        raise ValueError("'a' debe ser menor que 'b'.")
        
    TAU = (math.sqrt(5) - 1) / 2
    historial = []
    x1, x2 = b - TAU * (b - a), a + TAU * (b - a)
    fx1, fx2 = f(x1), f(x2)
    k = 0
    while (b - a) > tol:
        k += 1
        historial.append({"k":k, "a":a, "b":b, "x1":x1, "x2":x2, "fx1":fx1, "fx2":fx2})
        
        condicion_min = objetivo == "Minimizar" and fx1 < fx2
        condicion_max = objetivo == "Maximizar" and fx1 > fx2

        if condicion_min or condicion_max:
            b, x2, fx2 = x2, x1, fx1
            x1 = b - TAU * (b - a)
            fx1 = f(x1)
        else:
            a, x1, fx1 = x1, x2, fx2
            x2 = a + TAU * (b - a)
            fx2 = f(x2)
            
    x_opt = (a+b)/2
    f_opt = f(x_opt)
    return historial, (x_opt, f_opt)

# ------------------------------------------------------------
# 2.  Métodos Multimodales (Plantillas a completar)
# ------------------------------------------------------------
def metodo_biseccion(f_prime_str, a, b, objetivo, tol):
    f_prime = eval(f'lambda x: {f_prime_str}', {"math": math, "np": np})
    historial = []
    k = 0
    while (b - a) / 2 > tol:
        k += 1
        xm = (a + b) / 2
        fa_prime, fb_prime, fxm_prime = f_prime(a), f_prime(b), f_prime(xm)
        error = abs(b - a)
        historial.append({"k": k, "a": a, "b": b, "xm": xm, "fa_prime": fa_prime, "fb_prime": fb_prime, "fxm_prime": fxm_prime, "error": error})
        if f_prime(a) * fxm_prime < 0:
            b = xm
        else:
            a = xm
    
    x_opt = (a + b) / 2
    return historial, x_opt

def metodo_newton_amortiguado(func_str, x0, objetivo, tol):
    x = sympy.symbols('x')
    f_sym = sympy.sympify(func_str)
    f_prime_sym = sympy.diff(f_sym, x)
    f_double_prime_sym = sympy.diff(f_prime_sym, x)

    f = sympy.lambdify(x, f_sym, modules=['numpy', 'math'])
    f_prime = sympy.lambdify(x, f_prime_sym, modules=['numpy', 'math'])
    
    historial = []
    xk = x0
    k = 0
    while abs(f_prime(xk)) > tol and k < 100:
        fxk = f(xk)
        fxk_prime = f_prime(xk)
        
        alpha = 1.0 # Búsqueda de línea simple (backtracking)
        while True:
            xk_new = xk - alpha * fxk_prime
            cond_min = objetivo == "Minimizar" and f(xk_new) < fxk
            cond_max = objetivo == "Maximizar" and f(xk_new) > fxk
            if cond_min or cond_max:
                break
            alpha /= 2
            if alpha < 1e-8: # Evitar bucle infinito
                raise RuntimeError("La búsqueda de línea no convergió.")

        historial.append({"k": k + 1, "xk": xk, "fxk": fxk, "fxk_prime": fxk_prime, "alpha": alpha, "xk_new": xk_new})
        xk = xk_new
        k += 1

    x_opt = xk
    f_opt = f(x_opt)
    return historial, x_opt, f_opt

# ------------------------------------------------------------
# 3.  Métodos Multivariantes (Plantillas a completar)
# ------------------------------------------------------------
def solve_multivariante(func_str, x1_0, x2_0, objetivo, method, tol):
    if method == 'gradiente':
        x1, x2 = sympy.symbols('x1 x2')
        f_sym = sympy.sympify(func_str)
        
        grad = [sympy.diff(f_sym, x1), sympy.diff(f_sym, x2)]
        f_lambda = sympy.lambdify((x1, x2), f_sym, 'numpy')
        grad_lambda = sympy.lambdify((x1, x2), grad, 'numpy')

        X = np.array([x1_0, x2_0])
        historial = []
        k = 0
        
        signo = -1 if objetivo == "Minimizar" else 1

        while k < 100:
            grad_val = np.array(grad_lambda(X[0], X[1]))
            if np.linalg.norm(grad_val) < tol:
                break

            # Búsqueda de línea simple para k* (alpha)
            alpha = 1.0
            f_current = f_lambda(X[0], X[1])
            while True:
                X_new = X + signo * alpha * grad_val
                f_new = f_lambda(X_new[0], X_new[1])
                cond_min = objetivo == "Minimizar" and f_new < f_current
                cond_max = objetivo == "Maximizar" and f_new > f_current
                if cond_min or cond_max:
                    break
                alpha /= 2
                if alpha < 1e-8:
                    break # Convergencia de alpha
            
            X_new = X + signo * alpha * grad_val
            f_new = f_lambda(X_new[0], X_new[1])
            
            historial.append({
                "k": k + 1, "x1": X[0], "x2": X[1], "f_val": f_current,
                "grad1": grad_val[0], "grad2": grad_val[1],
                "k_val": alpha, "next_x1": X_new[0], "next_x2": X_new[1], "f_new": f_new
            })
            
            X = X_new
            k += 1

        x1_opt, x2_opt = X[0], X[1]
        f_opt = f_lambda(x1_opt, x2_opt)
        return historial, (x1_opt, x2_opt, f_opt)
    else:
        raise NotImplementedError(f"El método '{method}' no está implementado.")