import { render, screen } from '@testing-library/react';
import StatsComponent from './Components/StatsComponent'

test('renders the landing page', () => {
  render(<StatsComponent stats={''}/>);
  });
  