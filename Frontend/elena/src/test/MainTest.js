import { render, screen } from '@testing-library/react';
import MainComponent from '../Components/MainComponent'

test('renders the landing page', () => {
  render(<MainComponent />);
});

test('renders the landing page', () => {
    render(<MainComponent />);
    
    expect(screen.getByRole("heading")).toHaveTextContent(/Elena/);
    expect(screen.getByRole("combobox")).toHaveDisplayValue("Source");
    expect(screen.getByRole("combobox")).toHaveDisplayValue("Destination");
    expect(screen.getByRole("button", { name: "Let's Start" })).toBeDisabled();
    expect(screen.getByRole("img")).toBeInTheDocument();
  });
  