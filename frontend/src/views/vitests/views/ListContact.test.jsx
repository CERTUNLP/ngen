import { expect, test, describe, vi, it } from "vitest";
import ListContact from "../../contact/ListContact";
import { MemoryRouter } from 'react-router-dom';
import TableContact from "../../contact/components/TableContact";
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
  const contacts = vi.fn();
  const list = vi.fn();
  const currentPage = vi.fn();  
  const setIsModify = vi.fn();
  const order = vi.fn();
  const setOrder = vi.fn();
  const loading = vi.fn();
  const setLoading = vi.fn();
  
  describe('TableContact Component', () => {
    // Test case 1: Should render
    it('should render', () => {
      render(
        <MemoryRouter>
              <TableContact
                setIsModify={setIsModify}
                list={contacts}
                loading={loading}
                currentPage={currentPage}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
              />
        </MemoryRouter>
      );
      expect(TableContact.toBeDefined); 
    });
  
   
  });
  