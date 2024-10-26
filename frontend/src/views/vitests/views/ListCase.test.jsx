import { expect, test, describe, vi, it } from "vitest";
import ListCase from "../../case/ListCase";
import { MemoryRouter } from 'react-router-dom';
import TableCase from "../../case/components/TableCase";
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

  const cases= vi.fn();
  const loading= vi.fn();
  const selectedCases= vi.fn();
  const setSelectedCases= vi.fn();
  const order= vi.fn();
  const setIfModify= vi.fn();
  const priorityNames= vi.fn();
  const stateNames= vi.fn();
  const tlpNames= vi.fn();
  const userNames= vi.fn();  
  const setIsModify = vi.fn();
  const setOrder = vi.fn();
  const setLoading = vi.fn();
  
  describe('TableCase Component', () => {
    // Test case 1: Should render
    it('should render', () => {
      render(
        <MemoryRouter>
          <TableCase
              cases={cases}
              loading={loading}
              selectedCases={selectedCases}
              setSelectedCases={setSelectedCases}
              order={order}
              setOrder={setOrder}
              setIfModify={setIfModify}
              setLoading={setLoading}
              priorityNames={priorityNames}
              stateNames={stateNames}
              tlpNames={tlpNames}
              userNames={userNames}
              editColum={true}
              deleteColum={true}
              navigationRow={true}
              buttonReturn={false}
              disableNubersOfEvents={true}
              disableDateModified={false}
          />
        </MemoryRouter>
      );
      expect(TableCase.toBeDefined) ; 
    });
  
   
  });
  