import { expect, test, describe, vi, it } from "vitest";
import ListUser from "../../user/ListUser";
import { MemoryRouter } from 'react-router-dom';
import TableUsers from "../../user/components/TableUsers";
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

  
  const mockEntityNames = {
    '1': 'Entity 1',
  };
  
  // Mock functions
  vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

  const users= vi.fn();
  const loading= vi.fn();
  const order= vi.fn();
  const setOrder = vi.fn();
  const setLoading = vi.fn();
  const currentPage = vi.fn();  
  describe('TableUser Component', () => {
    // Test User 1: Should render
    it('should render', () => {
      render(
        <MemoryRouter>
        <ListUser>
            <TableUsers 
                users={users} 
                loading={loading} 
                order={order} 
                setOrder={setOrder} 
                setLoading={setLoading} 
                currentPage={currentPage} />
 </ListUser>  

        </MemoryRouter>
      );
      expect(TableUsers.toBeDefined) ; 
    });
  
   
  });
  