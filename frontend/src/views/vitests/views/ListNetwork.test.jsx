import { expect, test, describe, vi, it } from "vitest";
import ListNetwork from "../../network/ListNetwork";
import { MemoryRouter } from 'react-router-dom';
import TableNetwork from "../../network/components/TableNetwork";
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


  const setIsModify = vi.fn();
  const setOrder = vi.fn();
  const setLoading = vi.fn();
  
  describe('TableNetwork Component', () => {
    // Test case 1: Should render
    it('should render', () => {
      render(
        <MemoryRouter>
          <TableNetwork
            setIsModify={setIsModify}
            list={[]}
            loading={true}
            order=""
            setOrder={setOrder}
            setLoading={setLoading}
            currentPage={1}
            entityNames={mockEntityNames}
          />
        </MemoryRouter>
      );
      expect(TableNetwork.toBeDefined) ; //
    });
  
   
  });
  