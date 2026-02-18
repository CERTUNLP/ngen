import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getEvent } from "api/services/events";
import LetterFormat from "../../components/LetterFormat";

const EventComponent = ({ event }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['eventKey', event],
    queryFn: () => getEvent(event).then((res) => res.data),
    enabled: !!event, // Seguridad: no dispara la petición si event es null/undefined
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading || error) return null;

  // Si la API respondió pero la data está vacía
  if (!data) {
    console.warn(`EventComponent: No se pudo recuperar data para el evento: ${event}`);
    return <span />;
  }

  const displayText = `${data.domain || data.cidr || 'N/A'} - ${data.initial_taxonomy_slug || ''}`;

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={displayText}
        bgcolor={"#0f0"} 
      />
    </span>
  );
};

export default EventComponent;
