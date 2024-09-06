export const loadEnv = () => {
  return new Promise((resolve, reject) => {
    // primero ver si existe import.meta.env.VITE_APP_API_SERVER o localStorage
    const apiUrl = import.meta.env.VITE_APP_API_SERVER || localStorage.getItem("API_SERVER");

    if (apiUrl) {
      localStorage.setItem("API_SERVER", apiUrl);
      resolve({ API_SERVER: apiUrl });
    } else {
      // Si no está en localStorage, cargar el script para definirlo
      const script = document.createElement("script");
      script.src = "/env.js"; // Carga el archivo env.js desde el servidor
      script.onload = () => {
        const apiUrl = localStorage.getItem("API_SERVER");
        if (apiUrl) {
          resolve({ API_SERVER: apiUrl });
        } else {
          reject(new Error("No se pudo cargar API_SERVER desde localStorage"));
        }
      };
      script.onerror = () => reject(new Error("Error al cargar env.js"));
      document.head.appendChild(script);
    }
  });
};
