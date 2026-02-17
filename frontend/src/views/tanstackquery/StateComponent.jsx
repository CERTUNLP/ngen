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

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={selectedState.name}  
        bgcolor={"#34deeb"}
      /> 
    </span>
  );
};


export default StateComponent;