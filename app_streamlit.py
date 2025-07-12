
import streamlit as st
import pandas as pd
import random
import time
import io
from collections import Counter, defaultdict

# Configuraciones
TOTAL_SIMULACIONES = 500000
CANTIDAD_COMBINACIONES = 4095
RANGO = list(range(1, 29))

st.set_page_config(page_title="Simulador de Chispa", layout="centered")

st.title("🔢 Simulador de Chispa Inteligente")
st.write("Sube tu archivo CSV con los resultados pasados (columnas R1 a R5).")

archivo = st.file_uploader("Selecciona el archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo)
        if not all(c in df.columns for c in ["R1", "R2", "R3", "R4", "R5"]):
            st.error("❌ El archivo debe tener las columnas: R1, R2, R3, R4, R5")
        else:
            resultados_hist = df[["R1", "R2", "R3", "R4", "R5"]].values.tolist()
            frecuencia = Counter()
            for fila in resultados_hist:
                frecuencia.update(fila)

            st.subheader("📊 Frecuencia de Números (Historial)")
            freq_df = pd.DataFrame(frecuencia.items(), columns=["Número", "Frecuencia"]).sort_values(by="Número")
            st.bar_chart(freq_df.set_index("Número"))

            def generar_combinacion():
                pesos = [frecuencia.get(i, 0) + 1 for i in RANGO]
                return sorted(random.choices(RANGO, weights=pesos, k=5))

            st.write("🔁 Generando combinaciones y simulando... Esto puede tardar un poco.")
            progress = st.progress(0)
            status = st.empty()
            combinaciones = set()

            while len(combinaciones) < CANTIDAD_COMBINACIONES:
                c = tuple(sorted(set(generar_combinacion())))
                if len(c) == 5:
                    combinaciones.add(c)

            combinaciones = list(combinaciones)
            resultados = defaultdict(Counter)
            inicio = time.time()

            for i in range(TOTAL_SIMULACIONES):
                sorteo = set(random.sample(RANGO, 5))
                for comb in combinaciones:
                    aciertos = len(sorteo & set(comb))
                    resultados[comb][aciertos] += 1

                if i % (TOTAL_SIMULACIONES // 100) == 0 and i > 0:
                    progreso = int(i / TOTAL_SIMULACIONES * 100)
                    elapsed = time.time() - inicio
                    estimado = (elapsed / progreso) * (100 - progreso)
                    minutos = int(elapsed) // 60
                    segundos = int(elapsed) % 60
                    est_min = int(estimado) // 60
                    est_seg = int(estimado) % 60
                    status.text(f"⏱ Tiempo: {minutos}m {segundos}s | Estimado restante: {est_min}m {est_seg}s")
                    progress.progress(progreso)

            duracion = int(time.time() - inicio)
            minutos = duracion // 60
            segundos = duracion % 60

            def indice(c):
                r = resultados[c]
                return (r[2]*1 + r[3]*3 + r[4]*6 + r[5]*10) / TOTAL_SIMULACIONES

            ranking = sorted([(c, indice(c)) for c in combinaciones], key=lambda x: x[1], reverse=True)
            top3 = ranking[:3]

            st.success(f"✅ Simulación completada en {minutos}m {segundos}s")

            st.subheader("🏆 Mejores 3 combinaciones")
            for i, (comb, score) in enumerate(top3, 1):
                st.write(f"{i}. {comb} → Índice: {score:.6f}")

            df_resultado = pd.DataFrame([{"Combinación": comb, "Índice": score} for comb, score in top3])

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_resultado.to_excel(writer, index=False)
            output.seek(0)

            st.download_button(
                label="📥 Descargar en Excel",
                data=output,
                file_name="mejores_combinaciones.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ Error procesando archivo: {e}")
