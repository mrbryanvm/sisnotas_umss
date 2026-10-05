"""
================================================================================
SisNotas UMSS — Sistema de Gestión de Notas
================================================================================
Materia  : Evaluación y Auditoría de Sistemas
Docente  : Ing. Jimmy Villarroel Novillo
Equipo   : Grupo 15 — Bryan Vasquez, Juan Adiel Butrón, Fernando Vera
Gestión  : II-2026
--------------------------------------------------------------------------------
Reglas de evaluación reales de la UMSS implementadas:
  1. Parciales: 1P + 2P >= 51 → APROBADO (sin examen final)
  2. Final    : Si reprueba parciales (o quiere mejorar), rinde Final/100 pts
                Final >= 51 → APROBADO
  3. Instancia:
       - Requisito a: suma de parciales >= 26 (mínimo habilitante)
       - Requisito b: boleta de instancia pagada (número de comprobante)
       - Requisito c: no más de 2 instancias en el semestre
       - Si aprueba instancia (nota_instancia >= 51): nota asentada = 51
         (nunca más de 51, aunque haya sacado 100 en el examen)
================================================================================
"""

# ---------------------------------------------------------------------------
# CONSTANTES DEL REGLAMENTO (hacerlas constantes facilita la Auditoría:
# si el reglamento cambia, solo se toca aquí, no en todo el código)
# ---------------------------------------------------------------------------
NOTA_MINIMA_APROBACION    = 51    # Puntos mínimos para aprobar
NOTA_MINIMA_INSTANCIA     = 26    # Puntos mínimos en parciales para acceder a instancia
NOTA_MAXIMA_NOTA_FINAL    = 100   # Máximo de puntos en cualquier examen
NOTA_MINIMA_EXAMEN        = 0     # Mínimo de puntos en cualquier examen
NOTA_ASENTADA_INSTANCIA   = 51    # Nota que se asienta si aprueba instancia (no más)
MAX_INSTANCIAS_SEMESTRE   = 2     # Máximo de instancias permitidas por semestre


# ---------------------------------------------------------------------------
# MÓDULO 1: VALIDACIONES DE DATOS
# Estas funciones protegen el sistema de datos erróneos antes de calcular.
# Conexión con Auditoría: son "controles preventivos" — evitan que datos
# incorrectos corrompan los resultados.
# ---------------------------------------------------------------------------

def validar_nota(nota: float) -> bool:
    """
    Verifica que una nota esté dentro del rango válido [0, 100].

    Args:
        nota: El valor numérico de la nota a validar.

    Returns:
        True si la nota es válida, False si está fuera de rango.

    Ejemplo:
        >>> validar_nota(75)
        True
        >>> validar_nota(-5)
        False
        >>> validar_nota(101)
        False
    """
    return NOTA_MINIMA_EXAMEN <= nota <= NOTA_MAXIMA_NOTA_FINAL


def validar_codigo_sis(codigo: str) -> bool:
    """
    Verifica que el código SIS del estudiante sea válido.
    Reglas: exactamente 9 dígitos numéricos, primer dígito > 0.

    Args:
        codigo: Cadena de texto con el código SIS.

    Returns:
        True si el código es válido.

    Ejemplo:
        >>> validar_codigo_sis("202100123")
        True
        >>> validar_codigo_sis("012345678")   # primer dígito = 0 → inválido
        False
    """
    if not isinstance(codigo, str):
        return False
    if len(codigo) != 9:
        return False
    if not codigo.isdigit():
        return False
    if int(codigo[0]) == 0:
        return False
    return True


def validar_comprobante(numero_comprobante: str) -> bool:
    """
    Verifica que el número de comprobante de pago de instancia sea válido.
    Reglas: no vacío, solo alfanumérico, longitud entre 5 y 20 caracteres.

    Args:
        numero_comprobante: Código del comprobante de la boleta pagada en caja.

    Returns:
        True si el comprobante es válido.
    """
    if not isinstance(numero_comprobante, str):
        return False
    codigo = numero_comprobante.strip()
    if len(codigo) < 5 or len(codigo) > 20:
        return False
    if not codigo.isalnum():
        return False
    return True


# ---------------------------------------------------------------------------
# MÓDULO 2: LÓGICA DE EVALUACIÓN ACADÉMICA
# Aquí está el núcleo de las reglas del reglamento UMSS.
# Esta es la función que analizaremos con CAJA BLANCA (grafo de flujo,
# complejidad ciclomática de McCabe) y CAJA NEGRA (clases de equivalencia,
# valores límite).
# ---------------------------------------------------------------------------

