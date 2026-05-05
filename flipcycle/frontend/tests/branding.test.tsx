import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import HomePage from '@/app/page';

describe('FlipCycle branding', () => {
  it('renders the migrated FlipCycle homepage brand', () => {
    render(<HomePage />);
    expect(screen.getAllByText('FlipCycle').length).toBeGreaterThan(0);
    expect(screen.getByText(/Run your next profitable flip through FlipCycle/i)).toBeInTheDocument();
  });
});
