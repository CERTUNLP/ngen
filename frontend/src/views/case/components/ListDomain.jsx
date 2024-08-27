import React, { useEffect, useState } from "react";
import { getEvent } from "../../../api/services/events";

const ListDomain = ({ events }) => {
  const [eventDomains, setEventDomains] = useState([]);

  useEffect(() => {
    async function fetchAndSetEvents(events) {
      try {
        const responses = await Promise.all(
          events.map((event) =>
            getEvent(event).then((response) => {
              return response.data;
            })
          )
        );
        const ListDomain = responses.map((response) => response.domain);
        setEventDomains(ListDomain);
      } catch (error) {
        console.error("Error fetching events:", error);
      }
    }

    // Llamada a la función
    fetchAndSetEvents(events);
  }, [events]);
  return (
    <div>
      {eventDomains.map((domain) => {
        return <li>{domain}</li>;
      })}
    </div>
  );
};

export default ListDomain;
