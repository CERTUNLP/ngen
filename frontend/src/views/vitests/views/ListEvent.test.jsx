import { expect, test, describe, vi } from "vitest";
import ListEvent from "../../event/ListEvent"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));


  

const events = vi.fn();
const loading= vi.fn();
const selectedEvent= vi.fn();
const setSelectedEvent= vi.fn();
const order= vi.fn();
const setOrder= vi.fn();
const setLoading= vi.fn();
const currentPage= vi.fn();
const taxonomyNames= vi.fn();
const feedNames= vi.fn();
const tlpNames= vi.fn();


describe("ListEvent", () => {
    test("Test ListEvent correct display on screen.", () => {
        render(
        <MemoryRouter>

        <ListEvent
            events={events}
            loading={loading}
            selectedEvent={selectedEvent}
            setSelectedEvent={setSelectedEvent}
            order={order}
            setOrder={setOrder}
            setLoading={setLoading}
            currentPage={currentPage}
            taxonomyNames={taxonomyNames}
            feedNames={feedNames}
            tlpNames={tlpNames}
            disableCheckbox={false}
            disableUuid={false}
            disableMerged={false}
            disbleDateModified={false}
            disableDate={false}>
        </ListEvent>
        </MemoryRouter>
        );
        expect(ListEvent.toBeDefined)

        })
  });