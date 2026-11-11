# Caso 07 - Inspecciones sanitarias de establecimientos en Chicago

Proyecto - Tópicos Aplicados en Estadística.

## Integrantes 

- Graciela Goméz Jure
- Benjamín Gutiérrez Rivera
- Juan Pablo Mondaca Palma
- Benjamin Vargas Carmine

## Datos

Los datos provienen del paquete `caso07_chicago_inspecciones.zip`,
entregado en Canvas para el Caso 07 de EYP3407.

Extrae `datos.csv` del ZIP o descárgalo desde la
[Proyecto - EYP3407](https://drive.google.com/drive/folders/1palNK12Hm7pl-dw03mXjpNxo6WXBvZDT?usp=sharing).
Coloca `datos.csv` en la misma carpeta que `main.ipynb`.

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