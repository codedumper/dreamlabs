# Reglas de Bonus - Dreamslabs Manager

## Documento de Reglas de Bonus por Período

**Fecha de creación :** 19/01/2026  
**Versión :** 1.0

---

## 1. Introducción

Este documento describe las reglas de bonus aplicables a los modelos de Dreamslabs. Las reglas de bonus se configuran por agencia y pueden aplicarse a diferentes períodos (diario, semanal, quincenal, mensual).

---

## 2. Reglas de Rally Semanal (7 Días)

### 2.1 Descripción General

Las reglas de rally semanal se aplican sobre un período de 7 días consecutivos. El bonus se calcula basándose en el **total de ganancias de la semana**, comparado con los objetivos establecidos.

### 2.2 Niveles de Bonus

#### Nivel 1 - Bonus Básico
- **Objetivo mínimo :** 455 USD de total semanal
- **Bonus otorgado :** 40.000 COP (monto fijo)
- **Condición :** El modelo debe alcanzar un total de ganancias de al menos 455 USD durante los 7 días del período semanal.

#### Nivel 2 - Bonus Intermedio
- **Objetivo mínimo :** 525 USD de total semanal
- **Bonus otorgado :** 60.000 COP (monto fijo)
- **Condición :** El modelo debe alcanzar un total de ganancias de al menos 525 USD durante los 7 días del período semanal.

#### Nivel 3 - Bonus Avanzado
- **Objetivo mínimo :** 560 USD de total semanal
- **Bonus otorgado :** 100.000 COP (monto fijo)
- **Condición :** El modelo debe alcanzar un total de ganancias de al menos 560 USD durante los 7 días del período semanal.

### 2.3 Cálculo del Total Semanal

El total semanal se calcula sumando todas las ganancias de los días trabajados durante el período de 7 días:

```
Total Semanal = Suma de todas las ganancias de los días trabajados en la semana
```

**Ejemplo :**
- Si un modelo trabaja 5 días en la semana y genera:
  - Día 1: 100 USD
  - Día 2: 90 USD
  - Día 3: 120 USD
  - Día 4: 110 USD
  - Día 5: 95 USD
- Total semanal: 515 USD
- **Resultado :** El modelo alcanza el Nivel 1 (≥ 455 USD) y el Nivel 2 (≥ 525 USD) pero no el Nivel 3 (< 560 USD)
- **Bonus otorgado :** 60.000 COP (nivel más alto alcanzado)

### 2.4 Reglas de Aplicación

1. **Orden de evaluación :** Las reglas se evalúan en orden ascendente (Nivel 1, luego Nivel 2, luego Nivel 3).

2. **Aplicación única :** Solo se aplica el bonus del nivel más alto alcanzado. Si un modelo alcanza el Nivel 3, solo recibe 100.000 COP, no la suma de los tres niveles.

3. **Cumplimiento del objetivo :** El total semanal debe ser **igual o superior** al objetivo mínimo del nivel para que el bonus se active.

4. **Días trabajados :** Solo se consideran los días en los que el modelo realmente trabajó según su horario asignado.

5. **Moneda del objetivo :** Los objetivos están definidos en USD. Las ganancias se convierten a USD usando la tasa de cambio (TRM) del día correspondiente.

---

## 3. Configuración en el Sistema

### 3.1 Parámetros de Configuración

Cada regla de bonus debe configurarse en el sistema con los siguientes parámetros:

- **Nombre de la regla :** Descripción clara del nivel (ej: "Rally Semanal - Nivel 1")
- **Tipo de período :** Semanal (WEEKLY)
- **Moneda del objetivo :** USD
- **Objetivo :** Monto mínimo en USD (455, 525, o 560 según el nivel)
- **Tipo de bonus :** Monto Fijo (FIXED_AMOUNT)
- **Valor del bonus :** Monto en COP (40.000, 60.000, o 100.000 según el nivel)
- **Orden :** Orden de evaluación (1, 2, 3)
- **Detener en esta regla :** Configurado según necesidad (si se alcanza un nivel, no evaluar los siguientes)

### 3.2 Ejemplo de Configuración