def evaluar_estudiante(

    parcial1: float,
    parcial2: float,
    instancias_previas: int = 0,
    nota_final: float | None = None,
    nota_instancia: float | None = None,
    numero_comprobante: str | None = None,
) -> dict:
    """
    Evalúa el estado académico de un estudiante según el reglamento UMSS.

    Flujo de evaluación (refleja el Grafo de Flujo para Caja Blanca):

        [N1] Validar parcial1 y parcial2
            → Inválido → ERROR_NOTA_INVALIDA

        [N2] Calcular suma_parciales = parcial1 + parcial2

        [N3] ¿suma_parciales >= 51?
            → SÍ → APROBADO_PARCIALES

        [N4] ¿Se rindió examen final?
            → SÍ → Validar nota_final
                   ¿nota_final >= 51? → SÍ → APROBADO_FINAL
                                      → NO → REPROBADO_FINAL

        [N5] ¿Se rindió examen de instancia?
            → SÍ →
                [N6] ¿instancias_previas < MAX_INSTANCIAS_SEMESTRE?
                    → NO → ERROR_LIMITE_INSTANCIAS_EXCEDIDO
                [N7] ¿suma_parciales >= 26?
                    → NO → NO_HABILITADO_INSTANCIA
                [N8] ¿Comprobante válido?
                    → NO → ERROR_COMPROBANTE_INVALIDO
                [N9] Validar nota_instancia
                    → ¿nota_instancia >= 51?
                        → SÍ → APROBADO_INSTANCIA (nota asentada = 51)
                        → NO → REPROBADO_INSTANCIA

        [N10] Sin más opciones → REPROBADO_SIN_OPCIONES

    Args:
        parcial1             : Nota del primer parcial  (0-100).
        parcial2             : Nota del segundo parcial (0-100).
        instancias_previas   : Cuántas instancias ya rindió este semestre (default 0).
        nota_final           : Nota del examen final (None si no lo rindió).
        nota_instancia       : Nota del examen de instancia (None si no lo rindió).
        numero_comprobante   : Código del comprobante de pago de boleta (None si no aplica).

    Returns:
        dict con las claves:
            "estado"       : Cadena que describe el resultado académico.
            "nota_asentada": Nota que se registra en el libro de calificaciones.
            "detalle"      : Mensaje explicativo del resultado.
    """
    # ── NODO 1: Validación de parciales ────────────────────────────────────
    if not validar_nota(parcial1) or not validar_nota(parcial2):
        return {
            "estado": "ERROR_NOTA_INVALIDA",
            "nota_asentada": None,
            "detalle": "Las notas de los parciales deben estar entre 0 y 100.",
        }

    # ── NODO 2: Suma de parciales ───────────────────────────────────────────
    suma_parciales = parcial1 + parcial2

    # ── NODO 3: ¿Aprueba con parciales? ────────────────────────────────────
    if suma_parciales >= NOTA_MINIMA_APROBACION:
        return {
            "estado": "APROBADO_PARCIALES",
            "nota_asentada": suma_parciales,
            "detalle": f"Aprobado con nota {suma_parciales} (parciales).",
        }

    # ── NODO 4: ¿Rindió examen final? ──────────────────────────────────────
    if nota_final is not None:
        if not validar_nota(nota_final):
            return {
                "estado": "ERROR_NOTA_INVALIDA",
                "nota_asentada": None,
                "detalle": "La nota del examen final debe estar entre 0 y 100.",
            }
        if nota_final >= NOTA_MINIMA_APROBACION:
            return {
                "estado": "APROBADO_FINAL",
                "nota_asentada": nota_final,
                "detalle": f"Aprobado con nota {nota_final} en examen final.",
            }
        else:
            return {
                "estado": "REPROBADO_FINAL",
                "nota_asentada": nota_final,
                "detalle": f"Reprobado. Nota final: {nota_final}. Puede intentar instancia si cumple requisitos.",
            }

    # ── NODO 5: ¿Rindió examen de instancia? ───────────────────────────────
    if nota_instancia is not None:

        # ── NODO 6: ¿No superó el límite de instancias? ────────────────────
        if instancias_previas >= MAX_INSTANCIAS_SEMESTRE:
            return {
                "estado": "ERROR_LIMITE_INSTANCIAS_EXCEDIDO",
                "nota_asentada": None,
                "detalle": f"El estudiante ya rindió {MAX_INSTANCIAS_SEMESTRE} instancias este semestre. No puede rendir más.",
            }

        # ── NODO 7: ¿Cumple el mínimo de parciales para instancia? ─────────
        if suma_parciales < NOTA_MINIMA_INSTANCIA:
            return {
                "estado": "NO_HABILITADO_INSTANCIA",
                "nota_asentada": None,
                "detalle": f"No habilitado para instancia. Suma de parciales: {suma_parciales} (mínimo requerido: {NOTA_MINIMA_INSTANCIA}).",
            }

        # ── NODO 8: ¿Tiene comprobante de pago válido? ─────────────────────
        if not validar_comprobante(numero_comprobante):
            return {
                "estado": "ERROR_COMPROBANTE_INVALIDO",
                "nota_asentada": None,
                "detalle": "Comprobante de pago de instancia inválido. Presentar boleta de caja (10 Bs.).",
            }

        # ── NODO 9: ¿Aprueba la instancia? ─────────────────────────────────
        if not validar_nota(nota_instancia):
            return {
                "estado": "ERROR_NOTA_INVALIDA",
                "nota_asentada": None,
                "detalle": "La nota de instancia debe estar entre 0 y 100.",
            }

        if nota_instancia >= NOTA_MINIMA_APROBACION:
            # REGLA CLAVE: aunque haya sacado 100, se asienta máximo 51
            return {
                "estado": "APROBADO_INSTANCIA",
                "nota_asentada": NOTA_ASENTADA_INSTANCIA,
                "detalle": (
                    f"Aprobado por instancia. Nota en examen: {nota_instancia}. "
                    f"Nota asentada: {NOTA_ASENTADA_INSTANCIA} (máximo permitido por reglamento)."
                ),
            }
        else:
            return {
                "estado": "REPROBADO_INSTANCIA",
                "nota_asentada": nota_instancia,
                "detalle": f"Reprobado en instancia con nota {nota_instancia}.",
            }

    # ── NODO 10: Sin opciones adicionales ──────────────────────────────────
    return {
        "estado": "REPROBADO_SIN_OPCIONES",
        "nota_asentada": suma_parciales,
        "detalle": (
            f"Reprobado. Suma de parciales: {suma_parciales}. "
            "No rindió examen final ni de instancia."
        ),
    }


