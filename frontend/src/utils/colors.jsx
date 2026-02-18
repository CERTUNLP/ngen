function hexToRgb(hex) {
  hex = hex.replace("#", "");
  if (hex.length === 3) {
    hex = hex
      .split("")
      .map((char) => char + char)
      .join("");
  }
  let r = parseInt(hex.substring(0, 2), 16);
  let g = parseInt(hex.substring(2, 4), 16);
  let b = parseInt(hex.substring(4, 6), 16);
  return { r, g, b };
}

function getTextColorBasedOnBackground(hexColor) {
  const { r, g, b } = hexToRgb(hexColor);
  const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
  return brightness < 128 ? "#FFFFFF" : "#000000";
}

// Genera un color HSL basado en el hash de la cadena de texto
const getColor = (str) => {
  const getHash = (str) => {
    let hash = 0;
    const s = String(str);
    for (let i = 0; i < s.length; i++) {
      // El operador bitwise << ayuda a generar una dispersión mayor
      hash = s.charCodeAt(i) + ((hash << 5) - hash);
    }
    return Math.abs(hash);
  };

  const hash = getHash(str);
  
  // 1. Matiz (Hue): 0 a 360 grados para cubrir todo el espectro
  const h = hash % 360; 
  
  // 2. Saturación: Un valor fijo (70-80%) para que los colores sean vivos pero no chillones
  const s = 75; 
  
  // 3. Luminosidad (Lightness): Entre 75% y 85% para mantener tonos pastel legibles
  const l = 75 + (hash % 10); 

  return `hsl(${h}, ${s}%, ${l}%)`;
};

export { getTextColorBasedOnBackground, getColor };
