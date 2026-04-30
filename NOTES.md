# NOTES.md — Lecciones del Debugging de instagrapi (B2C)
## Lo que este proyecto intentó (y por qué falló)

---

## Errores recurrentes en TODOS los scripts de debug

### 1.  bloquea la EC2
**Error:** Todos los scripts (smoketest.py, run_extraction.py, etc.) usaban  para pedir el sessionid.
**Resultado:** El proceso se cuelga indefinidamente en EC2 (sin TTY). Nunca ejecuta nada útil.
**Fix:** Leer de  via  o de  en disco. Ver .

### 2. Atributo incorrecto:  → 
**Error:**  no existe en instagrapi 2.4.4.
**Resultado:**  en runtime al intentar imprimir el conteo.
**Fix:** Usar  (sin 's').

### 3.  no existe en instagrapi 2.4.4
**Error:** Llamar  al final causa .
**Fix:** Simplemente no llamarlo. La sesión se cierra al terminar el proceso.

### 4.  no funciona
**Error:** Asignar directamente  no autentica correctamente.
**Resultado:** Requests subsiguientes fallan con 401/403.
**Fix:** Usar  — esto inicializa todos los headers necesarios.

### 5. SmartProxy muerto (77.77.77.77:8080)
**Error:** Proxy hardcodeado que nunca existió o ya expiró.
**Resultado:**  en cada intento.
**Fix:** No usar proxy. La EC2 AWS puede conectarse a Instagram via  sin proxy.

### 6. ValesNissanCombustible bloqueada por Instagram
**Error:** Esta cuenta (incluso desde laptop) da  o .
**Resultado:** Ningún script puede autenticarse con ella via username/password.
**Fix:** Usar sesión de cuenta personal via Cookie-Editor → copiar cookie  → pegar en .

### 7.  no existe → usar 
**Error:**  causa AttributeError en instagrapi 2.4.4.
**Fix:** .

### 8.  /  son interactivos
**Error:** Varios scripts llamaban  creyendo que era necesario.
**Resultado:** Pre-flow puede funcionar, pero el login subsiguiente sigue fallando desde IPs de datacenter AWS.
**Fix:** El problema nunca fue el pre-flow. Es que AWS IPs están blacklisted para login directo.
**Solución real:** Saltar todo y usar  con cookie del browser.

---

## Lo que SÍ funciona (solución final: clientes_instagram/main.py)



---

## Por qué hay 16 archivos de debug

Cada intento fallido generó un nuevo archivo con nombre creativo (, , , , etc.).
Ninguno resolvió el problema porque todos tenían los mismos errores fundamentales (TTY + IP blacklist).
La solución real llegó cuando se cambió el approach completo: usar cookie del browser en lugar de login directo.

---

## Archivos en este directorio que PUEDES ignorar
Todos los , , , , ,
, ,  son intentos fallidos históricos.

**El único archivo relevante es: **
