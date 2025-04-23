import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryEvent } from "api/services/events";
import LetterFormat from "../../components/LetterFormat";


const EventComponent = ({ event }) => {


  // Fetch user data using useQuery.
  const { data, isLoading, error } = useQuery({
    queryKey: ['eventKey'], // Single query key to fetch all event data
    queryFn: getQueryEvent,

    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedEvent = data?.[event];

  return (

        <div>
<LetterFormat 
  useBadge={true} 
  stringToDisplay={
    `${selectedEvent?.domain || selectedEvent?.cidr || "No event available"} - ${selectedEvent?.initial_taxonomy_slug || ''}`
  } 
  bgcolor={"#0f0"} 
/>


           </div>
  );
};  


export default EventComponent;
