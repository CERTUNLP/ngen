// Polyfills para compatibilidad con IE11 y otros navegadores antiguos
import "react-app-polyfill/ie11";
import "react-app-polyfill/stable";

import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client"; // Nueva forma de renderizado con React 18+
import { Provider } from "react-redux"; // Para integrar Redux
import { ConfigProvider } from "./contexts/ConfigContext"; // Proveedor de configuración personalizada
import { PersistGate } from "redux-persist/integration/react"; // Persistencia de estado con Redux Persist
import "./index.scss"; // Estilos globales
import App from "./App"; // Componente principal de la aplicación
import reportWebVitals from "./reportWebVitals"; // Métricas de rendimiento
import store from "./store"; // Store de Redux
import persist from "./store/persist"; // Persister de Redux
import setupInterceptors from "./api/setupInterceptors"; // Configuración de interceptores para API

import { loadEnv } from "./api/services/loadEnv"; // Carga del entorno
import initializeI18n from "./i18n"; // Cargar la configuración de i18n después de loadEnv

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css"; // Importar estilos

import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from '@tanstack/react-query'

// Configuración del nuevo método de renderizado de React 18
const container = document.getElementById("root");
const root = createRoot(container);

const queryClient = new QueryClient();

const initializeApp = async () => {
  try {
    // Cargar variables de entorno
    await loadEnv();

    // Inicializar i18n
    await initializeI18n();

    // Renderizar la aplicación
    root.render(
      <StrictMode>
          <QueryClientProvider client={queryClient}>
        <Provider store={store}>
          <ConfigProvider>
            <PersistGate loading={null} persistor={persist}>
              <App />
              <ToastContainer />
            </PersistGate>
          </ConfigProvider>
        </Provider>
        </QueryClientProvider>
      </StrictMode>
    );
  } catch (error) {
    console.error("Error inicializando la aplicación:", error);
  }
};

// Iniciar la aplicación
initializeApp();

// Configurar interceptores de Axios
setupInterceptors(store);

// Iniciar el monitoreo de métricas de rendimiento
reportWebVitals();
