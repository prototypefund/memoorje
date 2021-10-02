module.exports = {
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#032B44',
        },
        accent: {
          DEFAULT: '#04D89D',
        },
      },
      inset: {
        unset: 'unset',
      },
      minHeight: {
        'screen-3/4': '75vh',
      },
      maxWidth: {
        '1/2': '50%',
        prose: '42ch',
        container: '960px',
        '720p': '1280px',
        '1080p': '1920px',
        screen: '100vw',
      },
      gridTemplateColumns: {
        cta: '1fr min-content',
      },
      textDecoration: ['group-focus'],
    },
  },
  variants: {
    extend: {
      display: ['group-focus-within'],
    },
  },
  plugins: [
    require('tailwindcss-typography'),
    require('tailwindcss-interaction-variants'),
  ],
}
