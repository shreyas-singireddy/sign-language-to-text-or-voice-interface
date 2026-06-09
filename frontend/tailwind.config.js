export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#2563EB',
          600: '#1D4ED8'
        },
        accent: '#22C55E'
      },
      boxShadow: {
        glass: '0 20px 50px rgba(15, 23, 42, 0.12)'
      }
    }
  },
  plugins: []
};
