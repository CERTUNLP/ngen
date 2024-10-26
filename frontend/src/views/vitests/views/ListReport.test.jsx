import { expect, test, describe, vi } from "vitest";
import ListReport from "../../report/ListReport"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';
import TableReport from "views/report/components/TableReport";

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

  const reports= vi.fn();
  const loading= vi.fn();
  const taxonomyNames = vi.fn();
  const order= vi.fn();
  const setOrder= vi.fn();
  const setLoading= vi.fn();

describe("ListReport", () => {
    test("Test ListReport correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListReport>
        <TableReport 
        list={reports}
        loading={loading}
        taxonomyNames={taxonomyNames}
        order={order}
        setOrder={setOrder}
        setLoading={setLoading}> </TableReport>
        </ListReport>
        </MemoryRouter>
        );
        expect(ListReport).toBeDefined();

        })
  });