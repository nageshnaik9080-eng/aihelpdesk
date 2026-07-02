import { render, screen } from '@testing-library/react';
import StatusChip from '../components/StatusChip';

describe('StatusChip', () => {
  it('humanizes the status label', () => {
    render(<StatusChip status="in_progress" />);
    expect(screen.getByText('in progress')).toBeInTheDocument();
  });

  it('falls back to "unknown" when status is empty', () => {
    render(<StatusChip status="" />);
    expect(screen.getByText('unknown')).toBeInTheDocument();
  });
});
