import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryPriority } from "../../api/services/priorities";
import LetterFormat from "../../components/LetterFormat";


const PriorityComponent = ({ priority }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['priorityKey'],
    queryFn: getQueryPriority,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading || error) return null;

  const selectedPriority = data?.[priority];

  if (!priority || !selectedPriority) {
    console.warn(`PriorityComponent: Valor "${priority}" no encontrado.`);
    return <span />;
  }

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={selectedPriority.name}  
        bgcolor={"#0a0"}
      /> 
    </span>
  );
};


export default PriorityComponent;
