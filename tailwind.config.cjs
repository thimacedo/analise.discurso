/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,html}",
    "./*.{js,ts,jsx,tsx,html}", // Inclui arquivos na raiz, como index.html
    "./*.html", // Para garantir que index.html seja incluído se não for JS/TS
    "./public/**/*.html", // Se houver subdiretórios para HTML
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