**Regla 1 - Nivel 1:**
```
Nombre: Rally Semanal - Nivel 1
Período: Semanal
Moneda objetivo: USD
Objetivo: 455.00 USD
Tipo bonus: Monto Fijo
Valor bonus: 40000.00 COP
Orden: 1
Detener en esta regla: No
```

**Regla 2 - Nivel 2:**
```
Nombre: Rally Semanal - Nivel 2
Período: Semanal
Moneda objetivo: USD
Objetivo: 525.00 USD
Tipo bonus: Monto Fijo
Valor bonus: 60000.00 COP
Orden: 2
Detener en esta regla: No
```

**Regla 3 - Nivel 3:**
```
Nombre: Rally Semanal - Nivel 3
Período: Semanal
Moneda objetivo: USD
Objetivo: 560.00 USD
Tipo bonus: Monto Fijo
Valor bonus: 100000.00 COP
Orden: 3
Detener en esta regla: Sí (opcional, si solo se quiere otorgar el nivel más alto)
```

---

## 4. Notas Importantes

### 4.1 Conversión de Moneda

- Los objetivos están definidos en USD para estandarizar los criterios.
- Las ganancias diarias se registran en COP y se convierten a USD usando la TRM del día correspondiente.
- El bonus se otorga siempre en COP.

### 4.2 Período de Evaluación

- El período semanal comprende 7 días consecutivos.
- El inicio y fin del período se calculan según la configuración del sistema.
- Se suman todas las ganancias de los días trabajados durante estos 7 días para obtener el total semanal.
- No se requiere que el modelo trabaje los 7 días; se suma el total de los días trabajados.

### 4.3 Activación y Desactivación

- Las reglas pueden activarse o desactivarse individualmente.
- Una regla desactivada no se evalúa, pero los datos históricos se conservan.
- Los cambios en las reglas no afectan los bonus ya calculados y otorgados.

---

## 5. Ejemplos Prácticos

### Ejemplo 1: Modelo que alcanza Nivel 1

**Semana del 1 al 7 de enero:**
- Días trabajados: 5 días
- Ganancias diarias: 100, 90, 95, 85, 90 USD
- **Total semanal: 460 USD**

**Resultado :** 
- ✅ Alcanza Nivel 1 (≥ 455 USD)
- ❌ No alcanza Nivel 2 (< 525 USD)
- **Bonus otorgado :** 40.000 COP

### Ejemplo 2: Modelo que alcanza Nivel 2

**Semana del 1 al 7 de enero:**
- Días trabajados: 6 días
- Ganancias diarias: 90, 95, 85, 90, 95, 85 USD
- **Total semanal: 540 USD**

**Resultado :**
- ✅ Alcanza Nivel 1 (≥ 455 USD)
- ✅ Alcanza Nivel 2 (≥ 525 USD)
- ❌ No alcanza Nivel 3 (< 560 USD)
- **Bonus otorgado :** 60.000 COP (solo el nivel más alto)

### Ejemplo 3: Modelo que alcanza Nivel 3

**Semana del 1 al 7 de enero:**
- Días trabajados: 7 días
- Ganancias diarias: 85, 90, 80, 85, 90, 80, 85 USD
- **Total semanal: 595 USD**

**Resultado :**
- ✅ Alcanza Nivel 1 (≥ 455 USD)
- ✅ Alcanza Nivel 2 (≥ 525 USD)
- ✅ Alcanza Nivel 3 (≥ 560 USD)
- **Bonus otorgado :** 100.000 COP (solo el nivel más alto)

---

## 6. Preguntas Frecuentes

### ¿Qué pasa si un modelo no alcanza ningún nivel?
Si el total semanal es inferior a 455 USD, no se otorga ningún bonus.

### ¿Puede un modelo recibir múltiples bonus en la misma semana?
No. Solo se otorga el bonus del nivel más alto alcanzado. Los niveles no son acumulativos.

### ¿Cómo se determina qué días se consideran "trabajados"?
Se consideran los días en los que el modelo tiene un horario asignado y ha registrado horas trabajadas en el sistema.

### ¿Qué pasa si falta información de ganancias para algunos días?
Solo se consideran los días con ganancias registradas. El total semanal se calcula sumando únicamente las ganancias de los días con datos disponibles.

---

**Nota :** Este documento puede actualizarse cuando se agreguen nuevas reglas de bonus o se modifiquen las existentes.
