import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryTlp } from "../../api/services/tlp";
import LetterFormat from "../../components/LetterFormat";


const TlpComponent = ({ tlp }) => {


  // Fetch data using useQuery, including data transformation
  const { data, isLoading, error } = useQuery({
    queryKey: ['tlpKey'], // Single query key to fetch all TLP data
    queryFn: getQueryTlp,

    staleTime: 5 * 60 * 1000, // Cache the data for 5 minutes
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedTlp = data?.[tlp];

  return (

        <div>
      <LetterFormat useBadge={true} stringToDisplay={selectedTlp.name} color={selectedTlp.color} bgcolor={"#000"}/>
        </div>
  );
};  


export default TlpComponent;
