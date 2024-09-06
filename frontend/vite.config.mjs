import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import jsconfigPaths from "vite-jsconfig-paths";

export default defineConfig(({ mode }) => {
  // Cargar variables de entorno específicas según el modo
  const env = loadEnv(mode, process.cwd());
  //   process.env = { ...process.env, ...loadEnv(mode, process.cwd()) };

  //   console.log(process.env);
  console.log(env);

  // Definir URL base y puerto
  const API_SERVER = env.VITE_APP_BASE_NAME ? `${env.VITE_APP_BASE_NAME}` : "/";
  const PORT = env.VITE_PORT || 3000;

  return {
    // Configuraciones específicas del servidor de desarrollo
    server: {
      open: false, // Abre el navegador automáticamente en desarrollo
      host: "0.0.0.0", // Permite acceder desde la red local
      port: PORT, // Puerto configurado en las variables de entorno o 3000
      strictPort: true, // Falla si el puerto ya está en uso
      sourcemap: true // Genera sourcemaps para debugging en desarrollo
    },
    // Configuraciones para el build de producción
    build: {
      sourcemap: true, // No generar sourcemaps en producción
      outDir: "dist", // Directorio de salida para la build
      rollupOptions: {
        // Configuraciones de optimización específicas
        output: {
          // Personalizar cómo se nombran los chunks
          chunkFileNames: "assets/js/[name]-[hash].js",
          entryFileNames: "assets/js/[name]-[hash].js",
          assetFileNames: "assets/[ext]/[name]-[hash].[ext]"
        }
      }
    },
    // Configuraciones para el comando `vite preview`
    preview: {
      open: false, // Abre el navegador automáticamente en preview
      host: "0.0.0.0",
      port: PORT,
      strictPort: true
    },
    // Definir variables globales o condiciones de construcción
    define: {
      global: "window"
      //   __APP_ENV__: JSON.stringify(env.APP_ENV),
      //   "process.env.NODE_ENV": JSON.stringify(mode),
      //   "process.env.VITE_APP_API_SERVER": JSON.stringify(env.VITE_APP_API_SERVER),
      //   TEST123: JSON.stringify(env.VITE_APP_API_SERVER)
    },
    // Resolución de módulos y alias
    resolve: {
      alias: {
        "@": "/src", // Puedes ajustar los alias según tu estructura
        assets: "/src/assets"
      }
    },
    // Configuraciones de CSS
    css: {
      preprocessorOptions: {
        // scss: {
        //   charset: false,
        //   additionalData: `@import "@src/scss/styles/_variables.scss";` // Importar variables globales SCSS
        // },
        less: {
          charset: false,
          javascriptEnabled: true
        }
      },
      charset: false,
      postcss: {
        plugins: [
          {
            postcssPlugin: "internal:charset-removal",
            AtRule: {
              charset: (atRule) => {
                if (atRule.name === "charset") {
                  atRule.remove();
                }
              }
            }
          }
        ]
      }
    },
    // URL base de la aplicación
    base: API_SERVER,
    // Plugins de Vite
    plugins: [
      react(), // Soporte para React
      jsconfigPaths() // Resolver paths según jsconfig.json o tsconfig.json
    ],
    // Configuración de dependencias optimizadas
    optimizeDeps: {
      exclude: [] // Excluir paquetes específicos del pre-bundling
    }
  };
});
