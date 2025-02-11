export const loadEnv = () => {
  return new Promise((resolve, reject) => {
    // primero ver si existe import.meta.env.VITE_APP_API o localStorage
    let API_HOST = import.meta.env.VITE_APP_API_HOST || localStorage.getItem("API_HOST");
    let API_PORT = import.meta.env.VITE_APP_API_PORT || localStorage.getItem("API_PORT");
    let API_PATH = import.meta.env.VITE_APP_API_PATH || localStorage.getItem("API_PATH");
    let apiUrl = normalizeApiUrl(API_HOST, API_PORT, API_PATH);
    
    if (apiUrl) {
      localStorage.setItem("API_SERVER", apiUrl);
      resolve({ API_SERVER: apiUrl });
    } else {
      // Si no está en localStorage, cargar el script para definirlo
      const script = document.createElement("script");
      script.src = "/env.js"; // Carga el archivo env.js desde el servidor
      script.onload = () => {
        let apiUrlRetrieved = normalizeApiUrl(localStorage.getItem("API_HOST"), localStorage.getItem("API_PORT"), localStorage.getItem("API_PATH"));
        if (apiUrlRetrieved) {
          resolve({ API_SERVER: apiUrlRetrieved });
        } else {
          reject(new Error("No se pudo cargar API desde localStorage"));
        }
      };
      script.onerror = () => reject(new Error("Error al cargar env.js"));
      document.head.appendChild(script);
    }
  });
};

const normalizeApiUrl = (host, port, path) => {
  let portValue = port || window.location.port;
  return `${window.location.protocol}//${host || window.location.hostname}${portValue ? ":" + portValue : ""}${path || "/api/"}`;
};
