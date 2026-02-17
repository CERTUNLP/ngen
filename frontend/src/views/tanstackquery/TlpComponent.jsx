import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryTlp } from "../../api/services/tlp";
import LetterFormat from "../../components/LetterFormat";


const TlpComponent = ({ tlp }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['tlpKey'],
    queryFn: getQueryTlp,
    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  // 1. Buscamos el objeto
  const selectedTlp = data?.[tlp];

  // 2. Validación: Si tlp no es válido o no existe en data
  if (!tlp || !selectedTlp) {
    // Solo logueamos en consola si tlp venía pero no se encontró, 
    // o si venía vacío para que sepas por qué no se renderiza nada.
    console.warn(`TlpComponent: El valor de tlp "${tlp}" no es válido o no se encontró en la data.`);
    return <div />; // Devuelve un div vacío como pediste
  }

  // 3. Si llegamos aquí, selectedTlp existe y es seguro acceder a sus propiedades
  return (
    <div>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={selectedTlp.name} 
        color={selectedTlp.color} 
        bgcolor={"#000"}
      />
    </div>
  );
};


export default TlpComponent;
