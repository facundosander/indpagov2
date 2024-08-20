async function loadPyodideAndRun() {
    const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/"
    });
    return pyodide;
}

const pyodideReadyPromise = loadPyodideAndRun();

document.getElementById('converter-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const pyodide = await pyodideReadyPromise;
    
    const fileInput = document.getElementById('file-input').files[0];
    const fecha = document.getElementById('fecha').value;
    const codSuc = document.getElementById('cod-suc').value;
    const tasaCambio = document.getElementById('tasa-cambio').value;
    const filasSeleccionadas = document.getElementById('filas-seleccionadas').value.split(',').map(Number);
    
    const reader = new FileReader();
    reader.onload = async function(event) {
        const arrayBuffer = event.target.result;
        const data = new Uint8Array(arrayBuffer);
        
        await pyodide.loadPackage(["pandas", "openpyxl"]);

        pyodide.globals.set('data', data);
        pyodide.globals.set('fecha', fecha);
        pyodide.globals.set('cod_suc', codSuc);
        pyodide.globals.set('tasa_cambio', tasaCambio);
        pyodide.globals.set('filas_seleccionadas', filasSeleccionadas);

        // Cargar el archivo pyodide.py
        const response = await fetch('pyodide.py');
        const pythonCode = await response.text();
        
        // Ejecutar el código Python desde pyodide.py
        const result = await pyodide.runPythonAsync(pythonCode + `
data = leer_input_excel(data)
grupos = agrupar_datos(data, fecha, cod_suc, filas_seleccionadas, tasa_cambio)
xml_result = generar_xml(grupos)
xml_result
        `);
        
        document.getElementById('output').textContent = result;
        document.getElementById('result').style.display = 'block';
        
        const blob = new Blob([result], {type: 'application/xml'});
        const url = URL.createObjectURL(blob);
        document.getElementById('download-link').href = url;
    };
    
    reader.readAsArrayBuffer(fileInput);
});
