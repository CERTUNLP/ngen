import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryState } from "../../api/services/states";
import LetterFormat from "../../components/LetterFormat";


const StateComponent = ({ state }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['stateKey'],
    queryFn: getQueryState,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading || error) return null;

  const selectedState = data?.[state];

  if (!state || !selectedState) {
    console.warn(`StateComponent: Estado "${state}" no encontrado.`);
    return <span />;
  }

  const getColor = () => {
    const { attended, solved, url, id } = selectedState;

    // Usamos el ID o la URL para generar el hash
    const getHash = (str) => {
      let hash = 0;
      const s = String(str);
      for (let i = 0; i < s.length; i++) {
        hash = s.charCodeAt(i) + ((hash << 5) - hash);
      }
      return Math.abs(hash);
    };

    const hash = getHash(url || id || state);
    
    // Aumentamos el rango de variación a 60 grados (el doble que antes)
    // y variamos la luminosidad entre 75% y 90% para dar más contraste
    const hVar = (hash % 60) - 30; 
    const lVar = (hash % 15); // Variación de hasta 15% en el brillo

    if (!attended && !solved) {
      // Rango de Rojos/Naranjas (Base 0°) -> de -30° (Rosa) a +30° (Naranja)
      return `hsl(${0 + hVar}, 85%, ${80 + lVar}%)`; 
    } else if (attended && !solved) {
      // Rango de Amarillos/Ámbar (Base 50°) -> de 20° (Dorado) a 80° (Lima)
      return `hsl(${55 + hVar}, 85%, ${75 + lVar}%)`; 
    } else if (solved) {
      // Rango de Verdes (Base 120°) -> de 90° (Verde Lima) a 150° (Verde Esmeralda)
      return `hsl(${125 + hVar}, 80%, ${80 + lVar}%)`; 
    }
    
    return "#34deeb"; 
  };

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={selectedState.name}  
        bgcolor={getColor()}
        color="#000" // Importante: Texto oscuro para legibilidad en fondos claros
      /> 
    </span>
  );
};


export default StateComponent;