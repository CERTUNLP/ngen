import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryFeed } from "../../api/services/feeds";
import LetterFormat from "../../components/LetterFormat";


const FeedComponent = ({ feed }) => {


  // Fetch data using useQuery, including data transformation
  const { data, isLoading, error } = useQuery({
    queryKey: ['feedKey'], // Single query key to fetch all TLP data
    queryFn: getQueryFeed,

    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedTlp = data?.[feed];

  return (

        <div>
      <LetterFormat useBadge={true} stringToDisplay={selectedTlp.feed} bgcolor={"#03fca5"}/>
        </div>
  );
};  


export default FeedComponent;
