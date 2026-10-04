"""
================================================================================
Suite de Pruebas — SisNotas UMSS
================================================================================
Materia  : Evaluación y Auditoría de Sistemas
Docente  : Ing. Jimmy Villarroel Novillo
Equipo   : Grupo 15 — Bryan Vásquez, Juan Adiel Butrón, Fernando Vera
Gestión  : II-2026
--------------------------------------------------------------------------------
Organización de los Tests:
  BLOQUE A — Validaciones (Caja Negra: clases de equivalencia + valores límite)
  BLOQUE B — Flujo de evaluación académica (Caja Blanca: caminos del grafo)
  BLOQUE C — Reglas específicas de instancia (TC Alto Nivel)
  BLOQUE D — Reportes y detección de anomalías (TC Alto Nivel)
  BLOQUE E — Casos de TC de Bajo Nivel (bifurcaciones exactas en los límites)
================================================================================
"""

import pytest
import sys
import os

# Agregar la raíz del proyecto al path para que Python encuentre 'src'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sisnotas import (
    validar_nota,
    validar_codigo_sis,
    validar_comprobante,
    evaluar_estudiante,
    calcular_promedio_curso,
    calcular_tasa_aprobacion,
    detectar_anomalias,
    NOTA_MINIMA_APROBACION,
    NOTA_MINIMA_INSTANCIA,
    NOTA_ASENTADA_INSTANCIA,
    MAX_INSTANCIAS_SEMESTRE,
)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BLOQUE A — VALIDACIONES (CAJA NEGRA)                                  ║
# ║  Técnica: Clases de Equivalencia + Análisis de Valores Límite (AVL)    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestValidarNota:
    """
    Clases de Equivalencia para validar_nota(nota):
        CE-V1 (Válida)  : nota en [0, 100]
        CE-I1 (Inválida): nota < 0
        CE-I2 (Inválida): nota > 100

    Valores Límite:
        -1 (fuera), 0 (mínimo), 1 (justo adentro),
        50 (nominal), 99 (justo antes del máximo), 100 (máximo), 101 (fuera)
    """

    # --- CE-V1: Notas válidas ---
    def test_nota_minima_valida(self):
        """AVL: valor en el límite inferior exacto → debe aceptar"""
        assert validar_nota(0) is True

    def test_nota_justo_sobre_minimo(self):
        """AVL: un punto sobre el límite inferior → debe aceptar"""
        assert validar_nota(1) is True

    def test_nota_nominal(self):
        """CE-V1: valor en el centro del rango → debe aceptar"""
        assert validar_nota(50) is True

    def test_nota_maxima_valida(self):
        """AVL: valor en el límite superior exacto → debe aceptar"""
        assert validar_nota(100) is True

    def test_nota_justo_bajo_maximo(self):
        """AVL: un punto bajo el límite superior → debe aceptar"""
        assert validar_nota(99) is True

    # --- CE-I1: Notas por debajo del mínimo ---
    def test_nota_negativa_invalida(self):
        """CE-I1 / AVL: nota negativa → debe rechazar"""
        assert validar_nota(-1) is False

    def test_nota_muy_negativa_invalida(self):
        """CE-I1: nota muy negativa → debe rechazar"""
        assert validar_nota(-50) is False

    # --- CE-I2: Notas por encima del máximo ---
    def test_nota_sobre_maximo_invalida(self):
        """CE-I2 / AVL: un punto sobre el máximo → debe rechazar"""
        assert validar_nota(101) is False

    def test_nota_muy_alta_invalida(self):
        """CE-I2: nota desorbitada → debe rechazar"""
        assert validar_nota(200) is False


