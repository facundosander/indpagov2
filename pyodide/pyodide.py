import pandas as pd
import xml.etree.ElementTree as ET
from collections import defaultdict
from io import BytesIO

def leer_input_excel(file_bytes):
    # Leer el archivo Excel desde un byte stream
    df = pd.read_excel(BytesIO(file_bytes))
    return df.to_dict(orient='records')

def convertir_montos(row, tasa_cambio):
    if row["Moneda"] == "USD":
        row["Neto IVA Tasa Minima"] = float(row["Neto IVA Tasa Minima"]) * tasa_cambio
        row["Neto IVA Tasa Basica"] = float(row["Neto IVA Tasa Basica"]) * tasa_cambio
        row["Monto No Gravado"] = float(row["Monto No Gravado"]) * tasa_cambio
        row["Monto Total"] = float(row["Monto Total"]) * tasa_cambio
    return row

def agrupar_datos(data, fecha, cod_suc, filas_seleccionadas, tasa_cambio):
    grupos = defaultdict(lambda: {
        "TotMntNoGrv": 0.0,
        "TotMntExpyAsim": 0.0,
        "TotMntImpPerc": 0.0,
        "TotMntIVAenSusp": 0.0,
        "TotMntIVATasaMin": 0.0,
        "TotMntIVATasaBas": 0.0,
        "TotMntIVAOtra": 0.0,
        "MntIVATasaMin": 0.0,
        "MntIVATasaBas": 0.0,
        "MntIVAOtra": 0.0,
        "IVATasaMin": 10.0,
        "IVATasaBas": 22.0,
        "TotMntTotal": 0.0,
        "TotMntRetenido": 0.0,
        "TotMntCredFisc": 0.0
    })

    for i, row in enumerate(data):
        row = convertir_montos(row, tasa_cambio)
        key = (fecha, cod_suc, 1 if i in filas_seleccionadas else 0)
        grupos[key]["TotMntNoGrv"] += float(row["Monto No Gravado"])
        grupos[key]["TotMntIVATasaMin"] += float(row["Neto IVA Tasa Minima"])
        grupos[key]["TotMntIVATasaBas"] += float(row["Neto IVA Tasa Basica"])
        grupos[key]["TotMntTotal"] += float(row["Monto Total"])

    return grupos

def generar_xml(grupos):
    root = ET.Element("ns1:Montos")
    for (fecha, cod_suc, ind_pag_cta3ros), montos in grupos.items():
        item = ET.SubElement(root, "ns1:Mnts_FyT_Item")
        ET.SubElement(item, "ns1:Fecha").text = fecha
        ET.SubElement(item, "ns1:CodSuc").text = str(cod_suc)
        ET.SubElement(item, "ns1:IndPagCta3ros").text = str(ind_pag_cta3ros)
        for key, value in montos.items():
            ET.SubElement(item, f"ns1:{key}").text = f"{value:.2f}"
    
    tree = ET.ElementTree(root)
    return ET.tostring(root, encoding='utf-8').decode('utf-8')
