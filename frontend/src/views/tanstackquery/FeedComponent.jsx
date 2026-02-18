import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryFeed } from "../../api/services/feeds";
import LetterFormat from "../../components/LetterFormat";


const FeedComponent = ({ feed }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['feedKey'],
    queryFn: getQueryFeed,
    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading) return null; // O un spinner pequeño si prefieres
  if (error) return null;

  const element = data?.[feed];

  // Validación de existencia
  if (!feed || !element) {
    console.warn(`FeedComponent: El valor "${feed}" no se encontró en la data.`);
    return <span />; 
  }

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={element.name} 
        bgcolor={"#03fca5"}
      />
    </span>
  );
};


export default FeedComponent;
