import axios from "axios";

// Crear instancia de Axios sin definir la baseURL por adelantado
const apiInstance = axios.create({
  withCredentials: true
});

// Usar un interceptor para establecer dinámicamente el valor de `baseURL`
apiInstance.interceptors.request.use(
  (config) => {
    const apiUrl = localStorage.getItem("API_SERVER") || "http://localhost:3003/api/";
    config.baseURL = apiUrl;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiInstance;
