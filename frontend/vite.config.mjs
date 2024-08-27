import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import jsconfigPaths from 'vite-jsconfig-paths';
// import path from 'path';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const API_URL = `/${env.VITE_APP_BASE_NAME}`;
    const PORT = `${'3000'}`;

    return {
        server: {
            // this ensures that the browser opens upon server start
            open: false,
            // this sets a default port to 3000
            port: PORT,
            host: true,
            sourcemap: false,
        },
        define: {
            global: 'window',
        },
        resolve: {
            alias: [
                // { find: '', replacement: path.resolve(__dirname, 'src') },
                // {
                //   find: /^~(.+)/,
                //   replacement: path.join(process.cwd(), 'node_modules/$1')
                // },
                // {
                //   find: /^src(.+)/,
                //   replacement: path.join(process.cwd(), 'src/$1')
                // },
                // {
                //   find: 'assets',
                //   replacement: path.join(process.cwd(), 'src/assets')
                // },
            ],
        },
        css: {
            preprocessorOptions: {
                scss: {
                    charset: false,
                },
                less: {
                    charset: false,
                },
            },
            charset: false,
            postcss: {
                plugins: [
                    {
                        postcssPlugin: 'internal:charset-removal',
                        AtRule: {
                            charset: (atRule) => {
                                if (atRule.name === 'charset') {
                                    atRule.remove();
                                }
                            },
                        },
                    },
                ],
            },
        },
        base: API_URL,
        plugins: [react(), jsconfigPaths()],
        build: {
            sourcemap: false,
        },
        optimizeDeps: {
            exclude: [
                // '@nivo/pie'
                // 'recharts'
                // 'react-nvd3',
                // 'i18next'
            ],
        },
    };
});
