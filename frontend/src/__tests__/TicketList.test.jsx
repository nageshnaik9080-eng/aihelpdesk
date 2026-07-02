import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TicketList from '../components/TicketList';

function makeTicket(overrides = {}) {
  return {
    id: 1,
    employee_id: 1,
    title: 'VPN keeps disconnecting',
    description: 'It drops every few minutes',
    ocr_text: '',
    priority_score: 0,
    confidence: 0,
    status: 'open',
    created_at: new Date('2024-01-01T10:00:00Z').toISOString(),
    ...overrides,
  };
}

describe('TicketList', () => {
  it('renders the empty state when there are no tickets', () => {
    render(<TicketList tickets={[]} emptyText="Nothing here yet" />);
    expect(screen.getByText('Nothing here yet')).toBeInTheDocument();
  });

  it('renders a row per ticket and calls onSelect when clicked', async () => {
    const user = userEvent.setup();
    const onSelect = jest.fn();
    render(
      <TicketList
        tickets={[makeTicket({ id: 7, title: 'Printer offline' })]}
        onSelect={onSelect}
      />,
    );

    expect(screen.getByText('Printer offline')).toBeInTheDocument();
    await user.click(screen.getByText('Printer offline'));
    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect.mock.calls[0][0].id).toBe(7);
  });
});
