import React from "react";
import { useQuery } from '@tanstack/react-query';
import { getQueryUser } from "api/services/users";
import LetterFormat from "../../components/LetterFormat";


const UserComponent = ({ user }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['userKey'],
    queryFn: getQueryUser,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (isLoading || error) return null;

  const selectedUser = data?.[user];

  if (!user || !selectedUser) {
    console.warn(`UserComponent: Usuario "${user}" no encontrado.`);
    return <span />;
  }

  return (
    <span style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <LetterFormat 
        useBadge={true} 
        stringToDisplay={selectedUser.username || selectedUser.first_name || "Unknown"}  
        bgcolor={"#0f0"}
      /> 
    </span>
  );
};


export default UserComponent;
