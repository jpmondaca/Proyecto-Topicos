# Proyecto-Topicos
# probando repositorio / prueba

## Generación del informe

Instalar las dependencias en el Python utilizado por Quarto:

```powershell
py -m pip install -r requirements.txt
```

Para generar el PDF durante la edición:

```powershell
quarto render informe.qmd --to pdf
```

La primera ejecución calcula el análisis y guarda una caché local.
Los cambios de texto y portada pueden reutilizarla sin repetir los modelos.

Cuando cambie main.ipynb o datos.csv, incluidos cambios descargados del equipo,
se debe actualizar la caché. El notebook se carga como archivo externo y sus
cambios no deben darse por detectados automáticamente.

Para actualizar resultados y para reproducir la entrega completa:

```powershell
quarto render informe.qmd --to pdf --cache-refresh
```