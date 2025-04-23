import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryUser } from "api/services/users";
import LetterFormat from "../../components/LetterFormat";


const UserComponent = ({ user }) => {


  // Fetch user data using useQuery.
  const { data, isLoading, error } = useQuery({
    queryKey: ['userKey'], // Single query key to fetch all TLP data
    queryFn: getQueryUser,

    staleTime: 5 * 60 * 1000, 
    refetchOnWindowFocus: false, // Disable refetching when window is focused
    refetchOnReconnect: false, // Disable refetching when the app reconnects

  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const selectedUser = data?.[user];
// User Table display??
  return (

        <div>
      <LetterFormat useBadge={true} stringToDisplay={selectedUser.username}  bgcolor={"#0f0"}/> 
        </div>
  );
};  


export default UserComponent;
