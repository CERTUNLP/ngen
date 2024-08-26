// Polyfills para compatibilidad con IE11 y otros navegadores antiguos
import 'react-app-polyfill/ie11';
import 'react-app-polyfill/stable';

import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client'; // Nueva forma de renderizado con React 18+
import { Provider } from 'react-redux'; // Para integrar Redux
import { ConfigProvider } from './contexts/ConfigContext'; // Proveedor de configuración personalizada
import { PersistGate } from 'redux-persist/integration/react'; // Persistencia de estado con Redux Persist
import './index.scss'; // Estilos globales
import App from './App'; // Componente principal de la aplicación
import reportWebVitals from './reportWebVitals'; // Métricas de rendimiento
// import { persister, store } from './store'; // Store y persister de Redux
import store from './store'; // Store de Redux
import persist from './store/persist'; // Persister de Redux
import './i18n';

import setupInterceptors from './api/setupInterceptors'; // Configuración de interceptores para API

// Configuración del nuevo método de renderizado de React 18
const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <StrictMode>
    <Provider store={store}>
      {' '}
      {/* Redux Provider */}
      <ConfigProvider>
        {' '}
        {/* Config Provider */}
        <PersistGate loading={null} persistor={persist}>
          {' '}
          {/* Persistencia de Redux */}
          <App />
        </PersistGate>
      </ConfigProvider>
    </Provider>
  </StrictMode>
);

setupInterceptors(store); // Configuración de interceptores para solicitudes API

reportWebVitals(); // Iniciar el monitoreo de métricas de rendimiento
