import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryTaxonomy } from "../../api/services/taxonomies";
import LetterFormat from "../../components/LetterFormat";


const TaxonomyComponent = ({ taxonomy }) => {


  // Fetch taxonomy data using useQuery.
  const { data, isLoading, error } = useQuery({
    queryKey: ['taxonomyKey'], // Single query key to fetch all TLP data
    queryFn: getQueryTaxonomy,

    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedTaxonomy = data?.[taxonomy];
//revisar como se displayea taxonomy, si usa letterformat...
  return (

        <div>
      <LetterFormat useBadge={true} stringToDisplay={selectedTaxonomy.name}  bgcolor={"#0f0"}/> 
        </div>
  );
};  


export default TaxonomyComponent;
