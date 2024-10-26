import { expect, test, describe, vi, it } from "vitest";
import ListEntity from "../../entity/ListEntity";
import { MemoryRouter } from 'react-router-dom';
import TableEntity from "../../entity/components/TableEntity";
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

  const entities= vi.fn();
  const loading= vi.fn();
  const currentPage= vi.fn();
  const setCurrentPage= vi.fn();
  const order= vi.fn();
  const setIsModify = vi.fn();
  const setOrder = vi.fn();
  const setLoading = vi.fn();
  
  describe('TableEntity Component', () => {
    // Test case 1: Should render
    it('should render', () => {
      render(
        <MemoryRouter>
            <TableEntity
            setIsModify={setIsModify}
            list={entities}
            loading={loading}
            setLoading={setLoading}
            currentPage={currentPage}
            order={order}
            setOrder={setOrder}
            /> 
        </MemoryRouter>
      );
      expect(TableEntity.toBeDefined) ; 
    });
  
   
  });
  