class TestValidarCodigoSIS:
    """
    Clases de Equivalencia para validar_codigo_sis(codigo):
        CE-V1 (Válida)  : 9 dígitos, primer dígito > 0
        CE-I1 (Inválida): longitud < 9
        CE-I2 (Inválida): longitud > 9
        CE-I3 (Inválida): contiene caracteres no numéricos
        CE-I4 (Inválida): primer dígito = 0
        CE-I5 (Inválida): cadena vacía
    """

    def test_codigo_valido(self):
        """CE-V1: código estándar UMSS → debe aceptar"""
        assert validar_codigo_sis("202100123") is True

    def test_codigo_valido_primer_digito_9(self):
        """CE-V1: primer dígito = 9 (máximo) → debe aceptar"""
        assert validar_codigo_sis("999999999") is True

    def test_codigo_corto_invalido(self):
        """CE-I1: menos de 9 dígitos → debe rechazar"""
        assert validar_codigo_sis("12345") is False

    def test_codigo_largo_invalido(self):
        """CE-I2: más de 9 dígitos → debe rechazar"""
        assert validar_codigo_sis("1234567890") is False

    def test_codigo_con_letras_invalido(self):
        """CE-I3: contiene letras → debe rechazar"""
        assert validar_codigo_sis("20210AB23") is False

    def test_codigo_primer_digito_cero_invalido(self):
        """CE-I4: primer dígito = 0 → debe rechazar"""
        assert validar_codigo_sis("012345678") is False

    def test_codigo_vacio_invalido(self):
        """CE-I5: cadena vacía → debe rechazar"""
        assert validar_codigo_sis("") is False

    def test_codigo_none_invalido(self):
        """CE-I5: None → debe rechazar (no crashear)"""
        assert validar_codigo_sis(None) is False


