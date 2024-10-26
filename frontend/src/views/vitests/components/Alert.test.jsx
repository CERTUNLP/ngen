import { expect, test, describe, vi } from "vitest";
import Alert from "../../../components/Alert/Alert";
import { render, screen } from '@testing-library/react'

vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));
  
describe("Alert", () => {
    test("Test Alert Component display on screen", () => {
        render( <Alert>

        </Alert>
        
        );
        expect(screen.Alert)

        })
  });

 

