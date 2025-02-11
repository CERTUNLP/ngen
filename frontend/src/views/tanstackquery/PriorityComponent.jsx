import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryPriority } from "../../api/services/priorities";
import LetterFormat from "../../components/LetterFormat";


const PriorityComponent = ({ priority }) => {


  // Fetch Priority data using useQuery.
  const { data, isLoading, error } = useQuery({
    queryKey: ['priorityKey'], // Single query key to fetch all TLP data
    queryFn: getQueryPriority,

    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedPriority = data?.[priority];
//revisar como se displayea Priority, si usa letterformat...
  return (

        <div>
      <LetterFormat useBadge={true} stringToDisplay={selectedPriority.name}  bgcolor={"#0a0"}/> 
        </div>
  );
};  


export default PriorityComponent;