# ---------------------------------------------------------------------------
# MÓDULO 3: REPORTES Y ESTADÍSTICAS DEL CURSO
# Funciones para calcular métricas agregadas sobre un conjunto de estudiantes.
# Conexión con Auditoría: generan los "papeles de trabajo" con estadísticas
# que un auditor analizaría para detectar anomalías.
# ---------------------------------------------------------------------------

def calcular_promedio_curso(notas_asentadas: list[float]) -> float:
    """
    Calcula el promedio de notas asentadas de todos los estudiantes.

    Args:
        notas_asentadas: Lista de notas numéricas (ya validadas).

    Returns:
        Promedio como float, redondeado a 2 decimales.
        Retorna 0.0 si la lista está vacía.

    Ejemplo:
        >>> calcular_promedio_curso([60, 70, 45, 80])
        63.75
    """
    if not notas_asentadas:
        return 0.0
    return round(sum(notas_asentadas) / len(notas_asentadas), 2)


def calcular_tasa_aprobacion(estados: list[str]) -> float:
    """
    Calcula el porcentaje de estudiantes aprobados sobre el total.

    Un estado se considera "aprobado" si comienza con "APROBADO".

    Args:
        estados: Lista de cadenas de estado (ej. ["APROBADO_PARCIALES", "REPROBADO_SIN_OPCIONES"]).

    Returns:
        Porcentaje de aprobación (0.0 a 100.0), redondeado a 2 decimales.
        Retorna 0.0 si la lista está vacía.

    Ejemplo:
        >>> calcular_tasa_aprobacion(["APROBADO_PARCIALES", "REPROBADO_FINAL", "APROBADO_INSTANCIA"])
        66.67
    """
    if not estados:
        return 0.0
    aprobados = sum(1 for e in estados if e.startswith("APROBADO"))
    return round((aprobados / len(estados)) * 100, 2)


def detectar_anomalias(registros: list[dict]) -> list[str]:
    """
    Detecta irregularidades en un conjunto de registros de estudiantes.
    Conexión con Auditoría: simula la fase de "Ejecución" donde el auditor
    busca desviaciones entre el criterio (reglamento) y la condición (datos reales).

    Anomalías detectadas:
        - Nota asentada mayor a 51 en examen de instancia.
        - Estudiante con más de 2 instancias en el semestre.
        - Nota asentada fuera de rango [0, 100].

    Args:
        registros: Lista de dicts con las claves:
            "nombre", "estado", "nota_asentada", "instancias_rendidas".

    Returns:
        Lista de strings describiendo cada anomalía encontrada.
        Lista vacía si no hay anomalías.
    """
    anomalias = []
    for r in registros:
        nombre = r.get("nombre", "Desconocido")
        estado = r.get("estado", "")
        nota   = r.get("nota_asentada")
        inst   = r.get("instancias_rendidas", 0)

        # Anomalía 1: Nota de instancia superior al máximo permitido
        if estado == "APROBADO_INSTANCIA" and nota is not None and nota > NOTA_ASENTADA_INSTANCIA:
            anomalias.append(
                f"ANOMALÍA [{nombre}]: Nota asentada {nota} supera el máximo permitido "
                f"por instancia ({NOTA_ASENTADA_INSTANCIA})."
            )

        # Anomalía 2: Más instancias de las permitidas
        if inst > MAX_INSTANCIAS_SEMESTRE:
            anomalias.append(
                f"ANOMALÍA [{nombre}]: Registra {inst} instancias, superando el máximo "
                f"permitido ({MAX_INSTANCIAS_SEMESTRE}) por semestre."
            )

        # Anomalía 3: Nota asentada fuera de rango
        if nota is not None and (nota < 0 or nota > 100):
            anomalias.append(
                f"ANOMALÍA [{nombre}]: Nota asentada {nota} está fuera del rango válido [0, 100]."
            )

    return anomalias
