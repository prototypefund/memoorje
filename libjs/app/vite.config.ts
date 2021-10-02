import path from 'path'

import { defineConfig } from 'vite'
import Vue from '@vitejs/plugin-vue'
import VueI18n from '@intlify/vite-plugin-vue-i18n'
import Components from 'unplugin-vue-components/vite'
import { HeadlessUiResolver } from 'unplugin-vue-components/resolvers'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Pages from 'vite-plugin-pages'
import { VitePWA } from 'vite-plugin-pwa'
import svgLoader from 'vite-svg-loader'

export default defineConfig({
  build: {
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  resolve: {
    alias: {
      '~/': `${path.resolve(__dirname, 'src')}/`,
    },
  },
  plugins: [
    Vue({
      include: [/\.vue$/, /\.md$/],
      refTransform: true,
    }),
    VitePWA({
      minify: false,
      mode: 'development',
    }),
    VueI18n({
      include: path.resolve(__dirname, 'src', 'locales', '**'),
      defaultSFCLang: 'yaml',
    }),
    Pages({
      extensions: ['vue'],
    }),
    svgLoader({
      svgoConfig: {
        multipass: true,
      },
    }),
    Components({
      resolvers: [
        HeadlessUiResolver(),
        IconsResolver({
          prefix: 'icon',
          alias: {
            sui: 'system-uicons',
          },
        }),
      ],
    }),
    Icons({
      compiler: 'vue3',
    }),
  ],
  ssgOptions: {
    script: 'async',
    formatting: 'prettify',
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
