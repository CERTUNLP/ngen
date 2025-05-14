import apiInstance from "../api";
import { COMPONENT_URL } from "config/constant";
import setAlert from "utils/setAlert";

const getVersion = async () => {
  try {
    const response = await apiInstance.get(COMPONENT_URL.version);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.detail || "No se pudo recuperar la información de la aplicación";
    setAlert(message, "error");
    console.error("Error al obtener la versión:", error);
    throw error;
  }
};

export { getVersion };
