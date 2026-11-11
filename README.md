# Caso 07 - Inspecciones sanitarias de establecimientos en Chicago

Proyecto - Tópicos Aplicados en Estadística.

## Integrantes 

- Graciela Goméz Jure
- Benjamín Gutiérrez Rivera
- Juan Pablo Mondaca Palma
- Benjamin Vargas Carmine

## Datos

Los datos están en el siguiente archivo llamado `datos.csv`, debes descargarlo y colocarlo 
en la misma carpeta de `main.ipynb`.

## Instalación

El análisis se desarrolló con Python 3.11.7. Las librerías y sus
versiones están registradas en `requirements.txt`.

Desde la carpeta del proyecto, ejecuta:

```powershell
py -3.11 -m pip install -r requirements.txt
```

## Informe

El informe se escribió en LaTeX y se compila en Overleaf.

## Ejecución

Para ejecutar el código coloque lo siguiente en la terminal en 
la carpeta del proyecto, es decir, la que contiene `main.ipynb`
y `datos.csv`.

```powershell
py -3.11 -m jupyter nbconvert --to notebook --execute --inplace main.ipynb --ExecutePreprocessor.timeout=-1
```