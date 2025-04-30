import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getEvent } from "api/services/events";
import LetterFormat from "../../components/LetterFormat";

const EventComponent = ({ event }) => {
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['eventKey', event], // Every event is identified by its url 
    queryFn: () => getEvent(event).then((res) => res.data), // getEvent receives an URL and retrieves an event
    enabled: !!event, // Only runs if event is valid
    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedEvent = data;
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
