import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getMinifiedTlp } from "../../api/services/tlp";

const TlpComponent = ({ tlp }) => {
  // Fetch data using useQuery, including data transformation
  const { data, isLoading, error } = useQuery({
    queryKey: ['tlpKey'], // Single query key to fetch all TLP data
    queryFn: async () => {
      const response = await getMinifiedTlp();
      
      // Transform the response into a dictionary
      let dicTlp = {};
      response.forEach((tlp) => {
        dicTlp[tlp.url] = { name: tlp.name, color: tlp.color };
      });

      // Return the transformed dictionary (this will be cached)
      return dicTlp;
    },
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedTlp = data?.[tlp];

  return (
    <div>
      {selectedTlp ? (
        <div>
          <h3 style={{ color: selectedTlp.color }}>{selectedTlp.name}</h3>
        </div>
      ) : (
        <div>No TLP data available.</div>
      )}
    </div>
  );
};


export default TlpComponent;
