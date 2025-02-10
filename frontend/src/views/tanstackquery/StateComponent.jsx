import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryState } from "../../api/services/states";
import LetterFormat from "../../components/LetterFormat";


const StateComponent = ({ state }) => {


  // Fetch State data using useQuery.
  const { data, isLoading, error } = useQuery({
    queryKey: ['stateKey'], // Single query key to fetch all TLP data
    queryFn: getQueryState,

    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedState = data?.[state];
//revisar como se displayea State, si usa letterformat...
  return (

        <div>
      <LetterFormat useBadge={true} stringToDisplay={selectedState.name}  bgcolor={"#34deeb"}/> 
        </div>
  );
};  


export default StateComponent;