# Proyecto-Topicos

## Generación del informe

Instalar las dependencias en el Python utilizado por Quarto:

```powershell
py -m pip install -r requirements.txt
```

Se requiere Quarto y una instalación de LaTeX. Puede instalarse TinyTeX con `quarto install tinytex`.

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
El informe ejecuta la preparación, el exploratorio y la sección M2 de `main.ipynb`. Las tablas y figuras de M2 se recalculan desde sus predicciones de validación. La primera generación o `--cache-refresh` puede tardar varios minutos por los SVM. Las secciones M0, M1, M3 y la evaluación de reserva no se ejecutan desde este informe parcial.
