import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryTaxonomy } from "../../api/services/taxonomies";
import LetterFormat from "../../components/LetterFormat";


const TaxonomyComponent = ({ taxonomy }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['taxonomyKey'],
    queryFn: getQueryTaxonomy,
    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading) return null;
  if (error) return null;

  const selectedTaxonomy = data?.[taxonomy];

  // Validación de existencia
  if (!taxonomy || !selectedTaxonomy) {
    console.warn(`TaxonomyComponent: El valor "${taxonomy}" no se encontró en la data.`);
    return <span />;
  }

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true}
        stringToDisplay={selectedTaxonomy.name} 
        bgcolor="#0f0" 
      />
    </span>
  );
}; 


export default TaxonomyComponent;