class TestValidarComprobante:
    """
    Clases de Equivalencia para validar_comprobante(comprobante):
        CE-V1 (Válida)  : alfanumérico, longitud 5-20
        CE-I1 (Inválida): longitud < 5
        CE-I2 (Inválida): longitud > 20
        CE-I3 (Inválida): contiene caracteres especiales
        CE-I4 (Inválida): vacío o None
    """

    def test_comprobante_valido(self):
        """CE-V1: comprobante estándar de caja UMSS → debe aceptar"""
        assert validar_comprobante("UMSS12345") is True

    def test_comprobante_minima_longitud(self):
        """AVL: exactamente 5 caracteres (límite mínimo) → debe aceptar"""
        assert validar_comprobante("A1B2C") is True

    def test_comprobante_corto_invalido(self):
        """CE-I1 / AVL: 4 caracteres (bajo el mínimo) → debe rechazar"""
        assert validar_comprobante("AB12") is False

    def test_comprobante_largo_invalido(self):
        """CE-I2 / AVL: 21 caracteres (sobre el máximo) → debe rechazar"""
        assert validar_comprobante("A" * 21) is False

    def test_comprobante_con_guion_invalido(self):
        """CE-I3: guiones son caracteres especiales → debe rechazar"""
        assert validar_comprobante("UMSS-12345") is False

    def test_comprobante_vacio_invalido(self):
        """CE-I4: cadena vacía → debe rechazar"""
        assert validar_comprobante("") is False

    def test_comprobante_none_invalido(self):
        """CE-I4: None → debe rechazar sin crashear"""
        assert validar_comprobante(None) is False


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BLOQUE B — FLUJO ACADÉMICO (CAJA BLANCA)                              ║
# ║  Técnica: Cobertura de Caminos Básicos (McCabe V(G) = 10)              ║
# ║                                                                        ║
# ║  Los 10 caminos cubren todos los nodos predicado del grafo de flujo    ║
# ║  de la función evaluar_estudiante().                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestEvaluarEstudianteCajaBlanca:
    """
    Caminos básicos del grafo de flujo de evaluar_estudiante():

    C1:  N1→ Error (nota parcial inválida)
    C2:  N1→N2→N3→ Aprobado con parciales
    C3:  N1→N2→N3→N4→ Aprobado con final
    C4:  N1→N2→N3→N4→ Reprobado con final
    C5:  N1→N2→N3→N4(none)→N5→N6→ Error límite instancias
    C6:  N1→N2→N3→N4(none)→N5→N6→N7→ No habilitado (parciales < 26)
    C7:  N1→N2→N3→N4(none)→N5→N6→N7→N8→ Error comprobante inválido
    C8:  N1→N2→N3→N4(none)→N5→N6→N7→N8→N9→ Aprobado instancia
    C9:  N1→N2→N3→N4(none)→N5→N6→N7→N8→N9→ Reprobado instancia
    C10: N1→N2→N3→N4(none)→N5(none)→N10→ Reprobado sin opciones
    """

    # ── C1: Nota parcial inválida ───────────────────────────────────────────
    def test_C1_nota_parcial_invalida(self):
        """Camino 1: parcial fuera de rango → ERROR_NOTA_INVALIDA"""
        resultado = evaluar_estudiante(parcial1=-10, parcial2=30)
        assert resultado["estado"] == "ERROR_NOTA_INVALIDA"
        assert resultado["nota_asentada"] is None

    # ── C2: Aprobado con parciales ─────────────────────────────────────────
    def test_C2_aprobado_con_parciales(self):
        """Camino 2: 1P + 2P >= 51 → APROBADO_PARCIALES"""
        resultado = evaluar_estudiante(parcial1=26, parcial2=25)
        assert resultado["estado"] == "APROBADO_PARCIALES"
        assert resultado["nota_asentada"] == 51

    # ── C3: Aprobado con examen final ──────────────────────────────────────
    def test_C3_aprobado_con_examen_final(self):
        """Camino 3: parciales < 51, final >= 51 → APROBADO_FINAL"""
        resultado = evaluar_estudiante(parcial1=20, parcial2=20, nota_final=60)
        assert resultado["estado"] == "APROBADO_FINAL"
        assert resultado["nota_asentada"] == 60

    # ── C4: Reprobado en examen final ──────────────────────────────────────
    def test_C4_reprobado_en_examen_final(self):
        """Camino 4: parciales < 51, final < 51 → REPROBADO_FINAL"""
        resultado = evaluar_estudiante(parcial1=20, parcial2=20, nota_final=40)
        assert resultado["estado"] == "REPROBADO_FINAL"
        assert resultado["nota_asentada"] == 40

    # ── C5: Error por límite de instancias excedido ────────────────────────
    def test_C5_limite_instancias_excedido(self):
        """Camino 5: ya tiene 2 instancias previas → ERROR_LIMITE"""
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=20,
            instancias_previas=2,
            nota_instancia=80,
            numero_comprobante="UMSS99999",
        )
        assert resultado["estado"] == "ERROR_LIMITE_INSTANCIAS_EXCEDIDO"
        assert resultado["nota_asentada"] is None

    # ── C6: No habilitado para instancia (parciales < 26) ──────────────────
    def test_C6_no_habilitado_instancia_parciales_bajos(self):
        """Camino 6: suma parciales < 26 → NO_HABILITADO_INSTANCIA"""
        resultado = evaluar_estudiante(
            parcial1=10, parcial2=10,
            instancias_previas=0,
            nota_instancia=80,
            numero_comprobante="UMSS99999",
        )
        assert resultado["estado"] == "NO_HABILITADO_INSTANCIA"

    # ── C7: Comprobante de pago inválido ───────────────────────────────────
    def test_C7_comprobante_invalido(self):
        """Camino 7: habilitado pero sin comprobante válido → ERROR_COMPROBANTE"""
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=0,
            nota_instancia=70,
            numero_comprobante="mal",   # muy corto, inválido
        )
        assert resultado["estado"] == "ERROR_COMPROBANTE_INVALIDO"

    # ── C8: Aprobado por instancia ─────────────────────────────────────────
    def test_C8_aprobado_instancia(self):
        """Camino 8: todos los requisitos OK, nota_instancia >= 51 → APROBADO_INSTANCIA"""
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=0,
            nota_instancia=75,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "APROBADO_INSTANCIA"

    # ── C9: Reprobado en instancia ─────────────────────────────────────────
    def test_C9_reprobado_instancia(self):
        """Camino 9: todos los requisitos OK, nota_instancia < 51 → REPROBADO_INSTANCIA"""
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=0,
            nota_instancia=30,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "REPROBADO_INSTANCIA"

    # ── C10: Reprobado sin opciones ────────────────────────────────────────
    def test_C10_reprobado_sin_opciones(self):
        """Camino 10: reprobó parciales, no rindió final ni instancia → REPROBADO_SIN_OPCIONES"""
        resultado = evaluar_estudiante(parcial1=20, parcial2=25)
        assert resultado["estado"] == "REPROBADO_SIN_OPCIONES"
        assert resultado["nota_asentada"] == 45


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BLOQUE C — REGLAS ESPECÍFICAS DE INSTANCIA (TC ALTO NIVEL)            ║
# ║  Casos de negocio críticos que un auditor revisaría                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestReglasInstanciaAltoNivel:
    """
    TC de Alto Nivel: Se enfoca en las REGLAS DE NEGOCIO,
    no en la estructura interna del código.
    """

    # TC-AN-01
    def test_nota_instancia_asentada_siempre_es_51_aunque_saque_100(self):
        """
        TC-AN-01 (Regla Crítica de Auditoría):
        Un estudiante que saca 100 en instancia NO puede tener
        una nota asentada mayor a 51. Detectar lo contrario es una anomalía.
        """
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=0,
            nota_instancia=100,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "APROBADO_INSTANCIA"
        assert resultado["nota_asentada"] == 51, (
            "FALLA DE AUDITORÍA: nota asentada no puede superar 51 en instancia"
        )

    # TC-AN-02
    def test_nota_instancia_asentada_siempre_es_51_aunque_saque_85(self):
        """TC-AN-02: igual que TC-AN-01 pero con nota 85"""
        resultado = evaluar_estudiante(
            parcial1=20, parcial2=10,
            instancias_previas=1,
            nota_instancia=85,
            numero_comprobante="UMSS99888",
        )
        assert resultado["nota_asentada"] == NOTA_ASENTADA_INSTANCIA

    # TC-AN-03
    def test_segunda_instancia_permitida(self):
        """
        TC-AN-03: Un estudiante con 1 instancia previa (NO 2) puede rendir una más.
        """
        resultado = evaluar_estudiante(
            parcial1=20, parcial2=10,
            instancias_previas=1,  # solo tiene 1, le queda 1 más
            nota_instancia=60,
            numero_comprobante="UMSS77777",
        )
        assert resultado["estado"] == "APROBADO_INSTANCIA"

    # TC-AN-04
    def test_tercera_instancia_bloqueada(self):
        """
        TC-AN-04: Un estudiante con 2 instancias previas NO puede rendir una tercera.
        El sistema DEBE bloquearlo automáticamente.
        """
        resultado = evaluar_estudiante(
            parcial1=20, parcial2=10,
            instancias_previas=2,  # ya agotó su cupo
            nota_instancia=90,
            numero_comprobante="UMSS77777",
        )
        assert resultado["estado"] == "ERROR_LIMITE_INSTANCIAS_EXCEDIDO"

    # TC-AN-05
    def test_sin_comprobante_no_puede_dar_instancia(self):
        """
        TC-AN-05: Sin boleta pagada en caja, no hay instancia.
        (Aunque tenga nota >= 26 en parciales)
        """
        resultado = evaluar_estudiante(
            parcial1=20, parcial2=10,
            instancias_previas=0,
            nota_instancia=70,
            numero_comprobante=None,  # no pagó
        )
        assert resultado["estado"] == "ERROR_COMPROBANTE_INVALIDO"

    # TC-AN-06
    def test_parciales_exactamente_26_habilita_instancia(self):
        """
        TC-AN-06 (Valor Límite): La frontera exacta que habilita instancia es 26.
        Con suma = 26 DEBE poder dar instancia.
        """
        resultado = evaluar_estudiante(
            parcial1=13, parcial2=13,  # suma exacta = 26
            instancias_previas=0,
            nota_instancia=55,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "APROBADO_INSTANCIA"

    # TC-AN-07
    def test_parciales_25_no_habilita_instancia(self):
        """
        TC-AN-07 (Valor Límite): Con suma = 25 (un punto bajo el límite) NO puede dar instancia.
        """
        resultado = evaluar_estudiante(
            parcial1=13, parcial2=12,  # suma exacta = 25
            instancias_previas=0,
            nota_instancia=90,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "NO_HABILITADO_INSTANCIA"

    # TC-AN-08
    def test_instancia_con_nota_50_reprueba(self):
        """
        TC-AN-08 (Valor Límite): 50 en instancia NO alcanza (necesita >= 51).
        """
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=0,
            nota_instancia=50,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "REPROBADO_INSTANCIA"

    # TC-AN-09
    def test_aprobado_con_parciales_exactamente_51(self):
        """
        TC-AN-09 (Valor Límite): Suma de parciales exactamente 51 → APROBADO.
        """
        resultado = evaluar_estudiante(parcial1=26, parcial2=25)
        assert resultado["estado"] == "APROBADO_PARCIALES"
        assert resultado["nota_asentada"] == 51

    # TC-AN-10
    def test_reprobado_con_parciales_exactamente_50(self):
        """
        TC-AN-10 (Valor Límite): Suma de parciales exactamente 50 → REPROBADO.
        Un punto hace la diferencia.
        """
        resultado = evaluar_estudiante(parcial1=25, parcial2=25)
        assert resultado["estado"] == "REPROBADO_SIN_OPCIONES"

    # TC-AN-11
    def test_final_con_nota_51_exacta_aprueba(self):
        """
        TC-AN-11 (Valor Límite): Nota final exactamente 51 → APROBADO_FINAL.
        """
        resultado = evaluar_estudiante(parcial1=20, parcial2=20, nota_final=51)
        assert resultado["estado"] == "APROBADO_FINAL"

    # TC-AN-12
    def test_final_con_nota_50_reprueba(self):
        """
        TC-AN-12 (Valor Límite): Nota final exactamente 50 → REPROBADO_FINAL.
        """
        resultado = evaluar_estudiante(parcial1=20, parcial2=20, nota_final=50)
        assert resultado["estado"] == "REPROBADO_FINAL"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BLOQUE D — REPORTES Y DETECCIÓN DE ANOMALÍAS (TC ALTO NIVEL)         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestReportesYAnomalias:

    def test_promedio_curso_normal(self):
        """TC-RPT-01: Promedio aritmético de varias notas → resultado correcto"""
        assert calcular_promedio_curso([60, 70, 80, 90]) == 75.0

    def test_promedio_curso_vacio(self):
        """TC-RPT-02: Lista vacía → retorna 0.0 sin error"""
        assert calcular_promedio_curso([]) == 0.0

    def test_tasa_aprobacion_todos_aprobados(self):
        """TC-RPT-03: 100% aprobados"""
        estados = ["APROBADO_PARCIALES", "APROBADO_FINAL", "APROBADO_INSTANCIA"]
        assert calcular_tasa_aprobacion(estados) == 100.0

    def test_tasa_aprobacion_ninguno_aprobado(self):
        """TC-RPT-04: 0% aprobados"""
        estados = ["REPROBADO_FINAL", "REPROBADO_INSTANCIA"]
        assert calcular_tasa_aprobacion(estados) == 0.0

    def test_tasa_aprobacion_mixta(self):
        """TC-RPT-05: 1 de 3 aprobados → 33.33%"""
        estados = ["APROBADO_PARCIALES", "REPROBADO_FINAL", "REPROBADO_INSTANCIA"]
        assert calcular_tasa_aprobacion(estados) == 33.33

    def test_detectar_anomalia_nota_instancia_superior_a_51(self):
        """
        TC-ANO-01 (Hallazgo de Auditoría):
        Si la nota asentada en instancia es > 51, el sistema detecta la anomalía.
        Esto equivale a un hallazgo de auditoría: CONDICIÓN vs CRITERIO.
        """
        registros = [
            {
                "nombre": "Juan Perez",
                "estado": "APROBADO_INSTANCIA",
                "nota_asentada": 75,      # ← ilegal, debería ser 51
                "instancias_rendidas": 1,
            }
        ]
        anomalias = detectar_anomalias(registros)
        assert len(anomalias) == 1
        assert "Juan Perez" in anomalias[0]

    def test_detectar_anomalia_mas_de_dos_instancias(self):
        """
        TC-ANO-02 (Hallazgo de Auditoría):
        Un registro con 3 instancias en el semestre viola el reglamento.
        """
        registros = [
            {
                "nombre": "Maria Lopez",
                "estado": "REPROBADO_INSTANCIA",
                "nota_asentada": 30,
                "instancias_rendidas": 3,   # ← ilegal
            }
        ]
        anomalias = detectar_anomalias(registros)
        assert len(anomalias) == 1
        assert "Maria Lopez" in anomalias[0]

    def test_sin_anomalias_en_datos_correctos(self):
        """TC-ANO-03: Datos limpios → lista de anomalías vacía"""
        registros = [
            {
                "nombre": "Carlos Vega",
                "estado": "APROBADO_INSTANCIA",
                "nota_asentada": 51,
                "instancias_rendidas": 1,
            }
        ]
        anomalias = detectar_anomalias(registros)
        assert anomalias == []


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BLOQUE E — TC DE BAJO NIVEL (Condiciones internas del código)         ║
# ║  Verifican bifurcaciones exactas, no la regla de negocio               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestCajaBlancarBajoNivel:

    def test_BN_01_nota_final_invalida_activa_rama_error(self):
        """
        TC-BN-01: El nodo predicado de validación de nota_final
        debe activar la rama ERROR cuando la nota es inválida.
        """
        resultado = evaluar_estudiante(parcial1=20, parcial2=20, nota_final=150)
        assert resultado["estado"] == "ERROR_NOTA_INVALIDA"

    def test_BN_02_nota_instancia_invalida_activa_rama_error(self):
        """
        TC-BN-02: El nodo predicado de validación de nota_instancia
        debe activar la rama ERROR cuando la nota es inválida.
        """
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=0,
            nota_instancia=-5,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "ERROR_NOTA_INVALIDA"

    def test_BN_03_parcial2_invalido_detectado(self):
        """
        TC-BN-03: Si parcial1 es válido pero parcial2 no lo es,
        la primera bifurcación (OR lógico) debe detectar el error.
        """
        resultado = evaluar_estudiante(parcial1=50, parcial2=110)
        assert resultado["estado"] == "ERROR_NOTA_INVALIDA"

    def test_BN_04_instancias_previas_igual_a_max_bloquea(self):
        """
        TC-BN-04 (Valor Límite interno): instancias_previas == MAX (2)
        activa la rama de bloqueo. No es instancias > 2, es >= 2.
        """
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=MAX_INSTANCIAS_SEMESTRE,  # exactamente 2
            nota_instancia=80,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "ERROR_LIMITE_INSTANCIAS_EXCEDIDO"

    def test_BN_05_instancias_previas_menor_que_max_permite(self):
        """
        TC-BN-05 (Valor Límite interno): instancias_previas == MAX - 1 (1)
        NO activa el bloqueo. El estudiante puede rendir.
        """
        resultado = evaluar_estudiante(
            parcial1=15, parcial2=15,
            instancias_previas=MAX_INSTANCIAS_SEMESTRE - 1,  # = 1
            nota_instancia=80,
            numero_comprobante="UMSS12345",
        )
        assert resultado["estado"] == "APROBADO_INSTANCIA"
